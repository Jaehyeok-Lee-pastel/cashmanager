"""Per-user rate limiting for LLM-backed endpoints (single-instance MVP).

Guards OpenAI cost / abuse: a per-minute burst cap AND a per-day total cap.
In-memory (resets on restart); for multi-instance move to Redis/Supabase.
NOTE: also set a hard monthly usage limit in the OpenAI dashboard — that is the
ultimate cost backstop independent of this code.
"""

import time
from collections import defaultdict, deque
from typing import Callable

from fastapi import HTTPException, status

from app.api.deps import CurrentUserDep

_DAY = 86400
_MINUTE = 60


def rate_limiter(per_minute: int, per_day: int) -> Callable[..., None]:
    """Build a FastAPI dependency enforcing per-minute + per-day caps per user."""
    hits: dict[str, deque[float]] = defaultdict(deque)

    def dependency(user: CurrentUserDep) -> None:
        now = time.monotonic()
        dq = hits[user.user_id]
        while dq and now - dq[0] > _DAY:  # drop entries older than a day
            dq.popleft()
        minute_count = sum(1 for t in dq if now - t <= _MINUTE)
        if minute_count >= per_minute:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="요청이 너무 많습니다. 잠시 후 다시 시도해주세요.",
            )
        if len(dq) >= per_day:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="오늘 사용량 한도를 초과했습니다. 잠시 후 다시 시도해주세요.",
            )
        dq.append(now)

    return dependency


# per-endpoint limiters (assistant costs ~2x tokens -> stricter)
rate_limit_parse = rate_limiter(per_minute=20, per_day=300)
rate_limit_assistant = rate_limiter(per_minute=10, per_day=100)
rate_limit_insights = rate_limiter(per_minute=10, per_day=200)
