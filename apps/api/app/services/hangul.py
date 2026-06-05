"""Pure-Python Hangul jamo utilities (no external deps).

Repairs 'broken' input where a standalone compatibility jamo got separated from
its syllable — a common mobile mistype:
    "기ㅁ밥"  -> "김밥"
    "비해ㅇ기" -> "비행기"

NFC normalization alone does NOT fix these: Unicode deliberately does not compose
standalone compatibility jamo (U+3131..) into syllables, so we recompose using the
0xAC00 syllable formula.
"""

import unicodedata

_BASE = 0xAC00  # '가'
_CHO = "ㄱㄲㄴㄷㄸㄹㅁㅂㅃㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎ"
_JUNG = "ㅏㅐㅑㅒㅓㅔㅕㅖㅗㅘㅙㅚㅛㅜㅝㅞㅟㅠㅡㅢㅣ"
# index 0 == no final (jongseong); placeholder space keeps the indexing aligned.
_JONG = " ㄱㄲㄳㄴㄵㄶㄷㄹㄺㄻㄼㄽㄾㄿㅀㅁㅂㅄㅅㅆㅇㅈㅊㅋㅌㅍㅎ"

# single consonants a user actually types that are valid simple finals
_SIMPLE_JONG = set("ㄱㄲㄴㄷㄹㅁㅂㅅㅆㅇㅈㅊㅋㅌㅍㅎ")


def is_syllable(ch: str) -> bool:
    return 0 <= ord(ch) - _BASE < 11172


def is_compat_jamo(ch: str) -> bool:
    """A standalone compatibility jamo (U+3131..U+3163), e.g. typed 'ㅁ'."""
    return bool(ch) and 0x3131 <= ord(ch) <= 0x3163


def decompose(ch: str) -> tuple[str, str, str]:
    """Syllable -> (cho, jung, jong); jong is ' ' when absent."""
    code = ord(ch) - _BASE
    return _CHO[code // 28 // 21], _JUNG[(code // 28) % 21], _JONG[code % 28]


def compose(cho: str, jung: str, jong: str = " ") -> str:
    return chr(_BASE + (_CHO.index(cho) * 21 + _JUNG.index(jung)) * 28 + _JONG.index(jong))


def restore_broken_jamo(text: str) -> str:
    """Absorb a floating consonant into the previous syllable as its final.

    Conservative: only when the previous char is a complete syllable WITHOUT a
    final, the floating jamo is a valid simple final, and it is not part of a
    jamo run (so "좋아ㅋㅋ" / "ㅋㅋ" are left alone).
    """
    out: list[str] = []
    for i, ch in enumerate(text):
        if ch in _SIMPLE_JONG and out and is_syllable(out[-1]):
            cho, jung, jong = decompose(out[-1])
            nxt = text[i + 1] if i + 1 < len(text) else ""
            if jong == " " and not is_compat_jamo(nxt):
                out[-1] = compose(cho, jung, ch)
                continue
        out.append(ch)
    return "".join(out)


def clean(text: str) -> str:
    """Entry-point normalization: NFC + broken-jamo repair. Idempotent."""
    return restore_broken_jamo(unicodedata.normalize("NFC", text))
