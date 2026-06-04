from app.core.timeutils import month_bounds
from app.repositories import budget_repo, category_repo, tx_repo
from app.schemas.summary import CategorySummary, MonthlySummaryOut

_UNCATEGORIZED = "미분류"


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
        )
        for cid, amount in per_category.items()
    ]
    by_category.sort(key=lambda c: c.sum_minor, reverse=True)

    return MonthlySummaryOut(
        month=month,
        total_expense=total_expense,
        total_income=total_income,
        count=len(rows),
        by_category=by_category,
    )


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
