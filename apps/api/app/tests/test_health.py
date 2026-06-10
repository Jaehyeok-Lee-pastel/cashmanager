from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_ok():
    res = client.get("/health")
    assert res.status_code == 200
    body = res.json()
    assert body["ok"] is True
    assert "service" in body


class _FakeQuery:
    def select(self, *a, **k):
        return self

    def limit(self, *a, **k):
        return self

    def execute(self):
        return None


def test_ready_ok_when_db_reachable(monkeypatch):
    monkeypatch.setattr(
        "app.api.routes.health.get_supabase",
        lambda: type("C", (), {"table": lambda self, *a, **k: _FakeQuery()})(),
    )
    res = client.get("/ready")
    assert res.status_code == 200
    assert res.json()["ready"] is True


def test_ready_503_when_db_down(monkeypatch):
    def boom():
        raise RuntimeError("db down")

    monkeypatch.setattr("app.api.routes.health.get_supabase", boom)
    res = client.get("/ready")
    assert res.status_code == 503
    assert res.json()["ready"] is False
