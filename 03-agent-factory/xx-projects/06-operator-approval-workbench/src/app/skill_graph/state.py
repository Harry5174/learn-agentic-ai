from typing import Any

from typing_extensions import TypedDict

from app.approval.schemas import ApprovalDecision, ApprovalRequest
from app.audit.schemas import AuditEvent
from app.identity.schemas import IdentityContext
from app.policy.schemas import PolicyDecision
from app.skills.schemas import (
    ProposalValidationResult,
    SkillProposal,
    SkillRunResult,
)
from app.state.schemas import TaskStatus
from app.tools.schemas import ToolExecutionResult


class SkillGraphState(TypedDict, total=False):
    """Runtime state for the local skill execution graph."""

    run_id: str
    task: str
    requested_skill_id: str | None
    identity: IdentityContext
    status: TaskStatus

    proposal: SkillProposal | None
    validation_result: ProposalValidationResult | None
    policy_decisions: list[PolicyDecision]
    approval_request: ApprovalRequest | None
    approval_decision: ApprovalDecision | None
    approval_actor: IdentityContext | None

    step_arguments: dict[str, dict[str, Any]]
    tool_results: list[ToolExecutionResult]
    audit_trail: list[AuditEvent]
    final_result: SkillRunResult | None
    final_report: str | None
    error_message: str | None
    resume_error: str | None
