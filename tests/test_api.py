from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_and_list_monitor() -> None:
    response = client.post("/monitors", json={"name": "Example", "url": "https://example.com"})
    assert response.status_code == 201
    monitor_id = response.json()["id"]

    listed = client.get("/monitors")
    assert listed.status_code == 200
    assert any(item["id"] == monitor_id for item in listed.json())
