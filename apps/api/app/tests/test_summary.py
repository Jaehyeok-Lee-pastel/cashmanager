from app.core.timeutils import month_progress, today_kst
from app.services.summary_service import _safe_to_spend


def _current_month() -> str:
    today = today_kst()
    return f"{today.year:04d}-{today.month:02d}"


def test_safe_to_spend_none_without_budget():
    assert _safe_to_spend("2026-06", 50000, {}, 10, 30) == (None, None)


def test_safe_to_spend_none_for_non_current_month():
    # an obviously-past month is never the current month
    assert _safe_to_spend("2000-01", 50000, {"c": 100000}, 31, 31) == (None, None)


def test_safe_to_spend_current_month_math():
    month = _current_month()
    elapsed, total = month_progress(month)
    safe, daily = _safe_to_spend(month, 30000, {"c": 100000}, elapsed, total)
    days_left = total - elapsed + 1
    assert safe == 70000
    assert daily == round(70000 / days_left)


def test_safe_to_spend_negative_when_over_budget():
    month = _current_month()
    elapsed, total = month_progress(month)
    safe, _ = _safe_to_spend(month, 150000, {"c": 100000}, elapsed, total)
    assert safe == -50000
