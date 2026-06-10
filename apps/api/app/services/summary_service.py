from datetime import date, timedelta

from app.core.timeutils import (
    cycle_bounds,
    cycle_progress,
    month_bounds,
    month_progress,
    today_kst,
)
from app.repositories import budget_repo, category_repo, tx_repo
from app.schemas.summary import CategorySummary, MonthlySummaryOut
from app.services import recurring_service

_UNCATEGORIZED = "미분류"

# Don't project before this many days have elapsed: early in the month a few
# entries extrapolate into wild numbers (linear pace is noisiest at the start).
_MIN_ELAPSED_DAYS = 7


def get_monthly_summary(
    user_id: str, month: str, pay_anchor_day: int | None = None
) -> MonthlySummaryOut:
    today = today_kst()
    cal_year, cal_mon = (int(p) for p in month.split("-", 1))
    is_current_cal = (today.year, today.month) == (cal_year, cal_mon)
    # Pay-cycle window only for the CURRENT month (past months keep calendar labels).
    use_cycle = pay_anchor_day is not None and is_current_cal
    if use_cycle:
        start, end = cycle_bounds(today, pay_anchor_day)
        elapsed, total_days = cycle_progress(today, pay_anchor_day)
        is_current = True
    else:
        start, end = month_bounds(month)
        elapsed, total_days = month_progress(month, today)
        is_current = is_current_cal

    rows = tx_repo.list_for_summary(user_id, start, end)

    total_expense = sum(r["amount_minor"] for r in rows if r["direction"] == "expense")
    total_income = sum(r["amount_minor"] for r in rows if r["direction"] == "income")

    # Sum expenses per category_id.
    per_category: dict[str | None, int] = {}
    for r in rows:
        if r["direction"] != "expense":
            continue
        cid = r.get("category_id")
        per_category[cid] = per_category.get(cid, 0) + r["amount_minor"]

    # Pace projection to the window end (only in-progress, past the noise window).
    in_progress = _MIN_ELAPSED_DAYS <= elapsed < total_days

    def project(amount: int) -> int | None:
        # Linear extrapolation: a one-off large purchase can inflate this, so the
        # UI wording stays estimative ("이 속도면").
        return round(amount * total_days / elapsed) if in_progress else None

    names = _category_names(user_id)
    limits = _category_limits(user_id)
    by_category = [
        CategorySummary(
            category_id=cid,
            name=names.get(cid, (_UNCATEGORIZED, None))[0],
            emoji=names.get(cid, (_UNCATEGORIZED, None))[1],
            sum_minor=amount,
            ratio=(amount / total_expense) if total_expense else 0.0,
            limit_minor=limits.get(cid),
            projected_minor=project(amount),
        )
        for cid, amount in per_category.items()
    ]
    by_category.sort(key=lambda c: c.sum_minor, reverse=True)

    upcoming_fixed = (
        recurring_service.upcoming_fixed_minor(user_id, start, end, today)
        if is_current
        else 0
    )
    # money moved into investments this window is gone from spendable cash (unlike a
    # card payment, it has NO matching expense entry) -> discount Safe-to-Spend too.
    invest_out = sum(r["amount_minor"] for r in rows if _is_investment_row(r, names))
    invest_target = next(
        (limits[cid] for cid, (nm, _e) in names.items() if nm == "투자" and cid in limits),
        None,
    )
    budget_total = sum(limits.values())
    days_left = total_days - elapsed + 1  # == days to next payday in cycle mode
    safe, daily = _safe_to_spend(
        budget_total, total_expense, upcoming_fixed, invest_out, days_left, is_current
    )

    # cycle display fields (None in calendar mode); cycle_end is the INCLUSIVE last day.
    cycle_end_incl = (
        (date.fromisoformat(end) - timedelta(days=1)).isoformat() if use_cycle else None
    )

    return MonthlySummaryOut(
        month=month,
        total_expense=total_expense,
        total_income=total_income,
        count=len(rows),
        by_category=by_category,
        projected_expense=project(total_expense),
        budget_total=(budget_total or None),
        safe_to_spend=safe,
        daily_allowance=daily,
        upcoming_fixed_minor=(upcoming_fixed or None),
        invested_minor=(invest_out or None),
        investment_target_minor=invest_target,
        cycle_start=start if use_cycle else None,
        cycle_end=cycle_end_incl,
        days_to_payday=days_left if use_cycle else None,
    )


def _is_investment_row(row: dict, names: dict[str, tuple[str, str | None]]) -> bool:
    """A transfer that is an investment (route tag from NL, or category '투자')."""
    if row.get("direction") != "transfer":
        return False
    if (row.get("parse_meta") or {}).get("route") == "investment":
        return True
    return names.get(row.get("category_id"), ("", None))[0] == "투자"


def _safe_to_spend(
    budget_total: int, total_expense: int, upcoming_fixed: int, invest_out: int,
    days_left: int, is_current: bool,
) -> tuple[int | None, int | None]:
    """(remaining budget, today's per-day allowance) for the current window only.

    daily = (budget - spent - upcoming fixed - invested) / days left. In cycle mode
    days_left counts down to the next payday. Returns (None, None) when no budget is
    set or the window isn't current. `remaining` may be negative (already over budget).
    """
    if not budget_total or not is_current:
        return None, None
    remaining = budget_total - total_expense - upcoming_fixed - invest_out
    daily = round(remaining / days_left) if days_left > 0 else None
    return remaining, daily


def _category_names(user_id: str) -> dict[str, tuple[str, str | None]]:
    """Map category_id -> (name, emoji) for the user's categories."""
    rows = category_repo.list_categories(user_id)
    return {row["id"]: (row["name"], row.get("emoji")) for row in rows}


def _category_limits(user_id: str) -> dict[str, int]:
    """Map category_id -> budget limit. Resilient if the budgets table is absent."""
    try:
        return {b["category_id"]: b["limit_minor"] for b in budget_repo.list_budgets(user_id)}
    except Exception:  # noqa: BLE001 — summary must work even before the budgets migration
        return {}
