from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.identity.schemas import Role
from app.tools.schemas import RiskLevel


class OperatorExecutionModeResponse(BaseModel):
    """Public execution-mode summary for operator review."""

    model_config = ConfigDict(extra="forbid")

    mode: str = "fake_default"
    real_github_enabled: bool = False
    token_required: bool = False


class OperatorApprovalTargetResponse(BaseModel):
    """Repository/issue target when available for an approval row."""

    model_config = ConfigDict(extra="forbid")

    repository: str | None = None
    issue_number: int | None = None


class OperatorAuditEventReferenceResponse(BaseModel):
    """Small read-only audit event reference for approval detail."""

    model_config = ConfigDict(extra="forbid")

    event_id: str
    event_type: str
    timestamp: datetime
    message: str


class OperatorAuditTimelineEventResponse(BaseModel):
    """Read-only local/demo audit timeline event for operator visibility."""

    model_config = ConfigDict(extra="forbid")

    sequence: int
    event_id: str
    event_type: str
    actor_id: str | None = None
    timestamp: datetime
    tool_name: str | None = None
    message: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class OperatorDecisionHistoryItemResponse(BaseModel):
    """Read-only operator decision history item derived from audit/state."""

    model_config = ConfigDict(extra="forbid")

    decision: str
    actor_id: str | None = None
    actor_role: Role | None = None
    reason: str | None = None
    timestamp: datetime | None = None
    event_id: str | None = None


class OperatorExecutionStepResultResponse(BaseModel):
    """Safe summary of one local/demo tool execution result."""

    model_config = ConfigDict(extra="forbid")

    tool_name: str
    success: bool
    dry_run: bool
    message: str | None = None
    result_summary: dict[str, Any] = Field(default_factory=dict)


class OperatorExecutionResultResponse(BaseModel):
    """Safe local/demo execution result summary."""

    model_config = ConfigDict(extra="forbid")

    attempted_step_count: int = 0
    completed_step_count: int = 0
    tool_names: list[str] = Field(default_factory=list)
    dry_run: bool = True
    final_report: str | None = None
    error_message: str | None = None
    step_results: list[OperatorExecutionStepResultResponse] = Field(
        default_factory=list
    )


class OperatorApprovalDecision(StrEnum):
    """Operator decision values for explicit workbench actions."""

    APPROVE = "approve"
    REJECT = "reject"


class OperatorApprovalDecisionRequest(BaseModel):
    """Strict request body for operator approval decisions."""

    model_config = ConfigDict(extra="forbid")

    decision_reason: str | None = None
    expected_side_effect_id: str | None = None
    expected_args_hash: str | None = None


class OperatorApprovalActorResponse(BaseModel):
    """Server-derived actor summary for operator decision responses."""

    model_config = ConfigDict(extra="forbid")

    user_id: str
    role: Role
    scopes: list[str] = Field(default_factory=list)
    server_derived: bool = True


class OperatorApprovalSummaryResponse(BaseModel):
    """Read-only operator approval inbox row."""

    model_config = ConfigDict(extra="forbid")

    approval_id: str
    run_id: str
    status: str
    task: str
    action_summary: str | None = None
    risk_level: RiskLevel | None = None
    required_scopes: list[str] = Field(default_factory=list)
    policy_status: str | None = None
    approval_status: str
    tool_name: str | None = None
    target: OperatorApprovalTargetResponse | None = None
    side_effect_id: str | None = None
    args_hash: str | None = None
    requested_by: str | None = None
    execution_mode: OperatorExecutionModeResponse = Field(
        default_factory=OperatorExecutionModeResponse
    )
    audit_event_count: int = 0
    created_at: datetime | None = None
    updated_at: datetime | None = None


class OperatorApprovalListResponse(BaseModel):
    """Read-only operator approval inbox response."""

    model_config = ConfigDict(extra="forbid")

    approvals: list[OperatorApprovalSummaryResponse] = Field(default_factory=list)


class OperatorApprovalDetailResponse(OperatorApprovalSummaryResponse):
    """Read-only operator approval detail response."""

    proposal: dict[str, Any] | None = None
    policy_decisions: list[dict[str, Any]] = Field(default_factory=list)
    validated_arguments: dict[str, dict[str, Any]] = Field(default_factory=dict)
    audit_events: list[OperatorAuditEventReferenceResponse] = Field(
        default_factory=list
    )


class OperatorApprovalDecisionResponse(BaseModel):
    """Operator approve/reject action response."""

    model_config = ConfigDict(extra="forbid")

    approval_id: str
    run_id: str
    decision: OperatorApprovalDecision
    status: str
    approval_status: str
    actor: OperatorApprovalActorResponse
    decision_reason: str | None = None
    side_effect_id: str | None = None
    args_hash: str | None = None
    audit_event_count: int = 0
    execution_mode: OperatorExecutionModeResponse = Field(
        default_factory=OperatorExecutionModeResponse
    )
    message: str


class OperatorApprovalStatusResponse(BaseModel):
    """Read-only current status for one local/demo operator approval."""

    model_config = ConfigDict(extra="forbid")

    approval_id: str
    run_id: str
    status: str
    approval_status: str
    decision_state: str
    task: str
    tool_name: str | None = None
    target: OperatorApprovalTargetResponse | None = None
    side_effect_id: str | None = None
    args_hash: str | None = None
    can_approve: bool = False
    can_reject: bool = False
    action_unavailable_reason: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    execution_mode: OperatorExecutionModeResponse = Field(
        default_factory=OperatorExecutionModeResponse
    )
    decision_history: list[OperatorDecisionHistoryItemResponse] = Field(
        default_factory=list
    )
    execution_result: OperatorExecutionResultResponse = Field(
        default_factory=OperatorExecutionResultResponse
    )


class OperatorApprovalAuditResponse(BaseModel):
    """Read-only local/demo audit evidence for one operator approval."""

    model_config = ConfigDict(extra="forbid")

    approval_id: str
    run_id: str
    audit_scope: str = "local_demo"
    audit_limitations: str = (
        "Local/demo audit evidence from current process state; not a "
        "production-grade audit log."
    )
    events: list[OperatorAuditTimelineEventResponse] = Field(default_factory=list)
    decision_history: list[OperatorDecisionHistoryItemResponse] = Field(
        default_factory=list
    )


class OperatorSideEffectLedgerResponse(BaseModel):
    """Read-only local/demo side-effect and ledger evidence."""

    model_config = ConfigDict(extra="forbid")

    side_effect_id: str
    run_id: str | None = None
    tool_name: str | None = None
    repository: str | None = None
    issue_number: int | None = None
    args_hash: str | None = None
    status: str | None = None
    ledger_status: str | None = None
    record_available: bool = False
    source: str = "local_demo_state"
    external_result_summary: dict[str, Any] | None = None
    error_summary: dict[str, Any] | None = None
    duplicate_status: str | None = None
    execution_mode: OperatorExecutionModeResponse = Field(
        default_factory=OperatorExecutionModeResponse
    )
    message: str
