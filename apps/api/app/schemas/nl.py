from datetime import date
from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.transaction import Direction, TxSource

AmbiguousField = Literal["amount", "category", "memo", "date"]


class ParseRequest(BaseModel):
    text: str = Field(min_length=1, max_length=200)


class ParseResult(BaseModel):
    """Non-persisted preview of a parsed natural-language line.

    The frontend shows this in a confirm card; nothing is saved until the
    user confirms via POST /transactions.
    """

    amount_minor: int | None = None
    direction: Direction = "expense"
    category_id: str | None = None
    category_name: str | None = None
    memo: str | None = None
    occurred_on: date | None = None
    confidence: float = 0.0
    ambiguous_fields: list[AmbiguousField] = []
    needs_manual: bool = False
    source: TxSource = "nl_text"  # recommended source to persist on confirm
    raw_input: str = ""
    parse_meta: dict | None = None
