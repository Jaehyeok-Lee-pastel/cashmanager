from fastapi import HTTPException, status

from app.core.timeutils import month_bounds, today_kst
from app.repositories import budget_repo, category_repo, tx_repo
from app.schemas.budget import BudgetItem, BudgetOut, BudgetSuggestion

_SUGGEST_MONTHS = 3


def list_budgets(user_id: str) -> list[BudgetOut]:
    return [BudgetOut(**row) for row in budget_repo.list_budgets(user_id)]


def upsert_budgets(user_id: str, items: list[BudgetItem]) -> list[BudgetOut]:
    owned = {c["id"] for c in category_repo.list_categories(user_id)}
    for item in items:
        if item.category_id not in owned:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="존재하지 않거나 권한이 없는 카테고리입니다.",
            )
    for item in items:
        budget_repo.upsert_budget(user_id, item.category_id, item.limit_minor)
    return list_budgets(user_id)


def delete_budget(user_id: str, category_id: str) -> None:
    budget_repo.delete_budget(user_id, category_id)


def suggest_budgets(user_id: str) -> list[BudgetSuggestion]:
    """Average monthly expense per category over the last 3 complete months."""
    categories = category_repo.list_categories(user_id)
    totals: dict[str, int] = {}
    months_with_activity = 0

    for month in _last_complete_months(_SUGGEST_MONTHS):
        start, end = month_bounds(month)
        rows = tx_repo.list_for_summary(user_id, start, end)
        had_activity = False
        for r in rows:
            if r["direction"] != "expense" or not r.get("category_id"):
                continue
            totals[r["category_id"]] = totals.get(r["category_id"], 0) + r["amount_minor"]
            had_activity = True
        if had_activity:
            months_with_activity += 1

    divisor = max(1, months_with_activity)
    names = {c["id"]: c["name"] for c in categories}
    suggestions = [
        BudgetSuggestion(
            category_id=cid,
            name=names.get(cid, "미분류"),
            suggested_minor=round(total / divisor),
        )
        for cid, total in totals.items()
        if cid in names  # only current (non-archived) categories
    ]
    suggestions.sort(key=lambda s: s.suggested_minor, reverse=True)
    return suggestions


def _last_complete_months(count: int) -> list[str]:
    today = today_kst()
    year, mon = today.year, today.month
    months: list[str] = []
    for _ in range(count):
        mon -= 1
        if mon == 0:
            mon = 12
            year -= 1
        months.append(f"{year:04d}-{mon:02d}")
    return months
