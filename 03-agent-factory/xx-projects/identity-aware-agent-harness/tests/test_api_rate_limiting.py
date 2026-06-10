from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.api import dependencies as api_dependencies
from app.api import routes_tasks
from app.api.main import create_app
from app.api.rate_limiter import InMemoryRateLimiter, RateLimitExceeded
from app.identity.config import ADMIN_API_KEY, OPERATOR_API_KEY, VIEWER_API_KEY
from app.state.schemas import TaskStatus


class FakeClock:
    def __init__(self) -> None:
        self.now = 0.0

    def __call__(self) -> float:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += seconds


class FakeTaskService:
    def __init__(self) -> None:
        self.started_tasks = 0
        self.approved_tasks = 0
        self.rejected_tasks = 0

    def start_task(self, user_query, identity):
        self.started_tasks += 1
        return {
            "task_id": f"task-{self.started_tasks}",
            "user_query": user_query,
            "identity": identity,
            "audit_trail": [],
            "status": TaskStatus.COMPLETED,
            "selected_tool_name": "inspect_sandbox_issues",
            "final_report": "Task completed successfully.",
            "error_message": None,
        }

    def approve_task(self, task_id, approver, reason="Approved via API."):
        self.approved_tasks += 1
        return {
            "task_id": task_id,
            "user_query": "trigger workflow",
            "identity": approver,
            "audit_trail": [],
            "status": TaskStatus.COMPLETED,
            "selected_tool_name": "trigger_workflow_dry_run",
            "final_report": reason,
            "error_message": None,
        }

    def reject_task(self, task_id, rejector, reason="Rejected via API."):
        self.rejected_tasks += 1
        return {
            "task_id": task_id,
            "user_query": "trigger workflow",
            "identity": rejector,
            "audit_trail": [],
            "status": TaskStatus.REJECTED,
            "selected_tool_name": "trigger_workflow_dry_run",
            "final_report": reason,
            "error_message": None,
        }


def test_rate_limiter_allows_requests_under_limit() -> None:
    limiter = InMemoryRateLimiter(time_provider=FakeClock())

    limiter.check(key="demo-viewer-key:tasks", limit=2, window_seconds=60)
    limiter.check(key="demo-viewer-key:tasks", limit=2, window_seconds=60)


def test_rate_limiter_blocks_requests_over_limit() -> None:
    limiter = InMemoryRateLimiter(time_provider=FakeClock())

    limiter.check(key="demo-viewer-key:tasks", limit=1, window_seconds=60)

    with pytest.raises(RateLimitExceeded):
        limiter.check(key="demo-viewer-key:tasks", limit=1, window_seconds=60)


def test_rate_limiter_resets_after_window() -> None:
    clock = FakeClock()
    limiter = InMemoryRateLimiter(time_provider=clock)

    limiter.check(key="demo-viewer-key:tasks", limit=1, window_seconds=60)

    with pytest.raises(RateLimitExceeded):
        limiter.check(key="demo-viewer-key:tasks", limit=1, window_seconds=60)

    clock.advance(60)
    limiter.check(key="demo-viewer-key:tasks", limit=1, window_seconds=60)


def test_rate_limiter_separates_keys() -> None:
    limiter = InMemoryRateLimiter(time_provider=FakeClock())

    limiter.check(key="demo-viewer-key:tasks", limit=1, window_seconds=60)
    limiter.check(key="demo-admin-key:tasks", limit=1, window_seconds=60)


def test_rate_limiter_separates_route_groups() -> None:
    limiter = InMemoryRateLimiter(time_provider=FakeClock())

    limiter.check(key="demo-viewer-key:task_create", limit=1, window_seconds=60)
    limiter.check(key="demo-viewer-key:approval_action", limit=1, window_seconds=60)


