from datetime import datetime, timezone
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class DurableAuditEventType(StrEnum):
    """Durable local/demo audit event types for side-effect decisions."""

    SIDE_EFFECT_PLANNED = "side_effect_planned"
    APPROVAL_BINDING_CREATED = "approval_binding_created"
    APPROVAL_APPROVED = "approval_approved"
    APPROVAL_REJECTED = "approval_rejected"
    APPROVAL_EXPIRED = "approval_expired"
    EXECUTION_REQUESTED = "execution_requested"
    APPROVAL_AUTHORIZED = "approval_authorized"
    EXECUTION_STARTED = "execution_started"
    FAKE_CLIENT_CALLED = "fake_client_called"
    EXECUTION_SUCCEEDED = "execution_succeeded"
    EXECUTION_FAILED = "execution_failed"
    DUPLICATE_SUPPRESSED = "duplicate_suppressed"
    EXECUTION_BLOCKED = "execution_blocked"
    REMOTE_MARKER_CHECK_STARTED = "remote_marker_check_started"
    REMOTE_MARKER_FOUND = "remote_marker_found"
    REMOTE_MARKER_NOT_FOUND = "remote_marker_not_found"
    REMOTE_MARKER_AMBIGUOUS = "remote_marker_ambiguous"
    REMOTE_MARKER_MISMATCH = "remote_marker_mismatch"
    REMOTE_MARKER_LOOKUP_FAILED = "remote_marker_lookup_failed"
    REMOTE_RECONCILED = "remote_reconciled"


class DurableAuditEvent(BaseModel):
    """SQLite-backed durable audit event for local/demo side-effect evidence."""

    model_config = ConfigDict(extra="forbid")

    event_id: str
    run_id: str
    side_effect_id: str | None = None
    event_type: DurableAuditEventType
    actor_id: str | None = None
    message: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class DuplicateDurableAuditEventError(Exception):
    """Raised when a durable audit event_id already exists."""


class DurableAuditEventNotFoundError(Exception):
    """Raised when a requested durable audit event does not exist."""


class InvalidDurableAuditEventTypeError(Exception):
    """Raised when a durable audit event has an unsupported event type."""


class UnsafeDurableAuditMetadataError(Exception):
    """Raised when metadata contains known unsafe keys or token-like values."""


class InvalidDurableAuditMetadataError(Exception):
    """Raised when metadata cannot be safely serialized as JSON."""
