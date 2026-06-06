from typing import Any
from uuid import uuid4

from app.audit.schemas import AuditEvent, AuditEventType


def create_audit_event(
    *,
    task_id: str,
    event_type: AuditEventType,
    actor_id: str,
    message: str,
    tool_name: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> AuditEvent:
    """Create a structured audit event.

    Timestamps are provided by the AuditEvent schema default factory.
    Metadata is copied defensively to avoid caller mutation leaks.
    """

    safe_metadata = dict(metadata) if metadata is not None else {}

    return AuditEvent(
        event_id=str(uuid4()),
        task_id=task_id,
        event_type=event_type,
        actor_id=actor_id,
        message=message,
        tool_name=tool_name,
        metadata=safe_metadata,
    )


def append_audit_event(
    audit_trail: list[AuditEvent],
    event: AuditEvent,
) -> list[AuditEvent]:
    """Return a new audit trail with the event appended.

    The original audit trail is not mutated.
    """

    return [*audit_trail, event]


def create_task_created_event(
    task_id: str,
    actor_id: str,
    user_query: str,
) -> AuditEvent:
    """Create a task-created audit event."""

    return create_audit_event(
        task_id=task_id,
        event_type=AuditEventType.TASK_CREATED,
        actor_id=actor_id,
        message="Task was created.",
        metadata={"user_query": user_query},
    )


def create_tool_selected_event(
    task_id: str,
    actor_id: str,
    tool_name: str,
    reason: str,
) -> AuditEvent:
    """Create a tool-selected audit event."""

    return create_audit_event(
        task_id=task_id,
        event_type=AuditEventType.TOOL_SELECTED,
        actor_id=actor_id,
        message="Tool was selected.",
        tool_name=tool_name,
        metadata={"reason": reason},
    )


def create_permission_checked_event(
    task_id: str,
    actor_id: str,
    tool_name: str,
    decision: str,
    reason: str,
    required_scopes: list[str],
    missing_scopes: list[str],
) -> AuditEvent:
    """Create a permission-checked audit event."""

    return create_audit_event(
        task_id=task_id,
        event_type=AuditEventType.PERMISSION_CHECKED,
        actor_id=actor_id,
        message="Permission check completed.",
        tool_name=tool_name,
        metadata={
            "decision": decision,
            "reason": reason,
            "required_scopes": list(required_scopes),
            "missing_scopes": list(missing_scopes),
        },
    )


def create_approval_requested_event(
    task_id: str,
    actor_id: str,
    tool_name: str,
    reason: str,
) -> AuditEvent:
    """Create an approval-requested audit event."""

    return create_audit_event(
        task_id=task_id,
        event_type=AuditEventType.APPROVAL_REQUESTED,
        actor_id=actor_id,
        message="Approval was requested.",
        tool_name=tool_name,
        metadata={"reason": reason},
    )


def create_tool_executed_event(
    task_id: str,
    actor_id: str,
    tool_name: str,
    dry_run: bool,
    success: bool,
) -> AuditEvent:
    """Create a tool-executed audit event."""

    return create_audit_event(
        task_id=task_id,
        event_type=AuditEventType.TOOL_EXECUTED,
        actor_id=actor_id,
        message="Tool execution completed.",
        tool_name=tool_name,
        metadata={
            "dry_run": dry_run,
            "success": success,
        },
    )