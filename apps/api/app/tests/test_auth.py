from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_protected_endpoints_require_auth():
    """Every domain endpoint must reject requests without a bearer token (401)."""
    cases = [
        ("get", "/me"),
        ("get", "/categories"),
        ("post", "/categories"),
        ("get", "/transactions?month=2026-06"),
        ("post", "/transactions/parse"),
        ("get", "/summary?month=2026-06"),
        ("get", "/budgets"),
        ("get", "/budgets/suggestions"),
        ("get", "/insights?month=2026-06"),
        ("post", "/assistant/query"),
    ]
    for method, path in cases:
        res = getattr(client, method)(path) if method == "get" else getattr(client, method)(path, json={})
        assert res.status_code == 401, f"{method.upper()} {path} -> {res.status_code}"


def test_health_stays_public():
    assert client.get("/health").status_code == 200
