from typing import Any

from app.api.operator_schemas import (
    OperatorApprovalStatusResponse,
    OperatorApprovalTargetResponse,
    OperatorExecutionModeResponse,
    OperatorExecutionResultResponse,
    OperatorExecutionStepResultResponse,
)
from app.identity.schemas import IdentityContext
from app.operator.approval_actions import (
    APPROVE_SCOPE,
    REJECT_SCOPE,
    _args_hash,
    _side_effect_id,
)
from app.operator.audit_views import (
    approval_status_from_state,
    decision_history_from_state,
    safe_mapping,
    safe_text,
)
from app.skill_graph.service import SkillGraphService, SkillRunNotFoundError
from app.skill_graph.state import SkillGraphState
from app.state.schemas import TaskStatus
from app.tools.schemas import ToolExecutionResult


class OperatorStatusViewNotFoundError(Exception):
    """Raised when local/demo status visibility cannot find a run."""


class OperatorStatusView:
    """Build read-only local/demo status views from skill-run state."""

    def __init__(self, skill_run_service: SkillGraphService) -> None:
        self._skill_run_service = skill_run_service

    def get_status(
        self,
        approval_id: str,
        identity: IdentityContext,
    ) -> OperatorApprovalStatusResponse:
        try:
            state = self._skill_run_service.get_run(approval_id)
        except SkillRunNotFoundError as exc:
            raise OperatorStatusViewNotFoundError(
                f"Approval not found: {approval_id}"
            ) from exc

        approval_status = approval_status_from_state(state)
        can_approve = _can_decide(state, identity, APPROVE_SCOPE)
        can_reject = _can_decide(state, identity, REJECT_SCOPE)

        return OperatorApprovalStatusResponse(
            approval_id=approval_id,
            run_id=state["run_id"],
            status=state["status"].value,
            approval_status=approval_status,
            decision_state=approval_status,
            task=safe_text(state["task"]) or "",
            tool_name=_tool_name(state),
            target=_target_from_state(state),
            side_effect_id=safe_text(_side_effect_id(state)),
            args_hash=safe_text(_args_hash(state)),
            can_approve=can_approve,
            can_reject=can_reject,
            action_unavailable_reason=_action_unavailable_reason(state, identity),
            created_at=_first_event_timestamp(state),
            updated_at=_last_event_timestamp(state),
            execution_mode=OperatorExecutionModeResponse(),
            decision_history=decision_history_from_state(state),
            execution_result=execution_result_from_state(state),
        )


def execution_result_from_state(
    state: SkillGraphState,
) -> OperatorExecutionResultResponse:
    tool_results = list(state.get("tool_results", []))

    return OperatorExecutionResultResponse(
        attempted_step_count=len(tool_results),
        completed_step_count=sum(1 for result in tool_results if result.success),
        tool_names=[result.tool_name for result in tool_results],
        dry_run=all(result.dry_run for result in tool_results),
        final_report=safe_text(state.get("final_report")),
        error_message=safe_text(state.get("error_message")),
        step_results=[_step_result(result) for result in tool_results],
    )


def _step_result(result: ToolExecutionResult) -> OperatorExecutionStepResultResponse:
    return OperatorExecutionStepResultResponse(
        tool_name=result.tool_name,
        success=result.success,
        dry_run=result.dry_run,
        message=safe_text(result.message),
        result_summary=safe_mapping(result.result),
    )


def _can_decide(
    state: SkillGraphState,
    identity: IdentityContext,
    required_scope: str,
) -> bool:
    return (
        state.get("status") == TaskStatus.PAUSED_FOR_APPROVAL
        and state.get("approval_request") is not None
        and required_scope in identity.scopes
    )


def _action_unavailable_reason(
    state: SkillGraphState,
    identity: IdentityContext,
) -> str | None:
    if (
        state.get("status") != TaskStatus.PAUSED_FOR_APPROVAL
        or state.get("approval_request") is None
    ):
        return "Approval is not pending."

    if APPROVE_SCOPE not in identity.scopes and REJECT_SCOPE not in identity.scopes:
        return "Current identity cannot approve or reject this approval."

    return None


def _tool_name(state: SkillGraphState) -> str | None:
    approval_request = state.get("approval_request")
    if approval_request is not None:
        return approval_request.tool_name

    tool_results = list(state.get("tool_results", []))
    if tool_results:
        return tool_results[0].tool_name

    return None


def _target_from_state(state: SkillGraphState) -> OperatorApprovalTargetResponse | None:
    approval_request = state.get("approval_request")
    if approval_request is not None:
        return _target_from_mapping(approval_request.tool_arguments)

    for result in state.get("tool_results", []):
        target = _target_from_mapping(result.result)
        if target is not None:
            return target

    return None


def _target_from_mapping(
    values: dict[str, Any],
) -> OperatorApprovalTargetResponse | None:
    safe_values = safe_mapping(values)
    repository = safe_values.get("repository")
    issue_number = safe_values.get("issue_number")

    if repository is None and issue_number is None:
        return None

    return OperatorApprovalTargetResponse(
        repository=repository if isinstance(repository, str) else None,
        issue_number=issue_number if isinstance(issue_number, int) else None,
    )


def _first_event_timestamp(state: SkillGraphState):
    audit_trail = list(state.get("audit_trail", []))
    if not audit_trail:
        return None
    return audit_trail[0].timestamp


def _last_event_timestamp(state: SkillGraphState):
    audit_trail = list(state.get("audit_trail", []))
    if not audit_trail:
        return None
    return audit_trail[-1].timestamp
