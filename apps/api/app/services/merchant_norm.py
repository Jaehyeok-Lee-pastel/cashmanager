"""Record standardization: expand common Korean brand abbreviations to a canonical
name and strip filler so stored memos look uniform.

"맥날 10000원 썼습니다" -> memo "맥도날드"  (amount/date live in their own fields)
"스벅" and "스타벅스" both -> "스타벅스"     (one merchant-map key => better learning)

Conservative on purpose: only HIGH-confidence aliases are mapped; unknown
merchants ("동네카페") pass through untouched, and raw_input always keeps the
original text for rollback.
"""

import re

# abbreviation (lowercased) -> canonical brand name. Add entries as they come up.
ALIASES = {
    # 카페/베이커리
    "스벅": "스타벅스", "스타벅": "스타벅스", "투썸": "투썸플레이스",
    "컴포즈": "컴포즈커피", "파바": "파리바게뜨", "뚜쥬르": "뚜레쥬르",
    "던킨": "던킨도너츠", "배라": "배스킨라빈스",
    # 패스트푸드
    "맥날": "맥도날드", "맘스": "맘스터치", "롯리": "롯데리아",
    "버킹": "버거킹", "써브웨이": "서브웨이",
    # 치킨/배달
    "배민": "배달의민족", "비비큐": "BBQ",
    # 쇼핑
    "올영": "올리브영", "노스": "노스페이스", "무탠다드": "무신사스탠다드",
    # 마트/편의
    "홈플": "홈플러스", "세븐": "세븐일레븐", "gs25": "GS25", "cu": "CU",
    # 문화/스트리밍
    "넷플": "넷플릭스", "유튭": "유튜브", "cgv": "CGV", "메박": "메가박스",
    "롯시": "롯데시네마",
    # 교통
    "카택": "카카오택시",
}

# trailing/standalone filler verbs that carry no merchant info
FILLER = {
    "썼어", "썼습니다", "썼다", "씀", "샀어", "샀습니다", "샀다", "냈어", "냈습니다",
    "결제", "결제함", "결제했어", "지출", "먹었어", "먹음", "마셨어", "마심",
    "탔어", "탔다", "구매", "구입", "했어",
}

# a pure money token (digits, or sino-Korean numerals + unit) — dropped from memo
_AMOUNT_TOK = re.compile(r"^[\d,]+원?$|^[\d.]*[영일이삼사오육칠팔구만천백십]+원?$")

# date expressions live in the occurred_on field, so they don't belong in the memo
_DATE_WORDS = {"오늘", "어제", "그제", "그저께", "엊그제", "내일", "지난주", "저번주", "이번주"}
_DATE_TOK = re.compile(r"요일$|^\d+일\s*전$|^\d{1,2}/\d{1,2}$|^\d{1,2}월(\d{1,2}일)?$")


def normalize_merchant(token: str) -> str:
    """Map a merchant token to its canonical form (identity if unknown)."""
    return ALIASES.get(token.strip().lower(), token)


def _is_amount_token(token: str) -> bool:
    return token not in FILLER and bool(_AMOUNT_TOK.match(token))


def _is_date_token(token: str) -> bool:
    return token in _DATE_WORDS or bool(_DATE_TOK.search(token))


def normalize_memo(text: str) -> str:
    """Standardize a memo: expand brand aliases, drop filler/amount/date tokens."""
    kept = []
    for tok in text.split():
        if tok in FILLER or _is_amount_token(tok) or _is_date_token(tok):
            continue
        kept.append(normalize_merchant(tok))
    return " ".join(kept)
