import pytest

from app.services import nl_service


@pytest.mark.parametrize("text", ["알바비 500000", "과외비 300000", "보너스 1000000", "이자 5000"])
def test_income_keywords_block_expense_fastpath(text):
    # income-looking lines must NOT be silently fast-pathed as an expense
    amount = int("".join(c for c in text if c.isdigit()))
    assert nl_service._can_fast_path(text, amount) is False


def test_pure_number_still_fast_paths():
    assert nl_service._can_fast_path("500000", 500000) is True


def test_card_payment_parsed_as_transfer(monkeypatch):
    monkeypatch.setattr(
        "app.repositories.category_repo.list_categories",
        lambda uid: [{"id": "c-card", "name": "카드대금"}],
    )
    res = nl_service.parse("u", "카드대금 1200000")
    assert res.direction == "transfer"
    assert res.amount_minor == 1200000
    assert res.category_id == "c-card"
    assert res.needs_manual is False


def test_investment_parsed_as_transfer(monkeypatch):
    monkeypatch.setattr(
        "app.repositories.category_repo.list_categories",
        lambda uid: [{"id": "c-inv", "name": "투자"}],
    )
    res = nl_service.parse("u", "주식 50만 샀어")
    assert res.direction == "transfer"
    assert res.amount_minor == 500000
    assert res.category_id == "c-inv"
    assert res.parse_meta["route"] == "investment"


def test_card_payment_without_card_category(monkeypatch):
    # no 카드대금 category exists -> still a transfer, just uncategorized
    monkeypatch.setattr(
        "app.repositories.category_repo.list_categories",
        lambda uid: [{"id": "c-food", "name": "식비"}],
    )
    res = nl_service.parse("u", "신용카드 결제 50만원")
    assert res.direction == "transfer"
    assert res.amount_minor == 500000
    assert res.category_id is None
