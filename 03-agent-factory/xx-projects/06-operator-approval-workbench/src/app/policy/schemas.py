from enum import StrEnum
from pydantic import BaseModel, Field

class PolicyDecisionType(StrEnum):
    """Deterministic policy decision result."""

    ALLOW = "allow"
    DENY = "deny"
    REQUIRE_APPROVAL = "require_approval"


class PolicyDecision(BaseModel):
    """Result of a policy guard evaluation."""

    decision: PolicyDecisionType
    tool_name: str
    reason: str
    required_scopes: list[str] = Field(default_factory=list)
    missing_scopes: list[str] = Field(default_factory=list)