def test_repeated_task_creation_over_limit_returns_429(monkeypatch) -> None:
    fake_service = FakeTaskService()
    monkeypatch.setattr(routes_tasks, "_task_service", fake_service)
    monkeypatch.setattr(api_dependencies, "TASK_CREATE_RATE_LIMIT", 2)
    client = TestClient(create_app())

    for _ in range(2):
        response = client.post(
            "/tasks",
            headers={"X-API-Key": VIEWER_API_KEY},
            json={"user_query": "inspect sandbox issues"},
        )
        assert response.status_code == 202

    response = client.post(
        "/tasks",
        headers={"X-API-Key": VIEWER_API_KEY},
        json={"user_query": "inspect sandbox issues"},
    )

    assert response.status_code == 429
    assert response.json()["detail"] == "Rate limit exceeded."
    assert fake_service.started_tasks == 2


def test_task_rate_limit_keys_are_independent_by_api_key(monkeypatch) -> None:
    fake_service = FakeTaskService()
    monkeypatch.setattr(routes_tasks, "_task_service", fake_service)
    monkeypatch.setattr(api_dependencies, "TASK_CREATE_RATE_LIMIT", 1)
    client = TestClient(create_app())

    first_viewer_response = client.post(
        "/tasks",
        headers={"X-API-Key": VIEWER_API_KEY},
        json={"user_query": "inspect sandbox issues"},
    )
    second_viewer_response = client.post(
        "/tasks",
        headers={"X-API-Key": VIEWER_API_KEY},
        json={"user_query": "inspect sandbox issues"},
    )
    operator_response = client.post(
        "/tasks",
        headers={"X-API-Key": OPERATOR_API_KEY},
        json={"user_query": "inspect sandbox issues"},
    )

    assert first_viewer_response.status_code == 202
    assert second_viewer_response.status_code == 429
    assert operator_response.status_code == 202
    assert fake_service.started_tasks == 2


def test_invalid_api_key_returns_401_before_rate_limit(monkeypatch) -> None:
    monkeypatch.setattr(api_dependencies, "TASK_CREATE_RATE_LIMIT", 0)
    client = TestClient(create_app())

    response = client.post(
        "/tasks",
        headers={"X-API-Key": "not-a-real-key"},
        json={"user_query": "inspect sandbox issues"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid API key."


def test_missing_api_key_returns_401_before_rate_limit(monkeypatch) -> None:
    monkeypatch.setattr(api_dependencies, "TASK_CREATE_RATE_LIMIT", 0)
    client = TestClient(create_app())

    response = client.post(
        "/tasks",
        json={"user_query": "inspect sandbox issues"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Missing X-API-Key header."


def test_approval_endpoint_is_rate_limited(monkeypatch) -> None:
    fake_service = FakeTaskService()
    monkeypatch.setattr(routes_tasks, "_task_service", fake_service)
    monkeypatch.setattr(api_dependencies, "APPROVAL_ACTION_RATE_LIMIT", 1)
    client = TestClient(create_app())

    first_response = client.post(
        "/tasks/task-1/approve",
        headers={"X-API-Key": ADMIN_API_KEY},
        json={"reason": "Approved."},
    )
    second_response = client.post(
        "/tasks/task-2/approve",
        headers={"X-API-Key": ADMIN_API_KEY},
        json={"reason": "Approved."},
    )

    assert first_response.status_code == 200
    assert second_response.status_code == 429
    assert fake_service.approved_tasks == 1


def test_rejection_endpoint_is_rate_limited(monkeypatch) -> None:
    fake_service = FakeTaskService()
    monkeypatch.setattr(routes_tasks, "_task_service", fake_service)
    monkeypatch.setattr(api_dependencies, "APPROVAL_ACTION_RATE_LIMIT", 1)
    client = TestClient(create_app())

    first_response = client.post(
        "/tasks/task-1/reject",
        headers={"X-API-Key": ADMIN_API_KEY},
        json={"reason": "Rejected."},
    )
    second_response = client.post(
        "/tasks/task-2/reject",
        headers={"X-API-Key": ADMIN_API_KEY},
        json={"reason": "Rejected."},
    )

    assert first_response.status_code == 200
    assert second_response.status_code == 429
    assert fake_service.rejected_tasks == 1


def test_sprint_8_does_not_add_forbidden_dependencies() -> None:
    project_config = Path("pyproject.toml").read_text()

    forbidden_terms = [
        "redis",
        "pyjwt",
        "python-jose",
        "openai",
        "langchain-openai",
    ]

    assert not any(term in project_config.lower() for term in forbidden_terms)
