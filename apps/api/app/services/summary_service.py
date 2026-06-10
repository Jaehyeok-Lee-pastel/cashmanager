from app.core.timeutils import month_bounds, month_progress, today_kst
from app.repositories import budget_repo, category_repo, tx_repo
from app.schemas.summary import CategorySummary, MonthlySummaryOut
from app.services import recurring_service

_UNCATEGORIZED = "미분류"

# Don't project before this many days have elapsed: early in the month a few
# entries extrapolate into wild numbers (linear pace is noisiest at the start).
_MIN_ELAPSED_DAYS = 7


def get_monthly_summary(user_id: str, month: str) -> MonthlySummaryOut:
    start, end = month_bounds(month)
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

    # Month-end pace projection (only for an in-progress month past the noise window).
    elapsed, total_days = month_progress(month)
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

    upcoming_fixed = recurring_service.upcoming_fixed_minor(user_id, month, elapsed, total_days)
    # money moved into investments this month is gone from spendable cash (unlike a
    # card payment, it has NO matching expense entry) -> discount Safe-to-Spend too.
    invest_out = sum(r["amount_minor"] for r in rows if _is_investment_row(r, names))
    invest_target = next(
        (limits[cid] for cid, (nm, _e) in names.items() if nm == "투자" and cid in limits),
        None,
    )
    safe, daily = _safe_to_spend(
        month, total_expense, limits, elapsed, total_days, upcoming_fixed, invest_out
    )

    return MonthlySummaryOut(
        month=month,
        total_expense=total_expense,
        total_income=total_income,
        count=len(rows),
        by_category=by_category,
        projected_expense=project(total_expense),
        budget_total=(sum(limits.values()) or None),
        safe_to_spend=safe,
        daily_allowance=daily,
        upcoming_fixed_minor=(upcoming_fixed or None),
        invested_minor=(invest_out or None),
        investment_target_minor=invest_target,
    )


def _is_investment_row(row: dict, names: dict[str, tuple[str, str | None]]) -> bool:
    """A transfer that is an investment (route tag from NL, or category '투자')."""
    if row.get("direction") != "transfer":
        return False
    if (row.get("parse_meta") or {}).get("route") == "investment":
        return True
    return names.get(row.get("category_id"), ("", None))[0] == "투자"


def _safe_to_spend(
    month: str, total_expense: int, limits: dict[str, int], elapsed: int,
    total_days: int, upcoming_fixed: int = 0, invest_out: int = 0,
) -> tuple[int | None, int | None]:
    """(remaining budget, today's per-day allowance) for the CURRENT month only.

    daily = (total budget - spent) / days left including today. Returns (None, None)
    when no budget is set or the month isn't the current one. `remaining` may be
    negative (already over the total budget) — the UI shows that case differently.
    """
    budget_total = sum(limits.values())
    today = today_kst()
    year, mon = (int(p) for p in month.split("-", 1))
    is_current = (today.year, today.month) == (year, mon)
    if not budget_total or not is_current:
        return None, None
    # discount fixed costs still coming (rent/subscriptions) AND money already moved
    # into investments this month, so "오늘 쓸 수 있는 돈" isn't optimistic.
    remaining = budget_total - total_expense - upcoming_fixed - invest_out
    days_left = total_days - elapsed + 1  # include today
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
