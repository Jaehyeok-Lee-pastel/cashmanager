from fastapi import APIRouter

from app.api.deps import CurrentUserDep, MonthDep
from app.schemas.summary import MonthlySummaryOut
from app.services import profile_service, summary_service

router = APIRouter(tags=["summary"])


# sync def: the service does blocking supabase-py I/O, so FastAPI runs it in a
# threadpool instead of blocking the event loop (matches transactions.py).
@router.get("/summary", response_model=MonthlySummaryOut)
def get_summary(month: MonthDep, user: CurrentUserDep) -> MonthlySummaryOut:
    anchor = profile_service.get_pay_anchor_day(user.user_id)
    return summary_service.get_monthly_summary(user.user_id, month, anchor)
