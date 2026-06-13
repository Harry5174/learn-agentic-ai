from pydantic import BaseModel

from app.approval.schemas import ApprovalRequest
from app.audit.schemas import AuditEvent
from app.graph.state import HarnessGraphState
from app.state.schemas import TaskStatus
from app.tools.schemas import RiskLevel


class ToolSummaryResponse(BaseModel):
    """Public metadata for a registered tool."""

    name: str
    description: str
    risk_level: RiskLevel
    required_scopes: list[str]


class ToolsListResponse(BaseModel):
    """Response body for the tools listing endpoint."""

    tools: list[ToolSummaryResponse]


class TaskCreateRequest(BaseModel):
    """Request body for starting a task."""

    user_query: str


class ApprovalActionRequest(BaseModel):
    """Optional request body for approving or rejecting a task."""

    reason: str | None = None


class ApprovalRequestSummary(BaseModel):
    """Public approval request summary for a paused task."""

    task_id: str
    tool_name: str
    reason: str
    requested_by: str


class TaskSummaryResponse(BaseModel):
    """Public task state summary."""

    task_id: str
    status: TaskStatus
    selected_tool_name: str | None = None
    requires_approval: bool
    final_report: str | None = None
    error_message: str | None = None
    approval_request: ApprovalRequestSummary | None = None


class TaskAuditResponse(BaseModel):
    """Public audit trail response for a task."""

    task_id: str
    audit_trail: list[AuditEvent]


def _approval_request_summary(
    approval_request: ApprovalRequest | None,
) -> ApprovalRequestSummary | None:
    if approval_request is None:
        return None

    return ApprovalRequestSummary(
        task_id=approval_request.task_id,
        tool_name=approval_request.tool_name,
        reason=approval_request.reason,
        requested_by=approval_request.requested_by,
    )


def task_summary_from_state(state: HarnessGraphState) -> TaskSummaryResponse:
    """Convert internal graph state into a public task response."""

    task_status = state["status"]
    requires_approval = task_status == TaskStatus.PAUSED_FOR_APPROVAL

    return TaskSummaryResponse(
        task_id=state["task_id"],
        status=task_status,
        selected_tool_name=state.get("selected_tool_name"),
        requires_approval=requires_approval,
        final_report=state.get("final_report"),
        error_message=state.get("error_message"),
        approval_request=(
            _approval_request_summary(state.get("approval_request"))
            if requires_approval
            else None
        ),
    )
