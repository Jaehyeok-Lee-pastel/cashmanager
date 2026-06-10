"""Recurring (fixed) expense/income rules + monthly materialization."""
import calendar
from datetime import date

from fastapi import HTTPException, status

from app.core.timeutils import month_bounds, today_kst
from app.repositories import category_repo, recurring_repo, tx_repo
from app.schemas.recurring import RecurringCreate, RecurringOut, RecurringUpdate
from app.schemas.transaction import TransactionCreate
from app.services import tx_service


def _verify_category(user_id: str, category_id: str | None) -> None:
    if category_id is None:
        return
    if category_repo.get_category(user_id, category_id) is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="존재하지 않거나 권한이 없는 카테고리입니다.",
        )


def list_rules(user_id: str) -> list[RecurringOut]:
    return [RecurringOut(**row) for row in recurring_repo.list_rules(user_id)]


def create_rule(user_id: str, payload: RecurringCreate) -> RecurringOut:
    _verify_category(user_id, payload.category_id)
    row = recurring_repo.create_rule(user_id, payload.model_dump())
    if row is None:
        raise HTTPException(status_code=500, detail="반복 규칙 저장에 실패했습니다.")
    return RecurringOut(**row)


def update_rule(user_id: str, rule_id: str, payload: RecurringUpdate) -> RecurringOut:
    if recurring_repo.get_rule(user_id, rule_id) is None:
        raise HTTPException(status_code=404, detail="반복 규칙을 찾을 수 없습니다.")
    fields = payload.model_dump(exclude_unset=True)
    if "category_id" in fields:
        _verify_category(user_id, fields["category_id"])
    row = recurring_repo.update_rule(user_id, rule_id, fields)
    if row is None:
        raise HTTPException(status_code=404, detail="반복 규칙을 찾을 수 없습니다.")
    return RecurringOut(**row)


def delete_rule(user_id: str, rule_id: str) -> None:
    if recurring_repo.get_rule(user_id, rule_id) is None:
        raise HTTPException(status_code=404, detail="반복 규칙을 찾을 수 없습니다.")
    recurring_repo.delete_rule(user_id, rule_id)


def materialize_month(user_id: str, month: str) -> int:
    """Create transactions for active rules due on/before today this month (or all
    days for a past month), skipping rules already recorded this month. day 29-31
    clamps to the month's length. Returns the number created."""
    today = today_kst()
    year, mon = (int(p) for p in month.split("-", 1))
    total_days = calendar.monthrange(year, mon)[1]
    is_current = (today.year, today.month) == (year, mon)
    if (year, mon) > (today.year, today.month):
        return 0  # don't pre-create a future month
    cutoff = today.day if is_current else total_days
    start, end = month_bounds(month)
    done = tx_repo.recurring_ids_in_month(user_id, start, end)

    created = 0
    for rule in recurring_repo.list_rules(user_id):
        if not rule["active"] or rule["id"] in done:
            continue
        day = min(rule["day_of_month"], total_days)
        if day > cutoff:
            continue  # not due yet this month
        tx_service.create_transaction(user_id, TransactionCreate(
            amount_minor=rule["amount_minor"],
            direction=rule["direction"],
            category_id=rule["category_id"],
            memo=rule["memo"],
            occurred_on=date(year, mon, day),
            source="manual",
            parse_meta={"recurring_id": rule["id"], "route": "recurring"},
        ))
        created += 1
    return created


def _occurrences_in_window(day_of_month: int, start: date, end: date) -> list[date]:
    """All dates in [start, end) when a monthly rule on `day_of_month` fires. A cycle
    window spans two calendar months and, when payday clamps (29~31), can be >1 month
    long — so the SAME day can fire twice (e.g. 28th in [2/28, 3/31))."""
    occs = []
    for year, mon in ((start.year, start.month), (end.year, end.month)):
        occ = date(year, mon, min(day_of_month, calendar.monthrange(year, mon)[1]))
        if start <= occ < end:
            occs.append(occ)
    return occs


def upcoming_fixed_minor(user_id: str, start_iso: str, end_iso: str, today: date) -> int:
    """Sum of active EXPENSE rules that fire LATER in this window (after today) —
    discounts Safe-to-Spend so '오늘 쓸 수 있는 돈' accounts for rent yet to come.
    Works for both calendar-month and pay-cycle windows. 0 if the table is absent."""
    start = date.fromisoformat(start_iso)
    end = date.fromisoformat(end_iso)
    try:
        rules = recurring_repo.list_rules(user_id)
    except Exception:  # noqa: BLE001 — summary must work before the migration
        return 0
    total = 0
    for r in rules:
        if not r["active"] or r["direction"] != "expense":
            continue
        for occ in _occurrences_in_window(r["day_of_month"], start, end):
            if occ > today:
                total += r["amount_minor"]
    return total
