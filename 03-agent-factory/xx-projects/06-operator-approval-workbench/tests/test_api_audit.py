from fastapi.testclient import TestClient

from app.api.main import create_app
from app.identity.config import ADMIN_API_KEY, OPERATOR_API_KEY


def _create_paused_trigger_task(client: TestClient) -> dict:
    response = client.post(
        "/tasks",
        headers={"X-API-Key": OPERATOR_API_KEY},
        json={"user_query": "trigger workflow"},
    )

    assert response.status_code == 202

    body = response.json()
    assert body["status"] == "paused_for_approval"
    return body


def test_audit_endpoint_returns_approved_path_events() -> None:
    client = TestClient(create_app())
    paused = _create_paused_trigger_task(client)

    approve_response = client.post(
        f"/tasks/{paused['task_id']}/approve",
        headers={"X-API-Key": ADMIN_API_KEY},
        json={"reason": "Approved for dry-run execution."},
    )

    assert approve_response.status_code == 200

    response = client.get(f"/tasks/{paused['task_id']}/audit")

    assert response.status_code == 200

    body = response.json()
    assert body["task_id"] == paused["task_id"]

    event_types = [event["event_type"] for event in body["audit_trail"]]
    assert "approval_requested" in event_types
    assert "approval_granted" in event_types
    assert "tool_executed" in event_types
    assert "task_completed" in event_types


def test_audit_endpoint_returns_rejected_path_events_without_execution() -> None:
    client = TestClient(create_app())
    paused = _create_paused_trigger_task(client)

    reject_response = client.post(
        f"/tasks/{paused['task_id']}/reject",
        headers={"X-API-Key": ADMIN_API_KEY},
        json={"reason": "Rejected during review."},
    )

    assert reject_response.status_code == 200

    response = client.get(f"/tasks/{paused['task_id']}/audit")

    assert response.status_code == 200

    body = response.json()
    assert body["task_id"] == paused["task_id"]

    event_types = [event["event_type"] for event in body["audit_trail"]]
    assert "approval_requested" in event_types
    assert "approval_rejected" in event_types
    assert "tool_executed" not in event_types


def test_audit_endpoint_missing_task_returns_404() -> None:
    client = TestClient(create_app())

    response = client.get("/tasks/not-found/audit")

    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found."
