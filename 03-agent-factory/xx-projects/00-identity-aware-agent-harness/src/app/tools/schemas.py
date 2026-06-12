from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field

class RiskLevel(StrEnum):
    """Risk level for a tool call."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ToolCallRequest(BaseModel):
    """Requested tool call proposed by the agent."""

    tool_name: str
    arguments: dict[str, Any] = Field(default_factory=dict)
    risk_level: RiskLevel | None = None

class ToolSpec(BaseModel):
    """Static specification for a registered tool."""

    name: str
    description: str
    required_scopes: list[str] = Field(default_factory=list)
    risk_level: RiskLevel

class ToolExecutionResult(BaseModel):
    """Result returned by a dry-run tool execution."""

    tool_name: str
    success: bool
    result: dict[str, Any] = Field(default_factory=dict)
    dry_run: bool = True
    message: str | None = None