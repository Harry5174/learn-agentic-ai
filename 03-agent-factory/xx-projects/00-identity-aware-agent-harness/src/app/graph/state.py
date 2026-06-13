from typing import Any

from typing_extensions import TypedDict

from app.approval.schemas import ApprovalDecision, ApprovalRequest
from app.audit.schemas import AuditEvent
from app.identity.schemas import IdentityContext
from app.policy.schemas import PolicyDecision
from app.state.schemas import TaskStatus
from app.tools.schemas import ToolExecutionResult


class HarnessGraphState(TypedDict, total=False):
    """Runtime state for the local LangGraph harness.

    This is intentionally separate from domain Pydantic contracts.
    """

    task_id: str
    user_query: str
    identity: IdentityContext
    status: TaskStatus

    selected_tool_name: str | None
    tool_arguments: dict[str, Any]
    policy_decision: PolicyDecision | None
    approval_request: ApprovalRequest | None
    approval_decision: ApprovalDecision | None
    approval_actor: IdentityContext | None

    tool_result: ToolExecutionResult | None
    audit_trail: list[AuditEvent]
    final_report: str | None
    error_message: str | None
    resume_error: str | None