from pydantic import BaseModel, Field


class ProfileOut(BaseModel):
    id: str
    email: str
    display_name: str | None = None


class ProfileUpdate(BaseModel):
    display_name: str | None = Field(default=None, max_length=50)
