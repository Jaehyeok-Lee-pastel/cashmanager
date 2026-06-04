from fastapi import APIRouter, Depends, status
from fastapi.concurrency import run_in_threadpool

from app.api.deps import CurrentUserDep
from app.core.ratelimit import rate_limit_parse
from app.schemas.nl import ParseRequest, ParseResult
from app.schemas.transaction import (
    TransactionCreate,
    TransactionOut,
    TransactionUpdate,
)
from app.services import nl_service, tx_service

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.post("/parse", response_model=ParseResult, dependencies=[Depends(rate_limit_parse)])
async def parse_line(payload: ParseRequest, user: CurrentUserDep) -> ParseResult:
    """Preview only — does NOT persist. The client confirms via POST /transactions.

    Offloaded to a thread so the blocking OpenAI call never stalls the event loop.
    """
    return await run_in_threadpool(nl_service.parse, user.user_id, payload.text)


@router.get("", response_model=list[TransactionOut])
async def list_transactions(
    month: str, user: CurrentUserDep, category_id: str | None = None
) -> list[TransactionOut]:
    return tx_service.list_transactions(user.user_id, month, category_id)


@router.post("", response_model=TransactionOut, status_code=status.HTTP_201_CREATED)
async def create_transaction(
    payload: TransactionCreate, user: CurrentUserDep
) -> TransactionOut:
    return tx_service.create_transaction(user.user_id, payload)


@router.patch("/{tx_id}", response_model=TransactionOut)
async def update_transaction(
    tx_id: str, payload: TransactionUpdate, user: CurrentUserDep
) -> TransactionOut:
    return tx_service.update_transaction(user.user_id, tx_id, payload)


@router.delete("/{tx_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transaction(tx_id: str, user: CurrentUserDep) -> None:
    tx_service.delete_transaction(user.user_id, tx_id)
