from datetime import datetime

from app.audit.logger import (
    append_audit_event,
    create_approval_requested_event,
    create_audit_event,
    create_permission_checked_event,
    create_task_created_event,
    create_tool_executed_event,
    create_tool_selected_event,
)
from app.audit.schemas import AuditEvent, AuditEventType
from pathlib import Path

def _event(message: str = "Test event.") -> AuditEvent:
    return create_audit_event(
        task_id="task-123",
        event_type=AuditEventType.TASK_CREATED,
        actor_id="user-123",
        message=message,
    )


def test_create_audit_event_returns_audit_event() -> None:
    event = create_audit_event(
        task_id="task-123",
        event_type=AuditEventType.TASK_CREATED,
        actor_id="user-123",
        message="Task was created.",
    )

    assert isinstance(event, AuditEvent)
    assert event.task_id == "task-123"
    assert event.event_type == AuditEventType.TASK_CREATED
    assert event.actor_id == "user-123"
    assert event.message == "Task was created."


def test_create_audit_event_generates_fresh_event_ids() -> None:
    first = _event()
    second = _event()

    assert first.event_id
    assert second.event_id
    assert first.event_id != second.event_id


def test_create_audit_event_uses_timezone_aware_timestamp() -> None:
    event = _event()

    assert isinstance(event.timestamp, datetime)
    assert event.timestamp.tzinfo is not None
    assert event.timestamp.utcoffset() is not None


def test_create_audit_event_uses_safe_metadata_default() -> None:
    first = _event()
    second = _event()

    first.metadata["key"] = "value"

    assert first.metadata == {"key": "value"}
    assert second.metadata == {}


def test_create_audit_event_defensively_copies_metadata() -> None:
    metadata = {"key": "value"}

    event = create_audit_event(
        task_id="task-123",
        event_type=AuditEventType.TASK_CREATED,
        actor_id="user-123",
        message="Task was created.",
        metadata=metadata,
    )

    metadata["key"] = "changed"

    assert event.metadata == {"key": "value"}


def test_append_audit_event_returns_new_list() -> None:
    original = [_event("Original event.")]
    new_event = _event("New event.")

    updated = append_audit_event(original, new_event)

    assert updated is not original


def test_append_audit_event_does_not_mutate_original_list() -> None:
    original = [_event("Original event.")]
    new_event = _event("New event.")

    updated = append_audit_event(original, new_event)

    assert len(original) == 1
    assert len(updated) == 2


def test_append_audit_event_preserves_existing_events() -> None:
    existing = _event("Existing event.")
    new_event = _event("New event.")

    updated = append_audit_event([existing], new_event)

    assert updated[0] == existing


def test_append_audit_event_adds_new_event() -> None:
    original = [_event("Original event.")]
    new_event = _event("New event.")

    updated = append_audit_event(original, new_event)

    assert updated[-1] == new_event


def test_create_task_created_event() -> None:
    event = create_task_created_event(
        task_id="task-123",
        actor_id="user-123",
        user_query="Inspect sandbox issues.",
    )

    assert event.event_type == AuditEventType.TASK_CREATED
    assert event.metadata["user_query"] == "Inspect sandbox issues."


def test_create_tool_selected_event() -> None:
    event = create_tool_selected_event(
        task_id="task-123",
        actor_id="user-123",
        tool_name="inspect_sandbox_issues",
        reason="Best tool for issue inspection.",
    )

    assert event.event_type == AuditEventType.TOOL_SELECTED
    assert event.tool_name == "inspect_sandbox_issues"
    assert event.metadata["reason"] == "Best tool for issue inspection."


def test_create_permission_checked_event() -> None:
    event = create_permission_checked_event(
        task_id="task-123",
        actor_id="user-123",
        tool_name="draft_issue_comment",
        decision="deny",
        reason="Missing required scope.",
        required_scopes=["tools:draft"],
        missing_scopes=["tools:draft"],
    )

    assert event.event_type == AuditEventType.PERMISSION_CHECKED
    assert event.tool_name == "draft_issue_comment"
    assert event.metadata["decision"] == "deny"
    assert event.metadata["reason"] == "Missing required scope."
    assert event.metadata["required_scopes"] == ["tools:draft"]
    assert event.metadata["missing_scopes"] == ["tools:draft"]


def test_create_permission_checked_event_copies_scope_lists() -> None:
    required_scopes = ["tools:draft"]
    missing_scopes = ["tools:draft"]

    event = create_permission_checked_event(
        task_id="task-123",
        actor_id="user-123",
        tool_name="draft_issue_comment",
        decision="deny",
        reason="Missing required scope.",
        required_scopes=required_scopes,
        missing_scopes=missing_scopes,
    )

    required_scopes.append("mutated:required")
    missing_scopes.append("mutated:missing")

    assert event.metadata["required_scopes"] == ["tools:draft"]
    assert event.metadata["missing_scopes"] == ["tools:draft"]


def test_create_approval_requested_event() -> None:
    event = create_approval_requested_event(
        task_id="task-123",
        actor_id="operator-123",
        tool_name="trigger_workflow_dry_run",
        reason="High-risk tool requires approval.",
    )

    assert event.event_type == AuditEventType.APPROVAL_REQUESTED
    assert event.tool_name == "trigger_workflow_dry_run"
    assert event.metadata["reason"] == "High-risk tool requires approval."


def test_create_tool_executed_event() -> None:
    event = create_tool_executed_event(
        task_id="task-123",
        actor_id="system",
        tool_name="inspect_sandbox_issues",
        dry_run=True,
        success=True,
    )

    assert event.event_type == AuditEventType.TOOL_EXECUTED
    assert event.tool_name == "inspect_sandbox_issues"
    assert event.metadata["dry_run"] is True
    assert event.metadata["success"] is True


def test_audit_logger_does_not_import_fastapi_or_langgraph() -> None:
    import app.audit.logger as logger

    module_names = set(logger.__dict__)

    assert "FastAPI" not in module_names
    assert "langgraph" not in module_names


def test_audit_logger_does_not_persist_to_database() -> None:
    source = Path("src/app/audit/logger.py").read_text()

    forbidden_terms = [
        "sqlite",
        "postgres",
        "database",
        "Session",
        "engine",
        "commit(",
        "execute(",
    ]

    assert not any(term in source for term in forbidden_terms)