from fastapi import HTTPException, status

from app.core.timeutils import datetime_now_iso
from app.repositories import category_repo
from app.schemas.category import CategoryCreate, CategoryOut, CategoryUpdate


def list_categories(user_id: str) -> list[CategoryOut]:
    rows = category_repo.list_categories(user_id)
    return [CategoryOut(**row) for row in rows]


def _require_owned(user_id: str, category_id: str) -> dict:
    row = category_repo.get_category(user_id, category_id)
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="카테고리를 찾을 수 없습니다."
        )
    return row


def create_category(user_id: str, payload: CategoryCreate) -> CategoryOut:
    fields = payload.model_dump(exclude_unset=True)
    try:
        row = category_repo.create_category(user_id, fields)
    except Exception as exc:  # noqa: BLE001 — unique (user_id, name) collision
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="이미 같은 이름의 카테고리가 있습니다.",
        ) from exc
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="카테고리 생성에 실패했습니다.",
        )
    return CategoryOut(**row)


def update_category(
    user_id: str, category_id: str, payload: CategoryUpdate
) -> CategoryOut:
    _require_owned(user_id, category_id)
    fields = payload.model_dump(exclude_unset=True)
    row = category_repo.update_category(user_id, category_id, fields)
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="카테고리를 찾을 수 없습니다."
        )
    return CategoryOut(**row)


def archive_category(user_id: str, category_id: str) -> None:
    _require_owned(user_id, category_id)
    category_repo.archive_category(user_id, category_id, datetime_now_iso())
