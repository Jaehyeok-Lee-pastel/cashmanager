from fastapi import HTTPException, status

from app.core.timeutils import month_bounds, prev_month, today_kst
from app.repositories import budget_repo, category_repo, tx_repo
from app.schemas.budget import BudgetItem, BudgetOut, BudgetSuggestion

_SUGGEST_MONTHS = 3

# Cold-start template (no history yet): allocate income by 통계청 가계동향 ratios.
# consumable budget = take-home income x average propensity to consume (~0.70).
_CONSUME_RATIO = 0.70
_FIXED_TOTAL = 0.78  # variable categories' combined share of the consumable budget

# (comfortable, tight) ratio anchors per VARIABLE category. Direction follows KOSIS
# 가계동향 5분위(여유)↔1분위(빠듯) + Engel's law: as the budget tightens (user invests
# more), necessities (식비·생활/마트·건강/의료) take a bigger share and discretionary
# (문화/여가·쇼핑·카페) shrink first. The midpoint equals the old flat ratio, so
# tightness=0.5 reproduces the previous behavior (regression-safe). Fixed costs
# (주거/통신)·카드대금 stay OUT — too person-specific. See research/cold-start-budget.md.
_ANCHORS = {
    "식비": (0.20, 0.28),
    "카페/간식": (0.08, 0.04),
    "생활/마트": (0.04, 0.06),
    "교통": (0.13, 0.11),
    "문화/여가": (0.11, 0.05),
    "건강/의료": (0.06, 0.10),
    "쇼핑": (0.13, 0.07),
    "기타지출": (0.05, 0.05),
}
_ROUND_TO = 1000  # round drafts to a tidy ₩1,000


def _ratios(tightness: float) -> dict[str, float]:
    """Variable-category ratios for a budget tightness (0=여유 … 1=빠듯), renormalized
    so the variable share always sums to _FIXED_TOTAL."""
    raw = {n: c + (t - c) * tightness for n, (c, t) in _ANCHORS.items()}
    scale = _FIXED_TOTAL / sum(raw.values())
    return {n: r * scale for n, r in raw.items()}


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


def template_budgets(
    user_id: str, income_minor: int, invest_minor: int = 0
) -> list[BudgetSuggestion]:
    """Cold-start draft: 소비예산 = 소득 − 투자(저축), split across variable categories
    with Engel-law tightness: the more you invest, the bigger the necessity share.

    invest_minor (월 투자/저축) is subtracted so investors don't over-budget. When not
    given, a default 30% savings is assumed (consumable = income x 0.70, the old
    behavior). Maps by category NAME; fixed (주거/통신)·카드대금 stay out.
    """
    invest = invest_minor if invest_minor > 0 else round(income_minor * (1 - _CONSUME_RATIO))
    consumable = max(0, income_minor - invest)
    # tightness from investment share: 10%↓ = 여유(0), 50%↑ = 빠듯(1). The default
    # 30% maps to 0.5 (= the old flat ratios), so non-investors see no change.
    investment_ratio = (invest / income_minor) if income_minor else (1 - _CONSUME_RATIO)
    tightness = min(1.0, max(0.0, (investment_ratio - 0.10) / 0.40))
    ratios = _ratios(tightness)
    suggestions = []
    for c in category_repo.list_categories(user_id):
        # the 투자 category holds the monthly investment target the user entered
        if c["name"] == "투자":
            if invest_minor > 0:
                suggestions.append(
                    BudgetSuggestion(category_id=c["id"], name="투자", suggested_minor=invest_minor)
                )
            continue
        ratio = ratios.get(c["name"])
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
