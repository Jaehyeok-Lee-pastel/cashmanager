"""Deterministic pre-processing for natural-language expense lines.

Extracts amount and date with pure regex / numeral rules — NO LLM, NO cost.
Heavily unit-tested so Korean phrasing variety is covered by code, not by the
model's self-report. The LLM stage only fills what this cannot.

Conservative by design: when a value is not unambiguous, return None and let
the LLM decide, rather than guessing (a wrong "known" value would override the
LLM downstream).
"""

import re
from datetime import date, timedelta

from app.services import merchant_norm

_SINO_DIGIT = {
    "영": 0, "일": 1, "이": 2, "삼": 3, "사": 4,
    "오": 5, "육": 6, "칠": 7, "팔": 8, "구": 9,
}
_WEEKDAY = {"월": 0, "화": 1, "수": 2, "목": 3, "금": 4, "토": 5, "일": 6}

_SMALL_UNIT = {"십": 10, "백": 100, "천": 1000}
# A contiguous "number run": digits/decimal, sino digits, units, and 원.
_NUM_RUN = re.compile(r"[0-9.영일이삼사오육칠팔구만천백십원]+")


def _parse_korean_number(run: str) -> int | None:
    """Parse a sino-Korean / mixed number run, e.g. 만이천원=12000, 백만원=1000000,
    이만삼천=23000, 3만2천=32000, 오천=5000, 4.9천=4900.
    """
    total = 0.0
    section = 0.0  # value within the current 만-group
    current = 0.0  # number awaiting a unit
    buf = ""

    def take_buf() -> None:
        nonlocal buf, current
        if buf:
            current = float(buf)
            buf = ""

    for ch in run:
        if ch.isdigit() or ch == ".":
            buf += ch
            continue
        if ch in _SINO_DIGIT:
            take_buf()
            current = current * 10 + _SINO_DIGIT[ch]
            continue
        take_buf()
        if ch in _SMALL_UNIT:
            section += (current or 1) * _SMALL_UNIT[ch]
            current = 0
        elif ch == "만":
            section += current
            total += (section or 1) * 10_000
            section = 0
            current = 0
        # '원' and anything else: ignore
    take_buf()
    total += section + current
    return int(total) if total > 0 else None


def _merged_runs(text: str) -> list[str]:
    """Number runs, merging ones separated only by whitespace so "5만 1천원" reads
    as one amount (51000). Only merges when the previous run ends in a unit
    (만/천/백/십) so fragments of unrelated words ("친구 만남" -> 구|만) don't combine.
    """
    runs: list[str] = []
    last_end: int | None = None
    for m in _NUM_RUN.finditer(text):
        if (
            runs
            and last_end is not None
            and not text[last_end:m.start()].strip()
            and runs[-1][-1] in "만천백십"
        ):
            runs[-1] += m.group()
        else:
            runs.append(m.group())
        last_end = m.end()
    return runs


def _parse_units(text: str) -> int | None:
    """Parse amounts that use Korean units (만/천/백/십).

    Pure-digit amounts (no unit) return None here and are handled by parse_amount's
    other branches. A bare unit inside a word ("만나서", "친구 만남") is rejected.
    """
    for run in _merged_runs(text):
        if not any(u in run for u in "만천백십"):
            continue  # no unit -> not a units expression
        core = run.replace("원", "")
        has_digit = any(c.isdigit() for c in run)
        if not (has_digit or "원" in run or len(core) >= 2):
            continue  # bare "만"/"천" embedded in a word -> skip
        value = _parse_korean_number(run)
        if value:
            return value
    return None


# Phonetic misspellings of money units ("소리나는대로"). Restored ONLY when right
# after a number, so a merchant like "처넌" (not preceded by a digit) is untouched.
# Unseen typos fall through to the LLM rather than being mis-corrected here.
_UNIT_TYPOS = {
    "처넌": "천원", "처원": "천원", "천언": "천원", "천넌": "천원", "처눤": "천원",
    "마누언": "만원", "마눤": "만원", "마넌": "만원", "마누원": "만원", "마눠": "만원",
}
_DIGIT_CLASS = r"[0-9영일이삼사오육칠팔구]"
_UNIT_TYPO_RES = [
    (re.compile(rf"({_DIGIT_CLASS}\s*){re.escape(typo)}"), canon)
    for typo, canon in _UNIT_TYPOS.items()
]


def restore_amount_units(text: str) -> str:
    """Fix money-unit typos adjacent to a number: '3처넌' -> '3천원'."""
    for pattern, canon in _UNIT_TYPO_RES:
        text = pattern.sub(rf"\g<1>{canon}", text)
    return text


def parse_amount(text: str) -> int | None:
    """Return amount in KRW won, or None if no unambiguous amount is present."""
    t = restore_amount_units(text.replace(",", ""))
    units = _parse_units(t)
    if units is not None:
        return units

    # Accept an optional decimal and floor it: "100.00"->100, "15000.5"->15000
    # (KRW is integer won; without this the trailing-digit regex would grab the
    # fraction, e.g. "100.00"->0).
    explicit = re.search(r"(\d+(?:\.\d+)?)\s*원", t)
    if explicit:
        return int(float(explicit.group(1)))

    # Amounts are almost always the trailing token; a number followed by a
    # counter word (3잔, 2개) is NOT treated as an amount.
    tail = re.search(r"(\d+(?:\.\d+)?)\s*$", t.strip())
    if tail:
        return int(float(tail.group(1)))
    return None


