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
