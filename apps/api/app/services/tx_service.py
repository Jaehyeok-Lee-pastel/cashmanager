from fastapi import HTTPException, status

import logging

from app.core.timeutils import month_bounds, today_kst
from app.repositories import category_repo, merchant_map_repo, tx_repo
from app.schemas.transaction import TransactionCreate, TransactionOut, TransactionUpdate
from app.services import nl_preprocess

logger = logging.getLogger(__name__)


def _verify_category(user_id: str, category_id: str | None) -> None:
    """Ensure a referenced category belongs to the user (RLS is bypassed by service_role)."""
    if category_id is None:
        return
    if category_repo.get_category(user_id, category_id) is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="존재하지 않거나 권한이 없는 카테고리입니다.",
        )


def list_transactions(
    user_id: str, month: str, category_id: str | None = None
) -> list[TransactionOut]:
    start, end = month_bounds(month)
    rows = tx_repo.list_transactions(user_id, start, end, category_id)
    return [TransactionOut(**row) for row in rows]


def create_transaction(user_id: str, payload: TransactionCreate) -> TransactionOut:
    _verify_category(user_id, payload.category_id)
    fields = payload.model_dump()  # include defaults (direction, source)
    fields["occurred_on"] = (payload.occurred_on or today_kst()).isoformat()
    row = tx_repo.create_transaction(user_id, fields)
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="거래 저장에 실패했습니다.",
        )
    _learn_merchant(user_id, payload)
    return TransactionOut(**row)


def _learn_merchant(user_id: str, payload: TransactionCreate) -> None:
    """Remember merchant -> category so future inputs classify without the LLM."""
    if not payload.category_id or not payload.raw_input:
        return
    keyword = nl_preprocess.merchant_keyword(payload.raw_input)
    if not keyword:
        return
    try:
        merchant_map_repo.upsert(user_id, keyword, payload.category_id)
    except Exception as exc:  # noqa: BLE001 — learning is best-effort
        logger.warning("merchant map upsert failed: %s", exc)


def update_transaction(
    user_id: str, tx_id: str, payload: TransactionUpdate
) -> TransactionOut:
    if tx_repo.get_transaction(user_id, tx_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="거래를 찾을 수 없습니다."
        )
    fields = payload.model_dump(exclude_unset=True)
    if "category_id" in fields:
        _verify_category(user_id, fields["category_id"])
    if fields.get("occurred_on") is not None:
        fields["occurred_on"] = fields["occurred_on"].isoformat()
    row = tx_repo.update_transaction(user_id, tx_id, fields)
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="거래를 찾을 수 없습니다."
        )
    return TransactionOut(**row)


def delete_transaction(user_id: str, tx_id: str) -> None:
    if tx_repo.get_transaction(user_id, tx_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="거래를 찾을 수 없습니다."
        )
    tx_repo.delete_transaction(user_id, tx_id)
