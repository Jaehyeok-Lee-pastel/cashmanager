from typing import Literal

from pydantic import BaseModel, Field

Severity = Literal["alert", "warn", "info"]


class InsightCard(BaseModel):
    type: str  # "budget" | "top" | "trend" | "coach"
    severity: Severity
    title: str
    detail: str


class AssistantQuery(BaseModel):
    question: str = Field(min_length=1, max_length=200)


class AssistantAnswer(BaseModel):
    answer: str
