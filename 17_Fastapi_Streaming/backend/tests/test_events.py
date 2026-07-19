"""API tests for productivity events and run creation."""

from fastapi.testclient import TestClient

from backend.database import reset_demo_data
from backend.main import app


def test_health_endpoint() -> None:
    """Health endpoint should return backend mode information."""

    with TestClient(app) as client:
        response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_trigger_event_creates_run() -> None:
    """Triggering an event should create an event and a run."""

    with TestClient(app) as client:
        reset_demo_data()
        sample = client.get("/api/sample-events").json()[0]
        response = client.post("/api/trigger", json=sample)

    assert response.status_code == 200
    payload = response.json()
    assert payload["event_id"].startswith("evt_")
    assert payload["run_id"].startswith("run_")
    assert payload["websocket_url"].startswith("/ws/runs/")
