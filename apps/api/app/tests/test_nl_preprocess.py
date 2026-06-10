from datetime import date

import pytest

from app.services import nl_preprocess

TODAY = date(2026, 6, 2)  # Tuesday


@pytest.mark.parametrize(
    "text,expected",
    [
        ("스벅 아메리카노 4900", 4900),
        ("당근마켓 장보기 32000", 32000),
        ("택시 4,900원", 4900),
        ("만원", 10000),
        ("3만2천", 32000),
        ("3만", 30000),
        ("2천", 2000),
        ("4.9천", 4900),
        ("오천", 5000),
        ("이만원", 20000),
        ("커피 3천원", 3000),
        ("만이천원", 12000),
        ("맥날 만이천원", 12000),
        ("이만삼천", 23000),
        ("백만원", 1000000),
        ("삼만오천원", 35000),
        # money-unit typos restored only when adjacent to a number
        ("3처넌", 3000),
        ("김밥 3처넌", 3000),
        ("12마누언", 120000),
        ("커피 2마눤", 20000),
    ],
)
def test_parse_amount(text: str, expected: int):
    assert nl_preprocess.parse_amount(text) == expected


def test_unit_typo_not_restored_without_number():
    # "처넌" as a bare word (no preceding digit) must NOT become an amount
    assert nl_preprocess.parse_amount("처넌 가게") is None


def test_parse_amount_none_when_no_number():
    assert nl_preprocess.parse_amount("커피 마심") is None


@pytest.mark.parametrize("text,expected", [
    ("100.00", 100), ("15000.5", 15000), ("3.5", 3), ("3,000.50원", 3000),
    ("커피 4900.0", 4900),
])
def test_parse_amount_decimals_floored(text: str, expected: int):
    assert nl_preprocess.parse_amount(text) == expected


@pytest.mark.parametrize("text,expected", [
    ("5만 1천원", 51000),   # space-separated units merge into one amount
    ("삼만 오천원", 35000),
    ("오만 천원", 51000),
])
def test_parse_amount_spaced_units(text: str, expected: int):
    assert nl_preprocess.parse_amount(text) == expected


@pytest.mark.parametrize("text,expected", [
    ("내일모레 약속 5000", date(2026, 6, 4)),
    ("모레 커피 4000", date(2026, 6, 4)),
    ("글피 모임 3000", date(2026, 6, 5)),
    ("다음주 월요일 점심 9000", date(2026, 6, 8)),
    ("다음주 수요일 5000", date(2026, 6, 10)),
    ("담주 금요일 회식 50000", date(2026, 6, 12)),
])
def test_parse_date_future_words(text: str, expected: date):
    resolved, _ = nl_preprocess.parse_date(text, TODAY)
    assert resolved == expected


@pytest.mark.parametrize(
    "text",
    [
        "만나서 커피",      # '만' inside a word must not become 10000
        "친구 만남",        # no numeral adjacent to 만 -> no phantom amount
        "아메리카노 3잔",   # counter word, not an amount
        "6월 30000 커피",   # amount not trailing -> defer to LLM, never corrupt
    ],
)
def test_parse_amount_no_phantom(text: str):
    assert nl_preprocess.parse_amount(text) is None


@pytest.mark.parametrize(
    "text,expected",
    [
        ("오늘 커피 4900", date(2026, 6, 2)),
        ("어제 택시 12000", date(2026, 6, 1)),
        ("그제 점심 9000", date(2026, 5, 31)),
        ("3일전 마트 20000", date(2026, 5, 30)),
        ("5월3일 영화 15000", date(2026, 5, 3)),
        ("5/3 커피 4000", date(2026, 5, 3)),
    ],
)
def test_parse_date(text: str, expected: date):
    resolved, _ = nl_preprocess.parse_date(text, TODAY)
    assert resolved == expected


def test_parse_date_weekday_this_week():
    # TODAY is Tue 2026-06-02; most recent Monday is 2026-06-01.
    resolved, _ = nl_preprocess.parse_date("월요일 점심 9000", TODAY)
    assert resolved == date(2026, 6, 1)


