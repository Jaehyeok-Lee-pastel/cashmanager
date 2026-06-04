from fastapi import APIRouter, Depends

from app.api.deps import CurrentUserDep, MonthDep
from app.core.ratelimit import rate_limit_insights
from app.schemas.analysis import InsightCard
from app.services import insights_service

router = APIRouter(tags=["insights"])


@router.get("/insights", response_model=list[InsightCard], dependencies=[Depends(rate_limit_insights)])
async def get_insights(month: MonthDep, user: CurrentUserDep) -> list[InsightCard]:
    return insights_service.get_insights(user.user_id, month)
