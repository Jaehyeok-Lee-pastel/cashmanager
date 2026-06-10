from pydantic import BaseModel, Field

from app.schemas.transaction import Direction


class RecurringCreate(BaseModel):
    category_id: str | None = None
    amount_minor: int = Field(gt=0)
    direction: Direction = "expense"
    day_of_month: int = Field(ge=1, le=31)
    memo: str | None = None
    active: bool = True


class RecurringUpdate(BaseModel):
    category_id: str | None = None
    amount_minor: int | None = Field(default=None, gt=0)
    direction: Direction | None = None
    day_of_month: int | None = Field(default=None, ge=1, le=31)
    memo: str | None = None
    active: bool | None = None


class RecurringOut(BaseModel):
    id: str
    category_id: str | None = None
    amount_minor: int
    direction: Direction
    day_of_month: int
    memo: str | None = None
    active: bool


class MaterializeResult(BaseModel):
    created: int
