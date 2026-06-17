from datetime import datetime

from app.audit.schemas import AuditEvent, AuditEventType


def test_valid_audit_event_creates_successfully() -> None:
    event = AuditEvent(
        event_id="event-123",
        task_id="task-123",
        event_type=AuditEventType.TASK_CREATED,
        actor_id="user-123",
        message="Task was created.",
    )

    assert event.event_id == "event-123"
    assert event.event_type == AuditEventType.TASK_CREATED
    assert event.tool_name is None


def test_timestamp_exists() -> None:
    event = AuditEvent(
        event_id="event-123",
        task_id="task-123",
        event_type=AuditEventType.TASK_CREATED,
        actor_id="user-123",
        message="Task was created.",
    )

    assert isinstance(event.timestamp, datetime)


def test_timestamp_is_timezone_aware() -> None:
    event = AuditEvent(
        event_id="event-123",
        task_id="task-123",
        event_type=AuditEventType.TASK_CREATED,
        actor_id="user-123",
        message="Task was created.",
    )

    assert event.timestamp.tzinfo is not None
    assert event.timestamp.utcoffset() is not None


def test_metadata_default_is_not_shared() -> None:
    first = AuditEvent(
        event_id="event-1",
        task_id="task-1",
        event_type=AuditEventType.TASK_CREATED,
        actor_id="user-1",
        message="First event.",
    )
    second = AuditEvent(
        event_id="event-2",
        task_id="task-2",
        event_type=AuditEventType.TASK_CREATED,
        actor_id="user-2",
        message="Second event.",
    )

    first.metadata["key"] = "value"

    assert first.metadata == {"key": "value"}
    assert second.metadata == {}