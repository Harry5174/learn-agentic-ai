from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ArgumentValueType(StrEnum):
    """Scalar argument value types supported by the V1 contract."""

    STRING = "string"
    INTEGER = "integer"
    BOOLEAN = "boolean"


class ArgumentValidationStatus(StrEnum):
    """Closed validation states for a proposed argument plan."""

    ACCEPTED = "accepted"
    REJECTED = "rejected"


FORBIDDEN_ARGUMENT_NAMES = frozenset(
    {
        "user_id",
        "role",
        "roles",
        "scope",
        "scopes",
        "identity",
        "api_key",
        "api_token",
        "approval_authority",
        "approval_decision",
        "policy_decision",
        "policy_override",
        "risk_override",
        "risk_level",
        "requires_approval",
        "tool_name",
        "tool_id",
        "selected_tool",
        "skill_id",
        "skill_version",
    }
)


ScalarArgumentValue = str | int | bool


class ToolArgumentSpec(BaseModel):
    """Trusted schema metadata for one accepted tool argument."""

    model_config = ConfigDict(extra="forbid")

    name: str
    value_type: ArgumentValueType
    required: bool = False
    sensitive: bool = False
    description: str | None = None
    notes: str | None = None
    constraints: list[str] = Field(default_factory=list)


class ProposedStepArguments(BaseModel):
    """Raw untrusted runtime arguments proposed for a skill step."""

    model_config = ConfigDict(extra="forbid")

    step_id: str
    arguments: dict[str, Any] = Field(default_factory=dict)


class ValidatedStepArguments(BaseModel):
    """Validator-approved scalar runtime arguments for a skill step."""

    model_config = ConfigDict(extra="forbid")

    step_id: str
    arguments: dict[str, ScalarArgumentValue] = Field(default_factory=dict)
    redacted_argument_names: list[str] = Field(default_factory=list)

    @field_validator("arguments", mode="before")
    @classmethod
    def validate_scalar_arguments(cls, value: Any) -> Any:
        if value is None:
            return {}

        if not isinstance(value, dict):
            raise ValueError("validated arguments must be a mapping")

        for argument_value in value.values():
            if not isinstance(argument_value, str | int | bool):
                raise ValueError(
                    "validated arguments must be string, integer, or boolean"
                )

        return value


class ArgumentValidationIssue(BaseModel):
    """Safe, non-secret explanation for an argument validation failure."""

    model_config = ConfigDict(extra="forbid")

    step_id: str | None = None
    argument_name: str | None = None
    reason_code: str
    message: str


class ValidatedSkillPlan(BaseModel):
    """Validated argument plan produced after checking untrusted arguments."""

    model_config = ConfigDict(extra="forbid")

    status: ArgumentValidationStatus
    skill_id: str
    skill_version: str
    step_arguments: list[ValidatedStepArguments] = Field(default_factory=list)
    issues: list[ArgumentValidationIssue] = Field(default_factory=list)