def test_parse_date_last_week():
    # 지난주 금요일 -> Friday of previous week = 2026-05-29.
    resolved, _ = nl_preprocess.parse_date("지난주 금요일 회식 50000", TODAY)
    assert resolved == date(2026, 5, 29)


def test_parse_date_this_week_future_weekday():
    # 이번주 수요일 -> this week's Wednesday = 2026-06-03 (not last week's).
    resolved, _ = nl_preprocess.parse_date("이번주 수요일 점심 9000", TODAY)
    assert resolved == date(2026, 6, 3)


def test_parse_date_future_md_falls_back_to_last_year():
    # "12/31" typed on 2026-06-02 means last year, not ~7 months in the future.
    resolved, _ = nl_preprocess.parse_date("12/31 선물 30000", TODAY)
    assert resolved == date(2025, 12, 31)


def test_parse_date_md_year_wrap_in_january():
    jan = date(2026, 1, 5)
    # "12월30일" typed in January -> previous December, not this year's future.
    resolved, _ = nl_preprocess.parse_date("12월30일 외식 20000", jan)
    assert resolved == date(2025, 12, 30)


def test_parse_date_near_future_md_stays_this_year():
    # "6월30일" typed on 2026-06-02 is only ~4 weeks ahead -> this year (planned),
    # NOT rolled back to last year.
    resolved, _ = nl_preprocess.parse_date("6월30일 회비 20000", TODAY)
    assert resolved == date(2026, 6, 30)


def test_parse_date_bare_month_does_not_eat_amount():
    # "6월" with no 일 must NOT be parsed as a date (would steal amount digits).
    resolved, remainder = nl_preprocess.parse_date("6월 30000 커피", TODAY)
    assert resolved is None
    assert "30000" in remainder


def test_parse_date_none_when_absent():
    resolved, remainder = nl_preprocess.parse_date("커피 4900", TODAY)
    assert resolved is None
    assert remainder == "커피 4900"


def test_parse_date_strips_expression():
    _, remainder = nl_preprocess.parse_date("어제 택시 12000", TODAY)
    assert "어제" not in remainder
    assert "택시" in remainder


@pytest.mark.parametrize(
    "text,trivial",
    [
        ("4900", True),
        ("4,900원", True),
        ("스벅 4900", False),  # merchant present -> must reach LLM/map
        ("맥날 5500", False),
        ("영화 15000", False),
        ("스벅 아메리카노 4900", False),
    ],
)
def test_is_trivial(text: str, trivial: bool):
    assert nl_preprocess.is_trivial(text) is trivial


@pytest.mark.parametrize(
    "text,expected",
    [
        ("카드대금 1200000", True),
        ("이번달 카드값 80만원", True),
        ("신용카드 결제 50만", True),
        ("신용카드 자동이체 45만원", True),
        ("카드비 30만원", True),
        ("맥날 5500 카드", False),  # a purchase paid by card -> NOT a bill payment
        ("스타벅스 카드 4000", False),
        ("택시 12000", False),
    ],
)
def test_is_card_payment(text: str, expected: bool):
    assert nl_preprocess.is_card_payment(text) is expected


@pytest.mark.parametrize(
    "text,keyword",
    [
        ("맥날 5500", "맥도날드"),  # alias canonicalized for map-key convergence
        ("어제 택시 12000", "택시"),
        ("스벅 아메리카노 4900", "스타벅스"),
        ("지난주 금요일 회식 50000", "회식"),
        ("5000", None),
        # generic store types are skipped so the learning map keys off real signal
        ("편의점 김밥 3500", "김밥"),
        ("편의점 5000", None),
        ("마트 만이천원", None),
        ("이마트 32000", "이마트"),  # a brand is specific -> kept
        ("편의점", None),
    ],
)
def test_merchant_keyword(text: str, keyword: str | None):
    assert nl_preprocess.merchant_keyword(text) == keyword
