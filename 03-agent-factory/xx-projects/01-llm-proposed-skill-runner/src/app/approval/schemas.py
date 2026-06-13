from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field

from app.identity.schemas import Role
from app.tools.schemas import RiskLevel


class ApprovalStatus(StrEnum):
    """Human approval decision status."""

    APPROVED = "approved"
    REJECTED = "rejected"


class ApprovalRequest(BaseModel):
    """Request for human approval before executing a high-risk action."""

    task_id: str
    tool_name: str
    tool_arguments: dict[str, Any] = Field(default_factory=dict)
    risk_level: RiskLevel
    requested_by: str
    reason: str


class ApprovalDecision(BaseModel):
    """Human approval or rejection decision."""

    task_id: str
    tool_name: str
    status: ApprovalStatus
    decided_by: str
    decider_role: Role
    reason: str | None = None