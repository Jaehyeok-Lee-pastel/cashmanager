"""Comprehensive deterministic-layer regression suite (was an ad-hoc QA script).

Covers amount parsing, Korean numerals, money-unit typos, jamo restoration
(generated + explicit), syllable roundtrip, date resolution, card detection.
Kept exhaustive on purpose — this is the reproducible form of the "324-case QA".
"""
from datetime import date

import pytest

from app.services import hangul
from app.services import nl_preprocess as p

TODAY = date(2026, 6, 2)  # Tuesday


# ---------- amounts ----------
@pytest.mark.parametrize("text,exp", [
    ("5000", 5000), ("12000", 12000), ("100", 100), ("1500원", 1500),
    ("3,000", 3000), ("3,000원", 3000), ("1,234,567", 1234567), ("커피 4900", 4900),
    ("택시 12000원", 12000), ("올리브영 23000", 23000), ("0", 0), ("750000", 750000),
])
def test_digit_amounts(text, exp):
    assert p.parse_amount(text) == exp


@pytest.mark.parametrize("text", ["아메리카노 3잔", "맥주 2개", "5명", "커피 마심", "3잔", "10번"])
def test_no_amount(text):
    assert p.parse_amount(text) is None


@pytest.mark.parametrize("text,exp", [
    ("만원", 10000), ("천원", 1000), ("오천원", 5000), ("삼천원", 3000), ("이만원", 20000),
    ("삼만오천원", 35000), ("백만원", 1000000), ("이만삼천", 23000), ("3만2천", 32000),
    ("삼천오백", 3500), ("사천오백원", 4500), ("오만원", 50000), ("십만원", 100000),
    ("만이천원", 12000), ("맥날 만이천원", 12000), ("4.9천", 4900), ("점심 김밥 8천원", 8000),
])
def test_korean_numerals(text, exp):
    assert p.parse_amount(text) == exp


_UNIT_VARIANTS = {"처넌": 1000, "처원": 1000, "천언": 1000, "천넌": 1000, "처눤": 1000,
                  "마누언": 10000, "마눤": 10000, "마넌": 10000, "마누원": 10000, "마눠": 10000}


@pytest.mark.parametrize("typo,mult", list(_UNIT_VARIANTS.items()))
@pytest.mark.parametrize("d", [1, 3, 5, 12])
def test_unit_typos(typo, mult, d):
    assert p.parse_amount(f"{d}{typo}") == d * mult


@pytest.mark.parametrize("text,exp", [
    ("삼처넌", 3000), ("김밥 3처넌", 3000), ("커피 2마눤", 20000), ("택시 7마누언", 70000),
])
def test_unit_typos_in_context(text, exp):
    assert p.parse_amount(text) == exp


@pytest.mark.parametrize("text", ["처넌 가게", "마누언", "처넌집 커피", "마넌상회"])
def test_unit_typos_not_adjacent(text):
    assert p.parse_amount(text) is None


# ---------- jamo restoration ----------
_WORDS = ["김밥", "행복", "사랑", "한글", "점심", "저녁", "택시", "통신", "건강", "문화",
          "생활", "음식", "영화", "안경", "가방", "신발", "양말", "장갑", "라면", "김치",
          "된장", "간장", "설탕", "소금", "국밥", "비빔밥", "삼겹살", "당근", "마늘", "호박",
          "감자", "옥수수", "딸기", "버섯", "편의점", "백화점", "주말", "월급", "용돈", "통장",
          "공원", "식당", "빵집", "과일", "우산", "연필", "책상", "손목", "발목", "목살",
          "술집", "찜닭", "냉면", "볶음밥", "간식", "야식", "구름", "바람", "햇빛"]


def _break_first(word):
    for i, ch in enumerate(word):
        if hangul.is_syllable(ch):
            cho, jung, jong = hangul.decompose(ch)
            if jong != " " and jong in hangul._SIMPLE_JONG:
                nxt = word[i + 1] if i + 1 < len(word) else ""
                if hangul.is_compat_jamo(nxt):
                    continue
                return word[:i] + hangul.compose(cho, jung) + jong + word[i + 1:]
    return None


