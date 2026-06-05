from app.services import hangul


def test_restore_floating_jong_mid_word():
    assert hangul.restore_broken_jamo("기ㅁ밥") == "김밥"
    assert hangul.restore_broken_jamo("비해ㅇ기") == "비행기"


def test_restore_leaves_laughter_alone():
    assert hangul.restore_broken_jamo("좋아ㅋㅋ") == "좋아ㅋㅋ"
    assert hangul.restore_broken_jamo("ㅋㅋㅋ") == "ㅋㅋㅋ"


def test_restore_does_not_double_existing_final():
    # '김' already has a final ㅁ -> a following ㅂ must not merge
    assert hangul.restore_broken_jamo("김ㅂ") == "김ㅂ"


def test_restore_normal_text_unchanged():
    assert hangul.restore_broken_jamo("스타벅스 4900") == "스타벅스 4900"
    assert hangul.restore_broken_jamo("어제 택시 12000") == "어제 택시 12000"


def test_decompose_compose_roundtrip():
    for ch in "김밥행한글":
        cho, jung, jong = hangul.decompose(ch)
        assert hangul.compose(cho, jung, jong) == ch


def test_clean_is_idempotent():
    once = hangul.clean("기ㅁ밥 3000")
    assert once == "김밥 3000"
    assert hangul.clean(once) == once
