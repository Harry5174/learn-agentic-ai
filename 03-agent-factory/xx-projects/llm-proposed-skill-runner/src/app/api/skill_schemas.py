from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.tools.schemas import RiskLevel


class ProposerMode(StrEnum):
    """Supported proposer modes for future skill-run creation."""

    FAKE = "fake"
    LLM = "llm"


class SkillRunStatusResponse(StrEnum):
    """Public lifecycle states for future skill-run responses."""

    CREATED = "created"
    RUNNING = "running"
    PAUSED_FOR_APPROVAL = "paused_for_approval"
    COMPLETED = "completed"
    FAILED = "failed"
    DENIED = "denied"
    REJECTED = "rejected"


class SkillValidationStatusResponse(StrEnum):
    """Public validation states for future skill-run responses."""

    NOT_VALIDATED = "not_validated"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class SkillRunApprovalStatusResponse(StrEnum):
    """Public approval states for future skill-run responses."""

    NOT_REQUIRED = "not_required"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class SkillStepSummaryResponse(BaseModel):
    """Public metadata for one registered skill step."""

    model_config = ConfigDict(extra="forbid")

    step_id: str
    description: str
    tool_name: str
    risk_level: RiskLevel
    required_scopes: list[str] = Field(default_factory=list)


class SkillSummaryResponse(BaseModel):
    """Public metadata for a registered skill."""

    model_config = ConfigDict(extra="forbid")

    skill_id: str
    version: str
    name: str
    description: str
    required_scopes: list[str] = Field(default_factory=list)
    risk_level: RiskLevel
    steps: list[SkillStepSummaryResponse] = Field(default_factory=list)


class SkillRunCreateRequest(BaseModel):
    """Request body for creating a future skill run."""

    model_config = ConfigDict(extra="forbid")

    task: str
    proposer_mode: ProposerMode | None = None
    requested_skill_id: str | None = None


class SkillProposalSummaryResponse(BaseModel):
    """Public summary of the proposer-selected skill."""

    model_config = ConfigDict(extra="forbid")

    proposed_skill_id: str | None = None
    proposed_skill_version: str | None = None
    rationale: str | None = None
    proposed_tool_names: list[str] = Field(default_factory=list)


class SkillValidationSummaryResponse(BaseModel):
    """Public summary of deterministic proposal validation."""

    model_config = ConfigDict(extra="forbid")

    status: SkillValidationStatusResponse
    rejection_reasons: list[str] = Field(default_factory=list)
    required_scopes: list[str] = Field(default_factory=list)
    risk_level: RiskLevel | None = None


class SkillExecutionSummaryResponse(BaseModel):
    """Public summary of controlled dry-run execution."""

    model_config = ConfigDict(extra="forbid")

    attempted_step_count: int = 0
    completed_step_count: int = 0
    tool_names: list[str] = Field(default_factory=list)
    dry_run: bool = True


class SkillRunSummaryResponse(BaseModel):
    """Public skill-run state summary."""

    model_config = ConfigDict(extra="forbid")

    run_id: str
    status: SkillRunStatusResponse
    task: str
    proposer_mode: ProposerMode | None = None
    selected_skill_id: str | None = None
    selected_skill_version: str | None = None
    validation_status: SkillValidationStatusResponse
    approval_required: bool
    approval_status: SkillRunApprovalStatusResponse
    risk_level: RiskLevel | None = None
    final_report: str | None = None
    error_message: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    proposal: SkillProposalSummaryResponse | None = None
    validation: SkillValidationSummaryResponse | None = None
    execution: SkillExecutionSummaryResponse | None = None


class SkillRunApprovalRequest(BaseModel):
    """Request body for future skill-run approval or rejection actions."""

    model_config = ConfigDict(extra="forbid")

    reason: str | None = None
    comment: str | None = None


class SkillRunAuditEventResponse(BaseModel):
    """Public audit event summary for a future skill run."""

    model_config = ConfigDict(extra="forbid")

    event_type: str
    timestamp: datetime
    message: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class SkillRunAuditResponse(BaseModel):
    """Public audit trail response for a future skill run."""

    model_config = ConfigDict(extra="forbid")

    run_id: str
    events: list[SkillRunAuditEventResponse] = Field(default_factory=list)


class SkillRunErrorResponse(BaseModel):
    """Public error response for future skill-run endpoints."""

    model_config = ConfigDict(extra="forbid")

    error_code: str
    message: str
    details: dict[str, Any] = Field(default_factory=dict)
