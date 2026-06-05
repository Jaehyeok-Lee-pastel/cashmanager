from pydantic import BaseModel


class CategorySummary(BaseModel):
    category_id: str | None = None
    name: str
    emoji: str | None = None
    sum_minor: int
    ratio: float  # share of total expense (0.0 ~ 1.0)
    limit_minor: int | None = None  # monthly budget limit, if set
    # Projected month-end spend at the current pace; None unless the month is
    # in progress and past the early-noise window. See summary_service.
    projected_minor: int | None = None


class MonthlySummaryOut(BaseModel):
    month: str  # "YYYY-MM"
    total_expense: int
    total_income: int
    count: int
    by_category: list[CategorySummary]
    # Projected total month-end expense at the current pace (None when N/A).
    projected_expense: int | None = None
