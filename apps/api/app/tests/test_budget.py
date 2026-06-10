import pytest
from fastapi import HTTPException

from app.schemas.budget import BudgetItem
from app.services import budget_service


def test_upsert_rejects_unowned_category(monkeypatch):
    monkeypatch.setattr(
        "app.repositories.category_repo.list_categories",
        lambda uid: [{"id": "cat-mine", "name": "식비"}],
    )
    with pytest.raises(HTTPException) as exc:
        budget_service.upsert_budgets(
            "user-1", [BudgetItem(category_id="cat-other", limit_minor=300000)]
        )
    assert exc.value.status_code == 400


def test_upsert_passes_user_and_calls_repo(monkeypatch):
    monkeypatch.setattr(
        "app.repositories.category_repo.list_categories",
        lambda uid: [{"id": "cat-1", "name": "식비"}],
    )
    captured = []
    monkeypatch.setattr(
        "app.repositories.budget_repo.upsert_budget",
        lambda uid, cid, lim: captured.append((uid, cid, lim)),
    )
    monkeypatch.setattr(
        "app.repositories.budget_repo.list_budgets",
        lambda uid: [{"category_id": "cat-1", "limit_minor": 300000}],
    )
    out = budget_service.upsert_budgets(
        "user-7", [BudgetItem(category_id="cat-1", limit_minor=300000)]
    )
    assert captured == [("user-7", "cat-1", 300000)]
    assert out[0].limit_minor == 300000


def test_suggest_averages_last_3_months(monkeypatch):
    monkeypatch.setattr(
        "app.repositories.category_repo.list_categories",
        lambda uid: [{"id": "c-food", "name": "식비"}],
    )
    # food expense in 2 of the 3 months -> avg divides by months WITH activity (2).
    per_month = {
        "2026-05": [{"amount_minor": 100000, "direction": "expense", "category_id": "c-food"}],
        "2026-04": [{"amount_minor": 200000, "direction": "expense", "category_id": "c-food"}],
        "2026-03": [],
    }

    def fake_summary(uid, start, end):
        return per_month.get(start[:7], [])

    monkeypatch.setattr("app.repositories.tx_repo.list_for_summary", fake_summary)
    monkeypatch.setattr(
        "app.services.budget_service._last_complete_months",
        lambda n: ["2026-05", "2026-04", "2026-03"],
    )
    out = budget_service.suggest_budgets("user-1")
    assert len(out) == 1
    # (100000 + 200000) / 2 months-with-activity = 150000
    assert out[0].suggested_minor == 150000
    assert out[0].category_id == "c-food"


def test_template_budgets_allocates_by_ratio(monkeypatch):
    monkeypatch.setattr(
        "app.repositories.category_repo.list_categories",
        lambda uid: [
            {"id": "c-food", "name": "식비"},
            {"id": "c-rent", "name": "주거"},  # fixed cost -> left blank
            {"id": "c-card", "name": "카드대금"},  # transfer -> excluded
            {"id": "c-custom", "name": "내맘대로"},  # not in template -> excluded
        ],
    )
    out = budget_service.template_budgets("u", 3_000_000)
    # consumable = 3,000,000 * 0.70 = 2,100,000; 식비 24% = 504,000
    food = next(s for s in out if s.category_id == "c-food")
    assert food.suggested_minor == 504000
    ids = {s.category_id for s in out}
    # 주거(fixed)·카드대금(transfer)·custom are NOT templated
    assert ids == {"c-food"}


def test_template_budgets_subtracts_investment(monkeypatch):
    monkeypatch.setattr(
        "app.repositories.category_repo.list_categories",
        lambda uid: [{"id": "c-food", "name": "식비"}, {"id": "c-etc", "name": "기타지출"}],
    )
    # more investment -> smaller consumable -> smaller overall draft
    low = sum(s.suggested_minor for s in budget_service.template_budgets("u", 3_000_000, 200_000))
    high = sum(s.suggested_minor for s in budget_service.template_budgets("u", 3_000_000, 1_500_000))
    assert high < low


def test_template_ratios_shift_with_tightness():
    tight = budget_service._ratios(1.0)
    comfy = budget_service._ratios(0.0)
    # necessities rise, discretionary falls as the budget tightens (Engel's law)
    assert tight["식비"] > comfy["식비"]
    assert tight["건강/의료"] > comfy["건강/의료"]
    assert tight["문화/여가"] < comfy["문화/여가"]
    assert tight["쇼핑"] < comfy["쇼핑"]
    # variable share preserved at all tightness levels
    assert abs(sum(tight.values()) - 0.78) < 1e-9
    assert abs(sum(comfy.values()) - 0.78) < 1e-9
    # midpoint regression: tightness 0.5 == the old flat ratios
    mid = budget_service._ratios(0.5)
    assert abs(mid["식비"] - 0.24) < 1e-6
    assert abs(mid["문화/여가"] - 0.08) < 1e-6


def test_template_budgets_fills_investment_category(monkeypatch):
    monkeypatch.setattr(
        "app.repositories.category_repo.list_categories",
        lambda uid: [{"id": "c-food", "name": "식비"}, {"id": "c-inv", "name": "투자"}],
    )
    out = budget_service.template_budgets("u", 3_000_000, 800_000)
    # the 투자 category gets the entered investment amount as its monthly target
    assert next(s for s in out if s.category_id == "c-inv").suggested_minor == 800000


def test_suggest_ignores_income_and_uncategorized(monkeypatch):
    monkeypatch.setattr(
        "app.repositories.category_repo.list_categories",
        lambda uid: [{"id": "c-food", "name": "식비"}],
    )
    rows = [
        {"amount_minor": 50000, "direction": "income", "category_id": "c-food"},
        {"amount_minor": 30000, "direction": "expense", "category_id": None},
        {"amount_minor": 90000, "direction": "expense", "category_id": "c-food"},
    ]
    monkeypatch.setattr(
        "app.repositories.tx_repo.list_for_summary", lambda uid, s, e: rows if s[:7] == "2026-05" else []
    )
    monkeypatch.setattr(
        "app.services.budget_service._last_complete_months", lambda n: ["2026-05"]
    )
    out = budget_service.suggest_budgets("user-1")
    assert out[0].suggested_minor == 90000  # only the categorized expense counts
