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
