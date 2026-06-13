from fastapi.testclient import TestClient

from app.api.main import create_app
from app.identity.config import OPERATOR_API_KEY, VIEWER_API_KEY


def test_viewer_can_create_inspect_task() -> None:
    client = TestClient(create_app())

    response = client.post(
        "/tasks",
        headers={"X-API-Key": VIEWER_API_KEY},
        json={"user_query": "inspect sandbox issues"},
    )

    assert response.status_code == 202

    body = response.json()
    assert body["task_id"]
    assert body["status"] == "completed"
    assert body["selected_tool_name"] == "inspect_sandbox_issues"
    assert body["final_report"]
    assert body["requires_approval"] is False
    assert body["approval_request"] is None


def test_viewer_draft_task_is_denied() -> None:
    client = TestClient(create_app())

    response = client.post(
        "/tasks",
        headers={"X-API-Key": VIEWER_API_KEY},
        json={"user_query": "draft issue comment"},
    )

    assert response.status_code == 202

    body = response.json()
    assert body["status"] == "denied"
    assert body["selected_tool_name"] == "draft_issue_comment"
    assert body["requires_approval"] is False
    assert body["approval_request"] is None


def test_unsupported_task_fails_safely() -> None:
    client = TestClient(create_app())

    response = client.post(
        "/tasks",
        headers={"X-API-Key": VIEWER_API_KEY},
        json={"user_query": "do something random"},
    )

    assert response.status_code == 202

    body = response.json()
    assert body["status"] == "failed"
    assert body["selected_tool_name"] is None
    assert body["error_message"]
    assert body["requires_approval"] is False


def test_operator_trigger_task_pauses_for_approval() -> None:
    client = TestClient(create_app())

    response = client.post(
        "/tasks",
        headers={"X-API-Key": OPERATOR_API_KEY},
        json={"user_query": "trigger workflow"},
    )

    assert response.status_code == 202

    body = response.json()
    assert body["status"] == "paused_for_approval"
    assert body["selected_tool_name"] == "trigger_workflow_dry_run"
    assert body["requires_approval"] is True

    approval_request = body["approval_request"]
    assert approval_request is not None
    assert approval_request["task_id"] == body["task_id"]
    assert approval_request["tool_name"] == "trigger_workflow_dry_run"
    assert approval_request["reason"]
    assert approval_request["requested_by"] == "demo_operator"


def test_created_task_can_be_fetched() -> None:
    client = TestClient(create_app())

    created_response = client.post(
        "/tasks",
        headers={"X-API-Key": VIEWER_API_KEY},
        json={"user_query": "inspect sandbox issues"},
    )

    assert created_response.status_code == 202

    created = created_response.json()
    fetched_response = client.get(f"/tasks/{created['task_id']}")

    assert fetched_response.status_code == 200

    fetched = fetched_response.json()
    assert fetched["task_id"] == created["task_id"]
    assert fetched["status"] == created["status"]


def test_missing_task_returns_404() -> None:
    client = TestClient(create_app())

    response = client.get("/tasks/not-found")

    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found."


def test_missing_api_key_for_create_task_returns_401() -> None:
    client = TestClient(create_app())

    response = client.post(
        "/tasks",
        json={"user_query": "inspect sandbox issues"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Missing X-API-Key header."


def test_invalid_api_key_for_create_task_returns_401() -> None:
    client = TestClient(create_app())

    response = client.post(
        "/tasks",
        headers={"X-API-Key": "not-a-real-key"},
        json={"user_query": "inspect sandbox issues"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid API key."


def test_request_body_cannot_override_identity_for_task_creation() -> None:
    client = TestClient(create_app())

    response = client.post(
        "/tasks",
        headers={"X-API-Key": VIEWER_API_KEY},
        json={
            "user_query": "draft issue comment",
            "user_id": "fake_admin",
            "role": "admin",
            "scopes": ["approval:approve", "tools:trigger_workflow"],
        },
    )

    assert response.status_code == 202

    body = response.json()
    assert body["status"] == "denied"
    assert body["selected_tool_name"] == "draft_issue_comment"
