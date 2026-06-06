from datetime import datetime, timezone
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class AuditEventType(StrEnum):
    """Types of audit events emitted by the harness."""

    TASK_CREATED = "task_created"
    IDENTITY_ATTACHED = "identity_attached"
    TOOL_SELECTED = "tool_selected"
    PERMISSION_CHECKED = "permission_checked"
    TOOL_ALLOWED = "tool_allowed"
    TOOL_DENIED = "tool_denied"
    APPROVAL_REQUESTED = "approval_requested"
    APPROVAL_GRANTED = "approval_granted"
    APPROVAL_REJECTED = "approval_rejected"
    TOOL_EXECUTED = "tool_executed"
    TASK_COMPLETED = "task_completed"
    TASK_FAILED = "task_failed"


class AuditEvent(BaseModel):
    """Structured audit event for important harness actions."""

    event_id: str
    task_id: str
    event_type: AuditEventType
    actor_id: str
    message: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    tool_name: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)