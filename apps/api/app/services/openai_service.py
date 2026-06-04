"""OpenAI structured parsing for natural-language expense lines.

Single creation point for the OpenAI client. Uses Structured Outputs (strict
JSON schema) so the model can only return valid, in-vocabulary results.
"""

from datetime import date
from functools import lru_cache

from openai import OpenAI

from app.core.config import settings

_TIMEOUT_SECONDS = 8.0
_MAX_TOKENS = 150
_MAX_RETRIES = 0  # "LLM 1회" design: no SDK auto-retry (else 6s -> up to ~18s)

# Static instruction block kept identical across calls. NOTE: this block is far
# below OpenAI's ~1024-token prompt-cache threshold, so cache hits are not
# expected — cost is controlled by max_tokens + single-call + fast-path instead.
_SYSTEM = (
    "너는 한국어 가계부 입력 파서다. 한 줄 입력을 거래로 변환한다.\n"
    "규칙:\n"
    "- category는 반드시 주어진 목록 중 하나만 고른다.\n"
    "- 상호·브랜드·품목·맥락으로 카테고리를 적극 추론하라. 한국 브랜드/업종 지식을 활용한다.\n"
    "- '기타지출'은 추측이 안 될 때의 최후수단이지만, 회비/후원/기부/벌금/수수료/택배비처럼 "
    "어느 카테고리에도 안 맞는 지출은 '기타지출'(direction=expense)로 한다.\n"
    "- amount는 KRW 정수(원). 이미 결정된 값이 주어지면 그대로 쓴다.\n"
    "- '월급/급여/입금/정산/환급/용돈' 등 수입성 표현이면 direction='income'.\n"
    "- memo에는 상호/품목 등 원문 핵심을 남긴다.\n"
    "예시(브랜드→카테고리 추론):\n"
    "  '스벅 아메리카노 4900' -> 4900, 카페/간식, expense\n"
    "  '맥도날드 6000' / '맥날 5500' / '버거킹' -> 식비, expense\n"
    "  '영화 15000' / 'CGV 14000' / '넷플릭스 13500' -> 문화/여가, expense\n"
    "  '올리브영 23000' -> 쇼핑, expense\n"
    "  '편의점 3000' / 'GS25' / '이마트 32000' -> 생활/마트, expense\n"
    "  '약국 8000' / '병원 5000' -> 건강/의료, expense\n"
    "  '어제 택시 12000' / '버스카드 충전' / '주차비' / '통행료' / '주유' / '항공권' / '기차표' -> 교통, expense\n"
    "  '월급 3500000' -> 3500000, 수입, income"
)


@lru_cache
def _client() -> OpenAI:
    return OpenAI(
        api_key=settings.openai_api_key,
        timeout=_TIMEOUT_SECONDS,
        max_retries=_MAX_RETRIES,
    )


def complete(system: str, user: str, max_tokens: int = 300) -> str:
    """Generic text completion (no schema). Used by assistant/insights."""
    response = _client().chat.completions.create(
        model=settings.openai_model,
        max_completion_tokens=max_tokens,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    )
    return response.choices[0].message.content or ""


def _schema(categories: list[str]) -> dict:
    return {
        "type": "json_schema",
        "json_schema": {
            "name": "expense_parse",
            "strict": True,
            "schema": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "amount": {"type": "integer"},
                    "direction": {"type": "string", "enum": ["expense", "income"]},
                    "category": {"type": "string", "enum": categories or ["기타지출"]},
                    "memo": {"type": "string"},
                    "occurred_on": {
                        "type": "string",
                        "description": "날짜 YYYY-MM-DD (KST). 모르면 오늘 날짜.",
                    },
                    "confidence": {"type": "number"},
                },
                "required": [
                    "amount", "direction", "category", "memo", "occurred_on", "confidence",
                ],
            },
        },
    }


def parse_line(
    text: str,
    categories: list[str],
    today: date,
    known_amount: int | None = None,
    known_date: date | None = None,
) -> dict:
    """Call the LLM and return the parsed dict. Raises on error/timeout.

    Returns keys: amount, direction, category, memo, occurred_on, confidence,
    plus 'latency_ms' and 'model' metadata.
    """
    import json
    import time

    user_parts = [
        f"오늘 날짜(KST): {today.isoformat()}",
        f"카테고리 목록: {', '.join(categories)}",
    ]
    if known_amount is not None:
        user_parts.append(f"이미 결정된 금액: {known_amount} (그대로 사용)")
    if known_date is not None:
        user_parts.append(f"이미 결정된 날짜: {known_date.isoformat()} (그대로 사용)")
    user_parts.append(f"입력: {text}")

    start = time.monotonic()
    response = _client().chat.completions.create(
        model=settings.openai_model,
        max_completion_tokens=_MAX_TOKENS,  # newer models reject max_tokens
        response_format=_schema(categories),
        messages=[
            {"role": "system", "content": _SYSTEM},
            {"role": "user", "content": "\n".join(user_parts)},
        ],
    )
    latency_ms = int((time.monotonic() - start) * 1000)
    parsed = json.loads(response.choices[0].message.content)
    parsed["latency_ms"] = latency_ms
    parsed["model"] = settings.openai_model
    return parsed
