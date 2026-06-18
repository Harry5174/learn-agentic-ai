"""Durable approval binding schemas for A4.2.

ApprovalBindingStatus is deliberately separate from DurableSideEffectStatus
and from the existing graph-level ApprovalStatus. They are three distinct
state machines:

- DurableSideEffectStatus: lifecycle of a side-effect record in SQLite
- ApprovalStatus: in-memory graph-level approval decision
- ApprovalBindingStatus: durable approval binding lifecycle in SQLite
"""

from enum import StrEnum

from pydantic import BaseModel, ConfigDict


class ApprovalBindingStatus(StrEnum):
    """Durable approval binding lifecycle state.

    Separate from DurableSideEffectStatus and graph-level ApprovalStatus.
    """

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"


class ApprovalBindingRecord(BaseModel):
    """Durable record for an approval binding, persisted in SQLite."""

    model_config = ConfigDict(extra="forbid")

    approval_id: str
    run_id: str
    skill_id: str
    step_id: str
    tool_name: str
    side_effect_id: str
    validated_arguments_hash: str
    approval_status: ApprovalBindingStatus
    requested_by: str | None = None
    decided_by: str | None = None
    reason: str | None = None
    created_at: str
    decided_at: str | None = None
    expires_at: str | None = None


# --- Domain Errors ---


class DuplicateApprovalBindingError(Exception):
    """Raised when attempting to create a binding with an existing approval_id
    or for a side_effect_id that already has a binding."""


class ApprovalBindingNotFoundError(Exception):
    """Raised when a requested approval binding does not exist."""


class SideEffectForApprovalNotFoundError(Exception):
    """Raised when the referenced side_effect_id does not exist in the ledger."""


class ApprovalSideEffectMismatchError(Exception):
    """Raised when approval binding fields do not match the side-effect record."""


class InvalidApprovalStatusError(Exception):
    """Raised when an invalid approval status is provided."""


class InvalidApprovalTransitionError(Exception):
    """Raised when attempting an illegal approval status transition."""


class TerminalApprovalStateError(Exception):
    """Raised when attempting to mutate a binding that is in a terminal state."""


class SideEffectNotApprovableError(Exception):
    """Raised when attempting to create an approval for a side effect
    that is not in the planned state."""


class ApprovalNotAuthorizedError(Exception):
    """Raised when assert_approved_for_action fails because the binding
    is not approved or the validated_arguments_hash does not match."""
