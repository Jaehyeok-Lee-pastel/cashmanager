from pydantic import BaseModel, Field


class CategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=40)
    emoji: str | None = Field(default=None, max_length=8)
    sort_order: int = 100


class CategoryUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=40)
    emoji: str | None = Field(default=None, max_length=8)
    sort_order: int | None = None


class CategoryOut(BaseModel):
    id: str
    name: str
    emoji: str | None = None
    sort_order: int
