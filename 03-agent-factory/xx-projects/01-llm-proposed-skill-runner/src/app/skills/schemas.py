from datetime import datetime, timezone
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field, computed_field, field_validator

from app.identity.schemas import Role
from app.skills.argument_schemas import ToolArgumentSpec, ValidatedSkillPlan
from app.tools.schemas import RiskLevel, ToolExecutionResult


class ProposalValidationStatus(StrEnum):
    """Validation state for a model-proposed skill plan."""

    NOT_VALIDATED = "not_validated"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class ProposalValidationReason(StrEnum):
    """Structured reasons a proposed skill plan can be rejected."""

    UNKNOWN_SKILL = "unknown_skill"
    UNSUPPORTED_SKILL_VERSION = "unsupported_skill_version"
    EMPTY_STEPS = "empty_steps"
    DUPLICATE_STEP_ID = "duplicate_step_id"
    UNKNOWN_STEP = "unknown_step"
    TOOL_NOT_ALLOWED = "tool_not_allowed"
    MISSING_REQUIRED_SCOPE = "missing_required_scope"
    RISK_MISMATCH = "risk_mismatch"
    INVALID_ARGUMENTS = "invalid_arguments"


class SkillRunStatus(StrEnum):
    """Possible status values for a future skill run."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class SkillStep(BaseModel):
    """One declared step inside an allowed skill."""

    step_id: str
    description: str
    tool_name: str
    allowed_args_schema: dict[str, Any] = Field(default_factory=dict)
    argument_specs: list[ToolArgumentSpec] = Field(default_factory=list)
    required_scopes: list[str] = Field(default_factory=list)
    risk_level: RiskLevel


class SkillProposalStep(BaseModel):
    """One untrusted step proposed by a model or proposer."""

    step_id: str
    description: str
    tool_name: str
    allowed_args_schema: dict[str, Any] = Field(default_factory=dict)
    required_scopes: list[str] = Field(default_factory=list)
    risk_level: RiskLevel
    arguments: dict[str, Any] = Field(default_factory=dict)


class SkillSpec(BaseModel):
    """Static specification for an allowed reusable skill."""

    skill_id: str
    version: str
    name: str
    description: str
    steps: list[SkillStep]
    required_scopes: list[str] = Field(default_factory=list)
    risk_level: RiskLevel
    input_schema: dict[str, Any] = Field(default_factory=dict)
    output_schema: dict[str, Any] = Field(default_factory=dict)
    tags: list[str] = Field(default_factory=list)

    @computed_field
    @property
    def allowed_tool_names(self) -> list[str]:
        """Tool names the skill is allowed to request."""

        return [step.tool_name for step in self.steps]


class SkillProposal(BaseModel):
    """Untrusted structure proposed by a future model or proposer."""

    proposed_skill_id: str
    proposed_skill_version: str
    rationale: str
    steps: list[SkillProposalStep]


class ProposalValidationResult(BaseModel):
    """Deterministic validation result for an untrusted skill proposal."""

    status: ProposalValidationStatus
    proposal: SkillProposal | None = None
    skill: SkillSpec | None = None
    rejection_reasons: list[ProposalValidationReason] = Field(default_factory=list)
    required_scopes: list[str] = Field(default_factory=list)
    risk_level: RiskLevel | None = None
    approval_required: bool = False
    validated_skill_plan: ValidatedSkillPlan | None = None


class SkillRunResult(BaseModel):
    """Minimal contract for a future skill-run result."""

    run_id: str
    status: SkillRunStatus
    skill_id: str
    skill_version: str
    step_results: list[ToolExecutionResult] = Field(default_factory=list)
    message: str | None = None


class ProposalAuditEvent(BaseModel):
    """Audit contract for what a model proposed and how the harness classified it."""

    task_id: str
    user_id: str
    role: Role
    scopes: list[str] = Field(default_factory=list)
    proposed_skill_id: str
    proposed_skill_version: str
    proposed_steps: list[SkillProposalStep]
    proposed_tool_names: list[str] = Field(default_factory=list)
    validation_status: ProposalValidationStatus = (
        ProposalValidationStatus.NOT_VALIDATED
    )
    rejection_reasons: list[str] = Field(default_factory=list)
    risk_level: RiskLevel
    approval_required: bool
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("proposed_steps", mode="before")
    @classmethod
    def validate_proposed_steps(cls, value: Any) -> Any:
        if value is None:
            return []

        if not isinstance(value, list):
            return value

        return [
            step.model_dump() if isinstance(step, SkillStep) else step
            for step in value
        ]
