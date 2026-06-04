"""Service-layer ownership checks (service_role bypasses RLS, so the API must verify)."""

import pytest
from fastapi import HTTPException

from app.schemas.transaction import TransactionCreate, TransactionUpdate
from app.services import tx_service


def test_create_rejects_unowned_category(monkeypatch):
    # Category lookup scoped to the user returns nothing -> not owned.
    monkeypatch.setattr(
        "app.repositories.category_repo.get_category", lambda uid, cid: None
    )
    payload = TransactionCreate(amount_minor=4900, category_id="other-users-cat")
    with pytest.raises(HTTPException) as exc:
        tx_service.create_transaction("user-1", payload)
    assert exc.value.status_code == 400


def test_update_rejects_unowned_transaction(monkeypatch):
    # Transaction lookup scoped to the user returns nothing -> 404, no write.
    monkeypatch.setattr(
        "app.repositories.tx_repo.get_transaction", lambda uid, tid: None
    )
    with pytest.raises(HTTPException) as exc:
        tx_service.update_transaction("user-1", "tx-x", TransactionUpdate(memo="x"))
    assert exc.value.status_code == 404


def test_delete_rejects_unowned_transaction(monkeypatch):
    monkeypatch.setattr(
        "app.repositories.tx_repo.get_transaction", lambda uid, tid: None
    )
    with pytest.raises(HTTPException) as exc:
        tx_service.delete_transaction("user-1", "tx-x")
    assert exc.value.status_code == 404


def test_create_passes_user_id_to_repo(monkeypatch):
    captured = {}

    def fake_create(user_id, fields):
        captured["user_id"] = user_id
        return {
            "id": "tx-1",
            "amount_minor": fields["amount_minor"],
            "direction": fields["direction"],
            "category_id": None,
            "memo": fields.get("memo"),
            "occurred_on": fields["occurred_on"],
            "source": fields["source"],
            "created_at": "2026-06-02T00:00:00+00:00",
        }

    monkeypatch.setattr("app.repositories.tx_repo.create_transaction", fake_create)
    out = tx_service.create_transaction("user-42", TransactionCreate(amount_minor=4900))
    assert captured["user_id"] == "user-42"
    assert out.amount_minor == 4900
