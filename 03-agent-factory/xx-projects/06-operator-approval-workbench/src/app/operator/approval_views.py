from typing import Any

from app.api.operator_schemas import (
    OperatorApprovalDetailResponse,
    OperatorApprovalSummaryResponse,
    OperatorApprovalTargetResponse,
    OperatorAuditEventReferenceResponse,
    OperatorExecutionModeResponse,
)
from app.audit.schemas import AuditEvent
from app.policy.schemas import PolicyDecision
from app.skill_graph.state import SkillGraphState
from app.skills.argument_schemas import ValidatedSkillPlan
from app.skills.schemas import ProposalValidationResult, SkillProposal
from app.state.schemas import TaskStatus

SENSITIVE_KEY_PARTS = (
    "authorization",
    "bearer",
    "token",
    "secret",
    "password",
    "credential",
    "api_key",
    "apikey",
    ".env",
)
SENSITIVE_VALUE_PARTS = (
    "ghp_",
    "github_pat_",
    "gho_",
    "ghu_",
    "ghs_",
    "ghr_",
    "bearer ",
    "github_access_token=",
    "agent_factory_github_token=",
)


class ApprovalViewNotFoundError(Exception):
    """Raised when a read-only approval view cannot be found."""


class ApprovalInboxView:
    """Build read-only operator approval views from local skill-run state."""

    def __init__(self, runs: list[SkillGraphState]) -> None:
        self._runs = runs

    def list_approvals(self) -> list[OperatorApprovalSummaryResponse]:
        return [
            _summary_from_state(state)
            for state in self._runs
            if _is_pending_approval_state(state)
        ]

    def get_approval(self, approval_id: str) -> OperatorApprovalDetailResponse:
        for state in self._runs:
            if _is_pending_approval_state(state) and state["run_id"] == approval_id:
                return _detail_from_state(state)

        raise ApprovalViewNotFoundError(f"Approval not found: {approval_id}")


def _is_pending_approval_state(state: SkillGraphState) -> bool:
    return (
        state.get("status") == TaskStatus.PAUSED_FOR_APPROVAL
        and state.get("approval_request") is not None
    )


def _summary_from_state(state: SkillGraphState) -> OperatorApprovalSummaryResponse:
    approval_request = state["approval_request"]
    validation_result = state.get("validation_result")
    policy_decisions = list(state.get("policy_decisions", []))
    audit_trail = list(state.get("audit_trail", []))

    return OperatorApprovalSummaryResponse(
        approval_id=state["run_id"],
        run_id=state["run_id"],
        status=state["status"].value,
        task=_redact_if_sensitive(state["task"]),
        action_summary=_redact_if_sensitive(approval_request.reason),
        risk_level=approval_request.risk_level,
        required_scopes=_required_scopes(validation_result, policy_decisions),
        policy_status=_policy_status(policy_decisions),
        approval_status="pending",
        tool_name=approval_request.tool_name,
        target=_target_from_arguments(approval_request.tool_arguments),
        side_effect_id=_first_metadata_value(audit_trail, "side_effect_id"),
        args_hash=_first_args_hash(audit_trail),
        requested_by=approval_request.requested_by,
        execution_mode=OperatorExecutionModeResponse(),
        audit_event_count=len(audit_trail),
        created_at=_first_event_timestamp(audit_trail),
        updated_at=_last_event_timestamp(audit_trail),
    )


def _detail_from_state(state: SkillGraphState) -> OperatorApprovalDetailResponse:
    summary = _summary_from_state(state)
    validation_result = state.get("validation_result")
    proposal = state.get("proposal")
    audit_trail = list(state.get("audit_trail", []))

    return OperatorApprovalDetailResponse(
        **summary.model_dump(),
        proposal=_safe_proposal_summary(proposal),
        policy_decisions=[
            _policy_decision_payload(decision)
            for decision in state.get("policy_decisions", [])
        ],
        validated_arguments=_safe_validated_arguments(validation_result),
        audit_events=[
            OperatorAuditEventReferenceResponse(
                event_id=event.event_id,
                event_type=event.event_type.value,
                timestamp=event.timestamp,
                message=_redact_if_sensitive(event.message),
            )
            for event in audit_trail
        ],
    )


