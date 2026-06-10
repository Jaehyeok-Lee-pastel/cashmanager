"""Route-level integration: auth dependency overridden, repos mocked at the
boundary. Exercises router -> service -> repo wiring (the previously-uncovered HTTP layer)."""
import pytest
from fastapi.testclient import TestClient

from app.api.deps import CurrentUser, get_current_user
from app.main import app


@pytest.fixture
def client():
    app.dependency_overrides[get_current_user] = lambda: CurrentUser("u1")
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_create_transaction_returns_201(client, monkeypatch):
    monkeypatch.setattr("app.repositories.category_repo.get_category", lambda uid, cid: {"id": cid})
    monkeypatch.setattr(
        "app.repositories.tx_repo.create_transaction",
        lambda uid, f: {
            "id": "t1", "amount_minor": 8000, "direction": "expense", "category_id": "c1",
            "memo": "김밥", "occurred_on": "2026-06-01", "source": "manual", "created_at": "x",
        },
    )
    res = client.post("/transactions", json={
        "amount_minor": 8000, "category_id": "c1", "memo": "김밥", "occurred_on": "2026-06-01",
    })
    assert res.status_code == 201
    assert res.json()["amount_minor"] == 8000


def test_create_transaction_rejects_unowned_category(client, monkeypatch):
    monkeypatch.setattr("app.repositories.category_repo.get_category", lambda uid, cid: None)
    res = client.post("/transactions", json={"amount_minor": 5000, "category_id": "nope"})
    assert res.status_code == 400


def test_get_summary_computes(client, monkeypatch):
    monkeypatch.setattr("app.repositories.tx_repo.list_for_summary", lambda uid, s, e: [
        {"amount_minor": 10000, "direction": "expense", "category_id": "c1"},
        {"amount_minor": 5000, "direction": "income", "category_id": None},
    ])
    monkeypatch.setattr("app.repositories.category_repo.list_categories", lambda uid: [{"id": "c1", "name": "식비", "emoji": None}])
    monkeypatch.setattr("app.repositories.budget_repo.list_budgets", lambda uid: [])
    monkeypatch.setattr("app.repositories.recurring_repo.list_rules", lambda uid: [])
    res = client.get("/summary?month=2026-06")
    assert res.status_code == 200
    body = res.json()
    assert body["total_expense"] == 10000
    assert body["total_income"] == 5000


def test_summary_rejects_bad_month(client):
    assert client.get("/summary?month=2026-13").status_code == 422


def test_list_budgets(client, monkeypatch):
    monkeypatch.setattr("app.repositories.budget_repo.list_budgets", lambda uid: [{"category_id": "c1", "limit_minor": 300000}])
    res = client.get("/budgets")
    assert res.status_code == 200
    assert res.json()[0]["limit_minor"] == 300000


def test_recurring_list_and_create(client, monkeypatch):
    monkeypatch.setattr("app.repositories.recurring_repo.list_rules", lambda uid: [])
    assert client.get("/recurring").json() == []

    monkeypatch.setattr("app.repositories.category_repo.get_category", lambda uid, cid: {"id": cid})
    monkeypatch.setattr(
        "app.repositories.recurring_repo.create_rule",
        lambda uid, f: {
            "id": "r1", "category_id": "c1", "amount_minor": 500000,
            "direction": "expense", "day_of_month": 1, "memo": "월세", "active": True,
        },
    )
    res = client.post("/recurring", json={
        "amount_minor": 500000, "category_id": "c1", "day_of_month": 1, "memo": "월세", "direction": "expense",
    })
    assert res.status_code == 201
    assert res.json()["amount_minor"] == 500000


def test_requires_auth_without_override():
    # no override -> the real dependency rejects an unauthenticated request
    res = TestClient(app).get("/budgets")
    assert res.status_code in (401, 403)
