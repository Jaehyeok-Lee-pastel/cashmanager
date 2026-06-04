from datetime import date
from typing import Literal

from pydantic import BaseModel, Field

Direction = Literal["expense", "income"]
TxSource = Literal["nl_text", "manual", "receipt", "voice", "import"]


class TransactionCreate(BaseModel):
    amount_minor: int = Field(gt=0)
    direction: Direction = "expense"
    category_id: str | None = None
    memo: str | None = None
    occurred_on: date | None = None  # defaults to today in the service layer
    source: TxSource = "manual"
    raw_input: str | None = None
    parse_meta: dict | None = None


class TransactionUpdate(BaseModel):
    amount_minor: int | None = Field(default=None, gt=0)
    direction: Direction | None = None
    category_id: str | None = None
    memo: str | None = None
    occurred_on: date | None = None


class TransactionOut(BaseModel):
    id: str
    amount_minor: int
    direction: Direction
    category_id: str | None = None
    memo: str | None = None
    occurred_on: date
    source: TxSource
    created_at: str
