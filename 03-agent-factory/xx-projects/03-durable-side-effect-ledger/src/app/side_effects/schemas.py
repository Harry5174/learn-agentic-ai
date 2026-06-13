from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class SideEffectStatus(StrEnum):
    """Lifecycle state for an idempotent side-effect attempt."""

    STARTED = "started"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class SideEffectRecord(BaseModel):
    """Process-local record for one side-effect attempt."""

    model_config = ConfigDict(extra="forbid")

    side_effect_id: str
    skill_run_id: str
    step_id: str
    tool_name: str
    validated_arguments_hash: str
    status: SideEffectStatus
    created_at: datetime
    updated_at: datetime
    external_result: dict[str, Any] | None = None
    failure: dict[str, Any] | None = None
    audit_event_ids: list[str] = Field(default_factory=list)
