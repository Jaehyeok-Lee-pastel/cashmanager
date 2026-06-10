from pydantic import BaseModel, Field


class ProfileOut(BaseModel):
    id: str
    email: str
    display_name: str | None = None
    pay_anchor_day: int | None = None  # payday (1~31); None = calendar-month budget


class ProfileUpdate(BaseModel):
    display_name: str | None = Field(default=None, max_length=50)
    pay_anchor_day: int | None = Field(default=None, ge=1, le=31)
