import pytest

from app.graph.service import HarnessGraphService, TaskNotFoundError, TaskNotPausedError
from app.identity.config import ADMIN_API_KEY, OPERATOR_API_KEY, VIEWER_API_KEY
from app.identity.resolver import resolve_identity_from_api_key
from app.state.schemas import TaskStatus


def test_service_starts_allowed_task() -> None:
    service = HarnessGraphService()
    viewer = resolve_identity_from_api_key(VIEWER_API_KEY)

    state = service.start_task(
        user_query="inspect sandbox issues",
        identity=viewer,
    )

    assert state["status"] == TaskStatus.COMPLETED
    assert state["tool_result"] is not None
    assert state["final_report"] is not None


def test_service_gets_existing_task() -> None:
    service = HarnessGraphService()
    viewer = resolve_identity_from_api_key(VIEWER_API_KEY)

    created = service.start_task(
        user_query="inspect sandbox issues",
        identity=viewer,
    )

    fetched = service.get_task(created["task_id"])

    assert fetched["task_id"] == created["task_id"]
    assert fetched["status"] == TaskStatus.COMPLETED


def test_service_raises_for_missing_task() -> None:
    service = HarnessGraphService()

    with pytest.raises(TaskNotFoundError):
        service.get_task("missing-task-id")


def test_service_approves_paused_task() -> None:
    service = HarnessGraphService()
    operator = resolve_identity_from_api_key(OPERATOR_API_KEY)
    admin = resolve_identity_from_api_key(ADMIN_API_KEY)

    paused = service.start_task(
        user_query="trigger workflow",
        identity=operator,
    )

    assert paused["status"] == TaskStatus.PAUSED_FOR_APPROVAL
    assert paused["tool_result"] is None

    approved = service.approve_task(
        task_id=paused["task_id"],
        approver=admin,
    )

    assert approved["status"] == TaskStatus.COMPLETED
    assert approved["tool_result"] is not None


def test_service_rejects_paused_task() -> None:
    service = HarnessGraphService()
    operator = resolve_identity_from_api_key(OPERATOR_API_KEY)
    admin = resolve_identity_from_api_key(ADMIN_API_KEY)

    paused = service.start_task(
        user_query="trigger workflow",
        identity=operator,
    )

    rejected = service.reject_task(
        task_id=paused["task_id"],
        rejector=admin,
    )

    assert rejected["status"] == TaskStatus.REJECTED
    assert rejected["tool_result"] is None


def test_service_rejects_approval_for_non_paused_task() -> None:
    service = HarnessGraphService()
    viewer = resolve_identity_from_api_key(VIEWER_API_KEY)
    admin = resolve_identity_from_api_key(ADMIN_API_KEY)

    completed = service.start_task(
        user_query="inspect sandbox issues",
        identity=viewer,
    )

    with pytest.raises(TaskNotPausedError):
        service.approve_task(
            task_id=completed["task_id"],
            approver=admin,
        )