def parse_date(text: str, today: date) -> tuple[date | None, str]:
    """Return (resolved_date, text_with_date_expression_removed)."""
    for keyword, delta in (("그저께", -2), ("그제", -2), ("엊그제", -2),
                           ("내일모레", 2), ("모레", 2), ("글피", 3),
                           ("오늘", 0), ("어제", -1), ("내일", 1)):
        if keyword in text:
            return today + timedelta(days=delta), text.replace(keyword, " ", 1)

    days_ago = re.search(r"(\d+)\s*일\s*전", text)
    if days_ago:
        resolved = today - timedelta(days=int(days_ago.group(1)))
        return resolved, text[: days_ago.start()] + text[days_ago.end():]

    weekday = re.search(
        r"(지난주\s*|저번주\s*|이번주\s*|다음주\s*|담주\s*)?([월화수목금토일])요일", text
    )
    if weekday:
        target = _WEEKDAY[weekday.group(2)]
        resolved = _resolve_weekday(today, target, _weekday_mode(weekday.group(1)))
        return resolved, text[: weekday.start()] + text[weekday.end():]

    # M월D일 — require 일 so amounts after a bare "M월" are not eaten.
    md = re.search(r"(\d{1,2})\s*월\s*(\d{1,2})\s*일", text)
    if md:
        resolved = _md_in_past(int(md.group(1)), int(md.group(2)), today)
        if resolved:
            return resolved, text[: md.start()] + text[md.end():]

    slash = re.search(r"\b(\d{1,2})/(\d{1,2})\b", text)
    if slash:
        resolved = _md_in_past(int(slash.group(1)), int(slash.group(2)), today)
        if resolved:
            return resolved, text[: slash.start()] + text[slash.end():]

    return None, text


# A bare M/D within this window ahead of today stays in the current year (a
# planned/near entry); only a FAR-future this-year date is read as last year
# (e.g. "12/31" typed in January = last December, not 11 months ahead).
_FUTURE_GRACE_DAYS = 183


def _md_in_past(month: int, day: int, today: date) -> date | None:
    """Resolve a bare month/day to its most likely year.

    Near future (<= ~6 months ahead) keeps this year; far future rolls back to
    last year, since a ledger entry that far ahead is almost certainly the date
    that just passed.
    """
    resolved = _safe_date(today.year, month, day)
    if resolved and (resolved - today).days > _FUTURE_GRACE_DAYS:
        return _safe_date(today.year - 1, month, day)
    return resolved


def _weekday_mode(prefix: str | None) -> str:
    prefix = prefix or ""
    if "지난" in prefix or "저번" in prefix:
        return "last"
    if "이번" in prefix:
        return "this"
    if "다음" in prefix or "담주" in prefix:
        return "next"
    return "recent"


def _resolve_weekday(today: date, target: int, mode: str) -> date:
    monday_this = today - timedelta(days=today.weekday())  # Monday of this week
    if mode == "last":
        return monday_this - timedelta(days=7) + timedelta(days=target)
    if mode == "this":
        return monday_this + timedelta(days=target)
    if mode == "next":
        return monday_this + timedelta(days=7) + timedelta(days=target)
    candidate = monday_this + timedelta(days=target)  # "recent": most recent past
    if candidate > today:
        candidate -= timedelta(days=7)
    return candidate


def _safe_date(year: int, month: int, day: int) -> date | None:
    try:
        return date(year, month, day)
    except ValueError:
        return None


# Credit-card BILL payment (a transfer, not new spending). Matches 카드대금/
# 카드값/카드비/카드 청구, 신용카드 결제·대금·자동이체 — but NOT a normal card
# purchase like "맥날 5500 카드" (that's an expense that happens to be paid by card).
_CARD_PAYMENT_RE = re.compile(
    r"카드\s*(대금|값|비|청구|결제대금)|신용카드\s*(결제|대금|자동이체)"
)


def is_card_payment(text: str) -> bool:
    """True when the line is paying off a credit-card bill (-> transfer)."""
    return bool(_CARD_PAYMENT_RE.search(text))


def is_trivial(text: str) -> bool:
    """True only for a PURE number (e.g. "5000", "5,000원").

    Such lines carry no categorization signal, so skipping the LLM costs nothing.
    A "<merchant> <amount>" line (e.g. "맥날 5500") is NOT trivial — the merchant
    IS the signal, so it must reach the LLM (or the learned merchant map).
    """
    return bool(re.fullmatch(r"[\d,]+\s*원?", text.strip()))


_DATE_WORDS = {"오늘", "어제", "그제", "그저께", "엊그제", "내일",
               "지난주", "저번주", "이번주"}

# Generic store TYPES (not brands) that sell across many categories. Learning
# "편의점 -> 식비" from "편의점 김밥" then mis-classifying "편의점 5000" is wrong, so
# we skip these and key off the next meaningful token ("김밥") instead. Brands like
# "이마트"/"올리브영" are specific and stay.
_GENERIC_MERCHANTS = {"편의점", "마트", "슈퍼", "슈퍼마켓", "백화점", "시장",
                      "가게", "상점", "몰", "쇼핑몰", "온라인", "스토어"}


def merchant_keyword(text: str) -> str | None:
    """Extract a normalized merchant keyword (first meaningful token).

    Skips amounts, dates, and generic store types so the learning map keys off a
    real signal: "맥날 5500" -> "맥날", "편의점 김밥 3500" -> "김밥",
    "편의점 5000" -> None (let the LLM decide; don't reuse a stale generic guess).
    """
    for token in text.split():
        low = token.strip().lower()
        if not low or low in _DATE_WORDS or low in _GENERIC_MERCHANTS:
            continue
        if any(ch.isdigit() for ch in low):
            continue
        if parse_amount(low) is not None:
            continue  # a Korean-numeral amount ("만이천원"), not a merchant
        if low.endswith("요일"):
            continue
        # canonicalize so "스벅"/"스타벅스" converge to one learning-map key
        return merchant_norm.normalize_merchant(low)
    return None
