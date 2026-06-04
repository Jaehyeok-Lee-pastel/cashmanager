from fastapi import APIRouter, status

from app.api.deps import CurrentUserDep
from app.schemas.category import CategoryCreate, CategoryOut, CategoryUpdate
from app.services import category_service

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("", response_model=list[CategoryOut])
async def list_categories(user: CurrentUserDep) -> list[CategoryOut]:
    return category_service.list_categories(user.user_id)


@router.post("", response_model=CategoryOut, status_code=status.HTTP_201_CREATED)
async def create_category(payload: CategoryCreate, user: CurrentUserDep) -> CategoryOut:
    return category_service.create_category(user.user_id, payload)


@router.patch("/{category_id}", response_model=CategoryOut)
async def update_category(
    category_id: str, payload: CategoryUpdate, user: CurrentUserDep
) -> CategoryOut:
    return category_service.update_category(user.user_id, category_id, payload)


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def archive_category(category_id: str, user: CurrentUserDep) -> None:
    category_service.archive_category(user.user_id, category_id)
