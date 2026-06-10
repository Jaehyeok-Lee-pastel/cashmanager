from app.services.summary_service import _is_investment_row, _safe_to_spend


def test_safe_to_spend_none_without_budget():
    assert _safe_to_spend(0, 50000, 0, 0, 20, True) == (None, None)


def test_safe_to_spend_none_when_not_current():
    assert _safe_to_spend(100000, 50000, 0, 0, 20, False) == (None, None)


def test_safe_to_spend_math():
    # budget 100,000 - spent 30,000 over 21 days left
    safe, daily = _safe_to_spend(100000, 30000, 0, 0, 21, True)
    assert safe == 70000
    assert daily == round(70000 / 21)


def test_safe_to_spend_negative_when_over_budget():
    safe, _ = _safe_to_spend(100000, 150000, 0, 0, 10, True)
    assert safe == -50000


def test_safe_to_spend_subtracts_fixed_and_investment():
    # 1,000,000 - spent 30,000 - fixed 0 - invest 200,000 = 770,000
    safe, _ = _safe_to_spend(1000000, 30000, 0, 200000, 20, True)
    assert safe == 770000


def test_is_investment_row():
    names = {"c-inv": ("투자", None), "c-card": ("카드대금", None)}
    assert _is_investment_row({"direction": "transfer", "category_id": "c-inv"}, names)
    assert _is_investment_row(
        {"direction": "transfer", "category_id": None, "parse_meta": {"route": "investment"}}, names
    )
    # a card-payment transfer is NOT an investment (its purchases are already expenses)
    assert not _is_investment_row({"direction": "transfer", "category_id": "c-card"}, names)
    assert not _is_investment_row({"direction": "expense", "category_id": "c-inv"}, names)
