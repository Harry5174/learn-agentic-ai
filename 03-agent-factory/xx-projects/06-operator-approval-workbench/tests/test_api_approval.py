from fastapi.testclient import TestClient

from app.api.main import create_app
from app.identity.config import ADMIN_API_KEY, OPERATOR_API_KEY, VIEWER_API_KEY


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


def test_admin_can_approve_paused_trigger_task() -> None:
    client = TestClient(create_app())
    paused = _create_paused_trigger_task(client)

    response = client.post(
        f"/tasks/{paused['task_id']}/approve",
        headers={"X-API-Key": ADMIN_API_KEY},
        json={"reason": "Approved for dry-run execution."},
    )

    assert response.status_code == 200

    body = response.json()
    assert body["task_id"] == paused["task_id"]
    assert body["status"] == "completed"
    assert body["requires_approval"] is False
    assert body["final_report"]
    assert body["approval_request"] is None


def test_viewer_cannot_approve_paused_trigger_task() -> None:
    client = TestClient(create_app())
    paused = _create_paused_trigger_task(client)

    response = client.post(
        f"/tasks/{paused['task_id']}/approve",
        headers={"X-API-Key": VIEWER_API_KEY},
        json={"reason": "Viewer attempting approval."},
    )

    assert response.status_code == 200

    body = response.json()
    assert body["task_id"] == paused["task_id"]
    assert body["status"] == "failed"
    assert body["requires_approval"] is False
    assert "approval:approve" in body["error_message"]

    audit_response = client.get(f"/tasks/{paused['task_id']}/audit")
    event_types = [
        event["event_type"] for event in audit_response.json()["audit_trail"]
    ]
    assert "tool_executed" not in event_types


def test_operator_cannot_approve_paused_trigger_task() -> None:
    client = TestClient(create_app())
    paused = _create_paused_trigger_task(client)

    response = client.post(
        f"/tasks/{paused['task_id']}/approve",
        headers={"X-API-Key": OPERATOR_API_KEY},
        json={"reason": "Operator attempting approval."},
    )

    assert response.status_code == 200

    body = response.json()
    assert body["task_id"] == paused["task_id"]
    assert body["status"] == "failed"
    assert body["requires_approval"] is False
    assert "approval:approve" in body["error_message"]


def test_approving_non_paused_task_returns_409() -> None:
    client = TestClient(create_app())

    created_response = client.post(
        "/tasks",
        headers={"X-API-Key": VIEWER_API_KEY},
        json={"user_query": "inspect sandbox issues"},
    )

    assert created_response.status_code == 202
    task_id = created_response.json()["task_id"]

    response = client.post(
        f"/tasks/{task_id}/approve",
        headers={"X-API-Key": ADMIN_API_KEY},
        json={"reason": "Too late."},
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "Task is not paused for approval."


def test_approving_missing_task_returns_404() -> None:
    client = TestClient(create_app())

    response = client.post(
        "/tasks/not-found/approve",
        headers={"X-API-Key": ADMIN_API_KEY},
        json={"reason": "Missing."},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found."


def test_admin_can_reject_paused_trigger_task() -> None:
    client = TestClient(create_app())
    paused = _create_paused_trigger_task(client)

    response = client.post(
        f"/tasks/{paused['task_id']}/reject",
        headers={"X-API-Key": ADMIN_API_KEY},
        json={"reason": "Rejected during review."},
    )

    assert response.status_code == 200

    body = response.json()
    assert body["task_id"] == paused["task_id"]
    assert body["status"] == "rejected"
    assert body["requires_approval"] is False
    assert body["final_report"].startswith("Task rejected:")
    assert body["approval_request"] is None

    audit_response = client.get(f"/tasks/{paused['task_id']}/audit")
    event_types = [
        event["event_type"] for event in audit_response.json()["audit_trail"]
    ]
    assert "tool_executed" not in event_types


def test_rejecting_non_paused_task_returns_409() -> None:
    client = TestClient(create_app())

    created_response = client.post(
        "/tasks",
        headers={"X-API-Key": VIEWER_API_KEY},
        json={"user_query": "inspect sandbox issues"},
    )

    assert created_response.status_code == 202
    task_id = created_response.json()["task_id"]

    response = client.post(
        f"/tasks/{task_id}/reject",
        headers={"X-API-Key": ADMIN_API_KEY},
        json={"reason": "Too late."},
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "Task is not paused for approval."


def test_rejecting_missing_task_returns_404() -> None:
    client = TestClient(create_app())

    response = client.post(
        "/tasks/not-found/reject",
        headers={"X-API-Key": ADMIN_API_KEY},
        json={"reason": "Missing."},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found."
