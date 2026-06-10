from app.core.timeutils import month_progress, today_kst
from app.services.summary_service import _is_investment_row, _safe_to_spend


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


def test_safe_to_spend_subtracts_investment():
    month = _current_month()
    elapsed, total = month_progress(month)
    # budget 1,000,000 - spent 30,000 - fixed 0 - invest 200,000 = 770,000
    safe, _ = _safe_to_spend(month, 30000, {"c": 1000000}, elapsed, total, 0, 200000)
    assert safe == 770000


def test_is_investment_row():
    names = {"c-inv": ("투자", None), "c-card": ("카드대금", None)}
    assert _is_investment_row({"direction": "transfer", "category_id": "c-inv"}, names)
    assert _is_investment_row(
        {"direction": "transfer", "category_id": None, "parse_meta": {"route": "investment"}}, names
    )
    # a card-payment transfer is NOT an investment (its purchases are already expenses)
    assert not _is_investment_row({"direction": "transfer", "category_id": "c-card"}, names)
    assert not _is_investment_row({"direction": "expense", "category_id": "c-inv"}, names)