@pytest.mark.parametrize("word", _WORDS)
def test_jamo_restore_generated(word):
    broken = _break_first(word)
    if broken and broken != word:
        assert hangul.restore_broken_jamo(broken) == word


@pytest.mark.parametrize("broken,exp", [
    ("기ㅁ밥", "김밥"), ("비해ㅇ기", "비행기"), ("바ㅂ", "밥"), ("그ㅁ", "금"),
    ("좋아ㅋㅋ", "좋아ㅋㅋ"), ("ㅋㅋㅋ", "ㅋㅋㅋ"), ("김ㅂ", "김ㅂ"),
    ("스타벅스 4900", "스타벅스 4900"), ("어제 택시 12000", "어제 택시 12000"),
])
def test_jamo_restore_explicit(broken, exp):
    assert hangul.restore_broken_jamo(broken) == exp


@pytest.mark.parametrize("ch", list("김밥행복사랑한글점심저녁택시건강문화생활음식영화안경값닭읽몫공원식당빵집과일우산연필책상손목발목목살술집냉면구름바람"))
def test_syllable_roundtrip(ch):
    if hangul.is_syllable(ch):
        cho, jung, jong = hangul.decompose(ch)
        assert hangul.compose(cho, jung, jong) == ch


# ---------- dates ----------
@pytest.mark.parametrize("text,exp", [
    ("오늘 커피 4900", date(2026, 6, 2)), ("어제 택시 12000", date(2026, 6, 1)),
    ("그제 점심 9000", date(2026, 5, 31)), ("그저께 술 30000", date(2026, 5, 31)),
    ("엊그제 책 15000", date(2026, 5, 31)), ("내일 예약 10000", date(2026, 6, 3)),
    ("3일전 마트 20000", date(2026, 5, 30)), ("5일 전 약속 5000", date(2026, 5, 28)),
    ("월요일 점심 9000", date(2026, 6, 1)), ("화요일 커피 4000", date(2026, 6, 2)),
    ("수요일 저녁 12000", date(2026, 5, 27)), ("이번주 수요일 점심 9000", date(2026, 6, 3)),
    ("지난주 금요일 회식 50000", date(2026, 5, 29)), ("저번주 월요일 5000", date(2026, 5, 25)),
    ("5월3일 영화 15000", date(2026, 5, 3)), ("12월31일 파티 30000", date(2025, 12, 31)),
    ("5/3 커피 4000", date(2026, 5, 3)), ("12/31 선물 30000", date(2025, 12, 31)),
    ("6월30일 회비 20000", date(2026, 6, 30)),
])
def test_dates(text, exp):
    assert p.parse_date(text, TODAY)[0] == exp


@pytest.mark.parametrize("text", ["커피 4900", "6월 30000 커피", "스벅 5000", "맥날 5500"])
def test_dates_absent(text):
    assert p.parse_date(text, TODAY)[0] is None


# ---------- card payment / trivial ----------
@pytest.mark.parametrize("text", [
    "카드대금 1200000", "카드값 80만원", "신용카드 결제 50만", "신용카드 자동이체 45만원",
    "카드비 30만원", "이번달 카드대금", "카드 청구 50만", "카드대금 자동이체",
])
def test_card_payment_positive(text):
    assert p.is_card_payment(text) is True


@pytest.mark.parametrize("text", [
    "맥날 5500 카드", "스타벅스 카드 4000", "택시 12000", "카드 샀어",
    "신한카드 결제 3만", "카드지갑 30000", "기프트카드 5만원", "체크카드 결제 2만",
])
def test_card_payment_negative(text):
    assert p.is_card_payment(text) is False


@pytest.mark.parametrize("text,exp", [
    ("5000", True), ("5,000원", True), ("5000원", True), ("12000", True), ("100", True),
    ("스벅 5000", False), ("맥날 5500", False), ("영화 15000", False), ("3천원", False),
])
def test_is_trivial(text, exp):
    assert p.is_trivial(text) is exp
