from pydantic import BaseModel


class ProfileOut(BaseModel):
    id: str
    email: str
    display_name: str | None = None


class ProfileUpdate(BaseModel):
    display_name: str | None = None
