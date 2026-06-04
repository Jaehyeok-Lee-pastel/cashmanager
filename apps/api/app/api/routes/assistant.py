from fastapi import APIRouter, Depends
from fastapi.concurrency import run_in_threadpool

from app.api.deps import CurrentUserDep
from app.core.ratelimit import rate_limit_assistant
from app.schemas.analysis import AssistantAnswer, AssistantQuery
from app.services import assistant_service

router = APIRouter(prefix="/assistant", tags=["assistant"])


@router.post("/query", response_model=AssistantAnswer, dependencies=[Depends(rate_limit_assistant)])
async def query(payload: AssistantQuery, user: CurrentUserDep) -> AssistantAnswer:
    """Answer a question over the user's own spending summary (offloaded LLM call)."""
    return await run_in_threadpool(
        assistant_service.answer_query, user.user_id, payload.question
    )
