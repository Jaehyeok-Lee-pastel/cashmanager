"""Record-standardization regression suite (reproducible form of the 248-case QA).

Iterates the full alias map + memo normalization matrix + token classifiers.
"""
import pytest

from app.services import merchant_norm as m
from app.services import nl_preprocess as p


# every alias maps to its canonical, and the canonical is stable (idempotent)
@pytest.mark.parametrize("alias,canon", list(m.ALIASES.items()))
def test_every_alias_maps(alias, canon):
    assert m.normalize_merchant(alias) == canon
    assert m.normalize_merchant(canon) == canon


@pytest.mark.parametrize("tok", ["택시", "회식", "김밥", "동네카페", "할머니국밥", "이마트", "맥도날드", "스타벅스"])
def test_unknown_merchant_unchanged(tok):
    assert m.normalize_merchant(tok) == tok


@pytest.mark.parametrize("tok,exp", [("GS25", "GS25"), ("gs25", "GS25"), ("CGV", "CGV"), ("cgv", "CGV"), ("맥날", "맥도날드")])
def test_merchant_case_insensitive(tok, exp):
    assert m.normalize_merchant(tok) == exp


# alias expansion with amount dropped -> canonical only (whole map)
@pytest.mark.parametrize("alias,canon", list(m.ALIASES.items()))
def test_memo_alias_amount_dropped(alias, canon):
    assert m.normalize_memo(f"{alias} 5000") == canon


@pytest.mark.parametrize("text,exp", [
    ("맥날 10000원 썼습니다", "맥도날드"),
    ("어제 택시 12000", "택시"),
    ("스벅 아메리카노 4900", "스타벅스 아메리카노"),
    ("올영 23000 샀어", "올리브영"),
    ("점심 김밥 8천원", "점심 김밥"),
    ("5/3 커피 4000", "커피"),
    ("지난주 금요일 회식 50000", "회식"),
    ("배민 치킨 20000", "배달의민족 치킨"),
    ("커피 마심", "커피"),
    ("택시 탔어", "택시"),
    ("오늘 커피", "커피"),
    ("3일전 마트", "마트"),
    ("5월3일 영화", "영화"),
    ("커피 만원", "커피"),
    ("삼천원 김밥", "김밥"),
    ("동네카페 4000", "동네카페"),
    ("할머니국밥 8000", "할머니국밥"),
    ("어제 맥날 만원 먹음", "맥도날드"),
    ("삼겹살 22000", "삼겹살"),
    ("천호동 김밥 5000", "천호동 김밥"),
    ("백반 8000", "백반"),
    ("넷플 13500", "넷플릭스"),
    ("홈플 장보기 32000", "홈플러스 장보기"),
    ("10000원", ""),
    ("샀어", ""),
    ("어제", ""),
])
def test_normalize_memo(text, exp):
    assert m.normalize_memo(text) == exp


@pytest.mark.parametrize("text,exp", [
    ("맥날 10000원 썼습니다", "맥도날드"), ("스벅 아메리카노 4900", "스타벅스 아메리카노"),
    ("어제 택시 12000", "택시"), ("배민 치킨 20000", "배달의민족 치킨"),
])
def test_normalize_memo_idempotent(text, exp):
    once = m.normalize_memo(text)
    assert m.normalize_memo(once) == once == exp


# merchant_keyword: alias convergence + skips (generic/amount/date)
@pytest.mark.parametrize("text,exp", [
    ("맥날 5500", "맥도날드"), ("스벅 아메리카노 4900", "스타벅스"),
    ("배민 치킨 20000", "배달의민족"), ("올영 23000", "올리브영"),
    ("택시 12000", "택시"), ("이마트 32000", "이마트"),
    ("어제 스벅 4900", "스타벅스"), ("내일 맥날 6000", "맥도날드"),
    ("편의점 김밥 3500", "김밥"), ("편의점 5000", None),
    ("마트 만이천원", None), ("백화점 쇼핑 50000", "쇼핑"),
    ("5000", None), ("만이천원", None), ("스타벅스 5000", "스타벅스"),
])
def test_merchant_keyword(text, exp):
    assert p.merchant_keyword(text) == exp


@pytest.mark.parametrize("tok,exp", [
    ("10000", True), ("10,000", True), ("만원", True), ("3천원", True), ("8천", True),
    ("삼천원", True), ("이만", True), ("백만원", True),
    ("택시", False), ("맥도날드", False), ("삼겹살", False), ("백반", False),
    ("천호동", False), ("만남", False), ("썼어", False), ("원", False), ("5/3", False),
])
def test_is_amount_token(tok, exp):
    assert m._is_amount_token(tok) is exp


@pytest.mark.parametrize("tok,exp", [
    ("어제", True), ("오늘", True), ("지난주", True), ("금요일", True), ("월요일", True),
    ("3일전", True), ("5/3", True), ("12/31", True), ("5월3일", True), ("6월", True),
    ("택시", False), ("회식", False), ("5000", False), ("월급", False), ("월세", False),
])
def test_is_date_token(tok, exp):
    assert m._is_date_token(tok) is exp
