from fastapi import APIRouter

from app.api.deps import CurrentUserDep
from app.schemas.analysis import InsightCard
from app.services import insights_service

router = APIRouter(tags=["insights"])


@router.get("/insights", response_model=list[InsightCard])
async def get_insights(month: str, user: CurrentUserDep) -> list[InsightCard]:
    return insights_service.get_insights(user.user_id, month)
