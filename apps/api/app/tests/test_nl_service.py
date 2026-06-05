from app.services import nl_service


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
