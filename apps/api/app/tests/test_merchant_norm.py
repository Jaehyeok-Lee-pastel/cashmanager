import pytest

from app.services import merchant_norm as m


@pytest.mark.parametrize(
    "token,expected",
    [
        ("맥날", "맥도날드"), ("스벅", "스타벅스"), ("올영", "올리브영"),
        ("배민", "배달의민족"), ("gs25", "GS25"), ("GS25", "GS25"),
        ("택시", "택시"), ("동네카페", "동네카페"),  # unknown -> unchanged
    ],
)
def test_normalize_merchant(token: str, expected: str):
    assert m.normalize_merchant(token) == expected


@pytest.mark.parametrize(
    "text,expected",
    [
        ("맥날 10000원 썼습니다", "맥도날드"),
        ("어제 택시 12000", "택시"),
        ("스벅 아메리카노 4900", "스타벅스 아메리카노"),
        ("지난주 금요일 회식 50000", "회식"),
        ("점심 김밥 8천원", "점심 김밥"),
        ("5/3 커피 4000", "커피"),
        ("올영 23000 샀어", "올리브영"),
    ],
)
def test_normalize_memo(text: str, expected: str):
    assert m.normalize_memo(text) == expected


def test_normalize_memo_keeps_unknown_merchant():
    assert m.normalize_memo("동네빵집 3000") == "동네빵집"
