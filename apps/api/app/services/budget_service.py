from fastapi import HTTPException, status

from app.core.timeutils import month_bounds, prev_month, today_kst
from app.repositories import budget_repo, category_repo, tx_repo
from app.schemas.budget import BudgetItem, BudgetOut, BudgetSuggestion

_SUGGEST_MONTHS = 3

# Cold-start template (no history yet): allocate income by 통계청 가계동향 ratios.
# consumable budget = take-home income x average propensity to consume (~0.70).
_CONSUME_RATIO = 0.70
# Ratios of the consumable budget, keyed by default category NAME — VARIABLE
# (discretionary) categories only. Fixed costs (주거/통신) and 카드대금 are left
# OUT on purpose: their amount varies wildly per person (월세 vs 전세/자가) and the
# user knows their exact number, so guessing them with an average ratio is worse
# than leaving them blank to fill in. (See research/cold-start-budget.md.)
_TEMPLATE_RATIOS = {
    "식비": 0.24,
    "카페/간식": 0.06,
    "생활/마트": 0.05,
    "교통": 0.12,
    "문화/여가": 0.08,
    "건강/의료": 0.08,
    "쇼핑": 0.10,
    "기타지출": 0.05,
}
_ROUND_TO = 1000  # round drafts to a tidy ₩1,000


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


def template_budgets(user_id: str, income_minor: int) -> list[BudgetSuggestion]:
    """Cold-start draft: split (income x consume ratio) across categories by template.

    For brand-new users with no history (suggest_budgets returns nothing). Maps by
    category NAME, so only the default categories get a draft; custom categories and
    카드대금 (ratio 0) are skipped.
    """
    consumable = income_minor * _CONSUME_RATIO
    suggestions = []
    for c in category_repo.list_categories(user_id):
        ratio = _TEMPLATE_RATIOS.get(c["name"])
        if not ratio:
            continue
        amount = round(consumable * ratio / _ROUND_TO) * _ROUND_TO
        if amount <= 0:
            continue
        suggestions.append(
            BudgetSuggestion(category_id=c["id"], name=c["name"], suggested_minor=amount)
        )
    suggestions.sort(key=lambda s: s.suggested_minor, reverse=True)
    return suggestions


def _last_complete_months(count: int) -> list[str]:
    """The `count` complete months before the current one (most recent first)."""
    today = today_kst()
    current = f"{today.year:04d}-{today.month:02d}"
    return [prev_month(current, back) for back in range(1, count + 1)]
