from fastapi import APIRouter

from app.api.deps import CurrentUserDep
from app.schemas.profile import ProfileOut, ProfileUpdate
from app.services import profile_service

router = APIRouter(tags=["me"])


@router.get("/me", response_model=ProfileOut)
async def get_me(user: CurrentUserDep) -> ProfileOut:
    return profile_service.get_profile(user.user_id)


@router.patch("/me", response_model=ProfileOut)
async def update_me(payload: ProfileUpdate, user: CurrentUserDep) -> ProfileOut:
    return profile_service.update_profile(user.user_id, payload)
