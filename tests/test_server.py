from fastapi.testclient import TestClient

from worldloop.server import app


def test_health():
    response = TestClient(app).get("/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["ok"] is True
    assert payload["cases"] >= 10