def _required_scopes(
    validation_result: ProposalValidationResult | None,
    policy_decisions: list[PolicyDecision],
) -> list[str]:
    if validation_result is not None:
        return list(validation_result.required_scopes)

    scopes: list[str] = []

    for decision in policy_decisions:
        scopes.extend(decision.required_scopes)

    return sorted(set(scopes))


def _policy_status(policy_decisions: list[PolicyDecision]) -> str | None:
    if not policy_decisions:
        return None

    return policy_decisions[-1].decision.value


def _policy_decision_payload(decision: PolicyDecision) -> dict[str, Any]:
    return {
        "decision": decision.decision.value,
        "tool_name": decision.tool_name,
        "reason": _redact_if_sensitive(decision.reason),
        "required_scopes": list(decision.required_scopes),
        "missing_scopes": list(decision.missing_scopes),
    }


def _safe_proposal_summary(proposal: SkillProposal | None) -> dict[str, Any] | None:
    if proposal is None:
        return None

    return {
        "proposed_skill_id": proposal.proposed_skill_id,
        "proposed_skill_version": proposal.proposed_skill_version,
        "rationale": _redact_if_sensitive(proposal.rationale),
        "proposed_tool_names": [step.tool_name for step in proposal.steps],
    }


def _safe_validated_arguments(
    validation_result: ProposalValidationResult | None,
) -> dict[str, dict[str, Any]]:
    if validation_result is None:
        return {}

    validated_plan = validation_result.validated_skill_plan

    if validated_plan is None:
        return {}

    return _safe_arguments_from_plan(validated_plan)


def _safe_arguments_from_plan(
    validated_plan: ValidatedSkillPlan,
) -> dict[str, dict[str, Any]]:
    safe_arguments: dict[str, dict[str, Any]] = {}

    for step_arguments in validated_plan.step_arguments:
        step_safe_arguments = _safe_mapping(step_arguments.arguments)

        if step_safe_arguments:
            safe_arguments[step_arguments.step_id] = step_safe_arguments

    return safe_arguments


def _target_from_arguments(
    arguments: dict[str, Any],
) -> OperatorApprovalTargetResponse | None:
    repository = arguments.get("repository")
    issue_number = arguments.get("issue_number")

    if repository is None and issue_number is None:
        return None

    return OperatorApprovalTargetResponse(
        repository=repository if isinstance(repository, str) else None,
        issue_number=issue_number if isinstance(issue_number, int) else None,
    )


def _safe_mapping(arguments: dict[str, Any]) -> dict[str, Any]:
    safe_arguments: dict[str, Any] = {}

    for key, value in arguments.items():
        if _is_sensitive_key(key):
            continue

        safe_arguments[key] = _safe_value(value)

    return safe_arguments


def _safe_value(value: Any) -> Any:
    if isinstance(value, str):
        return _redact_if_sensitive(value)

    if isinstance(value, bool) or isinstance(value, int) or value is None:
        return value

    return "[redacted]"


def _redact_if_sensitive(value: str) -> str:
    if _contains_sensitive_value(value):
        return "[redacted]"

    return value


def _is_sensitive_key(key: str) -> bool:
    normalized = key.lower()
    return any(part in normalized for part in SENSITIVE_KEY_PARTS)


def _contains_sensitive_value(value: str) -> bool:
    normalized = value.lower()
    return any(part in normalized for part in SENSITIVE_VALUE_PARTS)


def _first_metadata_value(audit_trail: list[AuditEvent], key: str) -> str | None:
    for event in audit_trail:
        value = event.metadata.get(key)

        if isinstance(value, str) and not _contains_sensitive_value(value):
            return value

    return None


def _first_args_hash(audit_trail: list[AuditEvent]) -> str | None:
    return _first_metadata_value(
        audit_trail,
        "validated_arguments_hash",
    ) or _first_metadata_value(audit_trail, "args_hash")


def _first_event_timestamp(audit_trail: list[AuditEvent]):
    if not audit_trail:
        return None

    return audit_trail[0].timestamp


def _last_event_timestamp(audit_trail: list[AuditEvent]):
    if not audit_trail:
        return None

    return audit_trail[-1].timestamp
