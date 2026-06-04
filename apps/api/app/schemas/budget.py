from pydantic import BaseModel, Field

_MAX_LIMIT = 1_000_000_000_000  # sane upper bound (KRW won)


class BudgetItem(BaseModel):
    category_id: str
    limit_minor: int = Field(gt=0, le=_MAX_LIMIT)


class BudgetUpsert(BaseModel):
    """Bulk upsert — only the sent items are written; removal uses DELETE."""

    budgets: list[BudgetItem]


class BudgetOut(BaseModel):
    category_id: str
    limit_minor: int


class BudgetSuggestion(BaseModel):
    category_id: str
    name: str
    suggested_minor: int
