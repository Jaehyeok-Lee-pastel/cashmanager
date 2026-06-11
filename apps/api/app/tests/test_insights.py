import pytest

from app.schemas.summary import CategorySummary, MonthlySummaryOut
from app.services import insights_service


def _summary(month, total_expense, cats):
    return MonthlySummaryOut(
        month=month,
        total_expense=total_expense,
        total_income=0,
        count=len(cats),
        by_category=cats,
    )


def _cat(name, sum_minor, limit=None):
    return CategorySummary(
        category_id=name, name=name, emoji=None,
        sum_minor=sum_minor, ratio=0.5, limit_minor=limit,
    )


@pytest.fixture(autouse=True)
def _no_coach(monkeypatch):
    # keep tests deterministic: coaching LLM call skipped, calendar-month mode
    monkeypatch.setattr(
        "app.services.openai_service.complete",
        lambda *a, **k: (_ for _ in ()).throw(RuntimeError("no llm")),
    )
    monkeypatch.setattr("app.services.profile_service.get_pay_anchor_day", lambda uid: None)


def test_budget_thresholds(monkeypatch):
    cur = _summary("2026-06", 250000, [
        _cat("식비", 100000, 100000),   # >= limit -> alert
        _cat("카페", 80000, 100000),    # 0.8 -> warn
        _cat("교통", 70000, 100000),    # 0.7 -> none
    ])
    prev = _summary("2026-05", 0, [])

    def fake(uid, month, anchor=None):
        return cur if month == "2026-06" else prev

    monkeypatch.setattr("app.services.summary_service.get_monthly_summary", fake)
    cards = insights_service.get_insights("u1", "2026-06")
    budget = [c for c in cards if c.type == "budget"]
    assert {c.severity for c in budget} == {"alert", "warn"}
    assert any("식비 예산 초과" in c.title for c in budget)
    assert any("카페 예산 임박" in c.title for c in budget)
    # 교통(0.7) produces no budget card
    assert not any("교통" in c.title for c in budget)
    # no trend card when previous month had no spending
    assert not any(c.type == "trend" for c in cards)
    # top category present
    assert any(c.type == "top" for c in cards)


def test_mom_trend(monkeypatch):
    cur = _summary("2026-06", 120000, [_cat("식비", 120000)])
    prev = _summary("2026-05", 100000, [_cat("식비", 100000)])
    monkeypatch.setattr(
        "app.services.summary_service.get_monthly_summary",
        lambda uid, m, a=None: cur if m == "2026-06" else prev,
    )
    cards = insights_service.get_insights("u1", "2026-06")
    trend = next(c for c in cards if c.type == "trend")
    assert "20%" in trend.title  # (120000-100000)/100000 = +20%
