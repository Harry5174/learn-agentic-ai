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
    metadata: dict[str, Any] | None = None,
) -> AuditEvent:
    """Create a permission-checked audit event."""

    safe_metadata = {
        "decision": decision,
        "reason": reason,
        "required_scopes": list(required_scopes),
        "missing_scopes": list(missing_scopes),
    }
    if metadata is not None:
        safe_metadata.update(metadata)

    return create_audit_event(
        task_id=task_id,
        event_type=AuditEventType.PERMISSION_CHECKED,
        actor_id=actor_id,
        message="Permission check completed.",
        tool_name=tool_name,
        metadata=safe_metadata,
    )


def create_approval_requested_event(
    task_id: str,
    actor_id: str,
    tool_name: str,
    reason: str,
    metadata: dict[str, Any] | None = None,
) -> AuditEvent:
    """Create an approval-requested audit event."""

    safe_metadata = {"reason": reason}
    if metadata is not None:
        safe_metadata.update(metadata)

    return create_audit_event(
        task_id=task_id,
        event_type=AuditEventType.APPROVAL_REQUESTED,
        actor_id=actor_id,
        message="Approval was requested.",
        tool_name=tool_name,
        metadata=safe_metadata,
    )


def create_tool_executed_event(
    task_id: str,
    actor_id: str,
    tool_name: str,
    dry_run: bool,
    success: bool,
    metadata: dict[str, Any] | None = None,
) -> AuditEvent:
    """Create a tool-executed audit event."""

    safe_metadata = {
        "dry_run": dry_run,
        "success": success,
    }
    if metadata is not None:
        safe_metadata.update(metadata)

    return create_audit_event(
        task_id=task_id,
        event_type=AuditEventType.TOOL_EXECUTED,
        actor_id=actor_id,
        message="Tool execution completed.",
        tool_name=tool_name,
        metadata=safe_metadata,
    )


def create_approval_granted_event(
    task_id: str,
    actor_id: str,
    tool_name: str,
    reason: str,
    metadata: dict[str, Any] | None = None,
) -> AuditEvent:
    """Create an approval-granted audit event."""
    safe_metadata = {"reason": reason}
    if metadata is not None:
        safe_metadata.update(metadata)

    return create_audit_event(
        task_id=task_id,
        event_type=AuditEventType.APPROVAL_GRANTED,
        actor_id=actor_id,
        message="Approval was granted.",
        tool_name=tool_name,
        metadata=safe_metadata,
    )


def create_approval_rejected_event(
    task_id: str,
    actor_id: str,
    tool_name: str,
    reason: str,
    metadata: dict[str, Any] | None = None,
) -> AuditEvent:
    """Create an approval-rejected audit event."""
    safe_metadata = {"reason": reason}
    if metadata is not None:
        safe_metadata.update(metadata)

    return create_audit_event(
        task_id=task_id,
        event_type=AuditEventType.APPROVAL_REJECTED,
        actor_id=actor_id,
        message="Approval was rejected.",
        tool_name=tool_name,
        metadata=safe_metadata,
    )


def create_task_completed_event(
    task_id: str,
    actor_id: str,
) -> AuditEvent:
    """Create a task-completed audit event."""
    return create_audit_event(
        task_id=task_id,
        event_type=AuditEventType.TASK_COMPLETED,
        actor_id=actor_id,
        message="Task was completed.",
    )
