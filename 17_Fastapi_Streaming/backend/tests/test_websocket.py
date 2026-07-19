"""WebSocket tests for replaying assistant stream chunks."""

from fastapi.testclient import TestClient

from backend.database import append_chunk, create_event, create_run, reset_demo_data, update_run_status
from backend.main import app
from backend.mock_events import SAMPLE_EVENTS


def test_websocket_replays_existing_chunks() -> None:
    """A WebSocket client should receive persisted chunks for an existing run."""

    with TestClient(app) as client:
        reset_demo_data()
        event = create_event(SAMPLE_EVENTS[0])
        run = create_run(event["id"])
        append_chunk(run["id"], 1, "Hello ")
        append_chunk(run["id"], 2, "stream.")
        update_run_status(run["id"], "completed", final_output="Hello stream.")

        with client.websocket_connect(f"/ws/runs/{run['id']}") as websocket:
            status = websocket.receive_json()
            first_chunk = websocket.receive_json()
            second_chunk = websocket.receive_json()
            done = websocket.receive_json()

    assert status["type"] == "status"
    assert first_chunk["content"] == "Hello "
    assert second_chunk["content"] == "stream."
    assert done["type"] == "done"
