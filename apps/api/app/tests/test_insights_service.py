"""Insights must follow the same pay-cycle window as the summary screen (the
consistency gap the audit flagged), and compare against the previous CYCLE."""
from app.schemas.summary import MonthlySummaryOut
from app.services import insights_service


def _cycle_summary(expense: int) -> MonthlySummaryOut:
    return MonthlySummaryOut(
        month="2026-06", total_expense=expense, total_income=0, count=1,
        by_category=[], cycle_start="2026-06-10", cycle_end="2026-07-09",
    )


def test_insights_trend_uses_prev_cycle_in_cycle_mode(monkeypatch):
    monkeypatch.setattr("app.services.profile_service.get_pay_anchor_day", lambda uid: 10)
    monkeypatch.setattr(
        "app.services.summary_service.get_monthly_summary",
        lambda uid, m, a=None: _cycle_summary(100000),
    )
    # previous cycle spent 80,000 -> +25%
    monkeypatch.setattr(
        "app.services.summary_service.cycle_total_expense", lambda uid, anchor, ref: 80000
    )

    cards = insights_service.get_insights("u", "2026-06")
    trend = next(c for c in cards if c.type == "trend")
    assert "지난 급여달" in trend.title  # cycle label, not "지난달"
    assert "25" in trend.title


def test_insights_trend_uses_calendar_when_no_anchor(monkeypatch):
    monkeypatch.setattr("app.services.profile_service.get_pay_anchor_day", lambda uid: None)
    cur = MonthlySummaryOut(month="2026-06", total_expense=100000, total_income=0, count=1, by_category=[])
    prev = MonthlySummaryOut(month="2026-05", total_expense=50000, total_income=0, count=1, by_category=[])
    calls = iter([cur, prev])
    monkeypatch.setattr(
        "app.services.summary_service.get_monthly_summary", lambda uid, m, a=None: next(calls)
    )

    cards = insights_service.get_insights("u", "2026-06")
    trend = next(c for c in cards if c.type == "trend")
    assert "지난달" in trend.title and "급여달" not in trend.title
