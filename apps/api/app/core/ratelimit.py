"""Lightweight in-memory per-user rate limiter (single-instance MVP).

Guards the LLM-backed parse endpoint from runaway cost / abuse. For a
multi-instance deployment this should move to a shared store (Redis / Supabase),
but for the MVP an in-process sliding window is enough.
"""

import time
from collections import defaultdict, deque

from fastapi import HTTPException, status

from app.api.deps import CurrentUserDep

_WINDOW_SECONDS = 60
_MAX_PER_WINDOW = 20

_hits: dict[str, deque[float]] = defaultdict(deque)


def _check(user_id: str) -> None:
    now = time.monotonic()
    window = _hits[user_id]
    while window and now - window[0] > _WINDOW_SECONDS:
        window.popleft()
    if len(window) >= _MAX_PER_WINDOW:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="요청이 너무 많습니다. 잠시 후 다시 시도해주세요.",
        )
    window.append(now)


def rate_limit_parse(user: CurrentUserDep) -> None:
    """FastAPI dependency: throttle the NL parse endpoint per user."""
    _check(user.user_id)
