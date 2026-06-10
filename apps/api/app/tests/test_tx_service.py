from app.schemas.transaction import TransactionUpdate
from app.services import tx_service

_ROW = {
    "id": "t1", "amount_minor": 5500, "direction": "expense",
    "category_id": "c-food", "memo": "맥날", "occurred_on": "2026-06-01",
    "source": "nl_text", "created_at": "2026-06-01T00:00:00Z",
}


def test_update_category_relearns_merchant(monkeypatch):
    monkeypatch.setattr(
        "app.repositories.tx_repo.get_transaction",
        lambda uid, tid: {**_ROW, "category_id": "c-misc", "raw_input": "맥날 5500"},
    )
    monkeypatch.setattr(
        "app.repositories.category_repo.get_category", lambda uid, cid: {"id": cid}
    )
    monkeypatch.setattr(
        "app.repositories.tx_repo.update_transaction",
        lambda uid, tid, f: {**_ROW, "category_id": "c-food"},
    )
    captured = []
    monkeypatch.setattr(
        "app.repositories.merchant_map_repo.upsert",
        lambda uid, kw, cid: captured.append((kw, cid)),
    )
    tx_service.update_transaction("u", "t1", TransactionUpdate(category_id="c-food"))
    # "맥날 5500" -> merchant_keyword canonicalizes to "맥도날드", relearned to c-food
    assert captured == [("맥도날드", "c-food")]


def test_update_without_category_does_not_relearn(monkeypatch):
    monkeypatch.setattr(
        "app.repositories.tx_repo.get_transaction",
        lambda uid, tid: {**_ROW, "raw_input": "맥날 5500"},
    )
    monkeypatch.setattr(
        "app.repositories.tx_repo.update_transaction", lambda uid, tid, f: _ROW
    )
    captured = []
    monkeypatch.setattr(
        "app.repositories.merchant_map_repo.upsert",
        lambda uid, kw, cid: captured.append((kw, cid)),
    )
    tx_service.update_transaction("u", "t1", TransactionUpdate(memo="새 메모"))
    assert captured == []  # only a memo change -> no relearn
