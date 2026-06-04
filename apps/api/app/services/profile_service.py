from fastapi import HTTPException, status

from app.repositories import profile_repo
from app.schemas.profile import ProfileOut, ProfileUpdate


def get_profile(user_id: str) -> ProfileOut:
    row = profile_repo.get_profile(user_id)
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="프로필을 찾을 수 없습니다."
        )
    return ProfileOut(**row)


def update_profile(user_id: str, payload: ProfileUpdate) -> ProfileOut:
    fields = payload.model_dump(exclude_unset=True)
    row = profile_repo.update_profile(user_id, fields)
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="프로필을 찾을 수 없습니다."
        )
    return ProfileOut(**row)
