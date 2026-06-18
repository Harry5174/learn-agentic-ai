from enum import StrEnum
from pydantic import BaseModel, ConfigDict


class DurableSideEffectStatus(StrEnum):
    """V1 Lifecycle state for a durable side-effect attempt."""
    PLANNED = "planned"
    APPROVED = "approved"
    EXECUTING = "executing"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    SKIPPED_DUPLICATE = "skipped_duplicate"
    REJECTED = "rejected"
    BLOCKED = "blocked"


class DurableSideEffectRecord(BaseModel):
    """Durable record for a side-effect attempt, persisted in SQLite."""

    model_config = ConfigDict(extra="forbid")

    side_effect_id: str
    run_id: str
    skill_id: str
    step_id: str
    tool_name: str
    validated_arguments_hash: str
    status: DurableSideEffectStatus
    
    repository: str | None = None
    issue_number: int | None = None
    comment_body_hash: str | None = None
    comment_body_preview: str | None = None
    
    created_at: str
    updated_at: str
    approved_at: str | None = None
    started_at: str | None = None
    executed_at: str | None = None
    skipped_at: str | None = None
    failed_at: str | None = None
    
    external_result_json: str | None = None
    failure_json: str | None = None


class DuplicateSideEffectRecordError(Exception):
    """Raised when attempting to create a record with an existing side_effect_id."""


class SideEffectRecordNotFoundError(Exception):
    """Raised when a requested side_effect_id does not exist in the ledger."""


class InvalidSideEffectStatusError(Exception):
    """Raised when an invalid status is provided."""


class InvalidSideEffectTransitionError(Exception):
    """Raised when attempting an illegal state transition."""


class TerminalSideEffectStateError(Exception):
    """Raised when attempting to mutate a record that is in a terminal state."""
