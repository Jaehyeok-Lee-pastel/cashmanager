from fastapi import APIRouter, status

from app.api.deps import CurrentUserDep
from app.schemas.budget import BudgetOut, BudgetSuggestion, BudgetUpsert
from app.services import budget_service

router = APIRouter(prefix="/budgets", tags=["budgets"])


# sync def throughout: services do blocking supabase-py I/O, so FastAPI offloads
# them to a threadpool rather than blocking the event loop.
@router.get("", response_model=list[BudgetOut])
def list_budgets(user: CurrentUserDep) -> list[BudgetOut]:
    return budget_service.list_budgets(user.user_id)


@router.put("", response_model=list[BudgetOut])
def upsert_budgets(payload: BudgetUpsert, user: CurrentUserDep) -> list[BudgetOut]:
    """Upserts only the sent items (not a full replace). Removal uses DELETE."""
    return budget_service.upsert_budgets(user.user_id, payload.budgets)


@router.get("/suggestions", response_model=list[BudgetSuggestion])
def suggest_budgets(user: CurrentUserDep) -> list[BudgetSuggestion]:
    return budget_service.suggest_budgets(user.user_id)


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_budget(category_id: str, user: CurrentUserDep) -> None:
    budget_service.delete_budget(user.user_id, category_id)
