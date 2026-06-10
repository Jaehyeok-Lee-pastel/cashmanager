from fastapi import APIRouter, status

from app.api.deps import CurrentUserDep, MonthDep
from app.schemas.recurring import (
    MaterializeResult,
    RecurringCreate,
    RecurringOut,
    RecurringUpdate,
)
from app.services import recurring_service

router = APIRouter(prefix="/recurring", tags=["recurring"])


# sync def: blocking supabase-py runs in a threadpool.
@router.get("", response_model=list[RecurringOut])
def list_rules(user: CurrentUserDep) -> list[RecurringOut]:
    return recurring_service.list_rules(user.user_id)


@router.post("", response_model=RecurringOut, status_code=status.HTTP_201_CREATED)
def create_rule(payload: RecurringCreate, user: CurrentUserDep) -> RecurringOut:
    return recurring_service.create_rule(user.user_id, payload)


@router.patch("/{rule_id}", response_model=RecurringOut)
def update_rule(rule_id: str, payload: RecurringUpdate, user: CurrentUserDep) -> RecurringOut:
    return recurring_service.update_rule(user.user_id, rule_id, payload)


@router.delete("/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_rule(rule_id: str, user: CurrentUserDep) -> None:
    recurring_service.delete_rule(user.user_id, rule_id)


@router.post("/materialize", response_model=MaterializeResult)
def materialize(month: MonthDep, user: CurrentUserDep) -> MaterializeResult:
    """Create this month's due fixed expenses/incomes (idempotent)."""
    return MaterializeResult(created=recurring_service.materialize_month(user.user_id, month))
