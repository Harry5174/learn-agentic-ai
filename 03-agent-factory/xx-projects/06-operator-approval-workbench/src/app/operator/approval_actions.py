from app.api.operator_schemas import (
    OperatorApprovalActorResponse,
    OperatorApprovalDecision,
    OperatorApprovalDecisionResponse,
    OperatorExecutionModeResponse,
)
from app.audit.schemas import AuditEvent
from app.identity.schemas import IdentityContext
from app.side_effects.idempotency import build_side_effect_id, validated_arguments_hash
from app.skill_graph.service import (
    SkillGraphService,
    SkillRunNotFoundError,
    SkillRunNotPausedError,
)
from app.skill_graph.state import SkillGraphState
from app.skill_graph.validation_helpers import (
    validated_step_arguments_by_id,
    validated_steps,
)
from app.state.schemas import TaskStatus
from app.tools.github_comment import GITHUB_COMMENT_TOOL_NAME


APPROVE_SCOPE = "approval:approve"
REJECT_SCOPE = "approval:reject"


class OperatorApprovalActionNotFoundError(Exception):
    """Raised when an operator approval cannot be found."""


class OperatorApprovalActionConflictError(Exception):
    """Raised when an operator approval action is stale or mismatched."""


class OperatorApprovalActionForbiddenError(Exception):
    """Raised when the server-derived actor lacks decision authority."""


class OperatorApprovalActionService:
    """Approve or reject current local/demo approvals by operator approval id."""

    def __init__(self, skill_run_service: SkillGraphService) -> None:
        self._skill_run_service = skill_run_service

    def approve(
        self,
        *,
        approval_id: str,
        actor: IdentityContext,
        decision_reason: str | None = None,
        expected_side_effect_id: str | None = None,
        expected_args_hash: str | None = None,
    ) -> OperatorApprovalDecisionResponse:
        return self._decide(
            approval_id=approval_id,
            actor=actor,
            decision=OperatorApprovalDecision.APPROVE,
            required_scope=APPROVE_SCOPE,
            decision_reason=decision_reason,
            expected_side_effect_id=expected_side_effect_id,
            expected_args_hash=expected_args_hash,
        )

    def reject(
        self,
        *,
        approval_id: str,
        actor: IdentityContext,
        decision_reason: str,
        expected_side_effect_id: str | None = None,
        expected_args_hash: str | None = None,
    ) -> OperatorApprovalDecisionResponse:
        return self._decide(
            approval_id=approval_id,
            actor=actor,
            decision=OperatorApprovalDecision.REJECT,
            required_scope=REJECT_SCOPE,
            decision_reason=decision_reason,
            expected_side_effect_id=expected_side_effect_id,
            expected_args_hash=expected_args_hash,
        )

    def _decide(
        self,
        *,
        approval_id: str,
        actor: IdentityContext,
        decision: OperatorApprovalDecision,
        required_scope: str,
        decision_reason: str | None,
        expected_side_effect_id: str | None,
        expected_args_hash: str | None,
    ) -> OperatorApprovalDecisionResponse:
        current_state = self._pending_state(approval_id)
        side_effect_id = _side_effect_id(current_state)
        args_hash = _args_hash(current_state)

        _assert_expected_value(
            label="side_effect_id",
            expected=expected_side_effect_id,
            actual=side_effect_id,
        )
        _assert_expected_value(
            label="args_hash",
            expected=expected_args_hash,
            actual=args_hash,
        )
        _assert_scope(actor, required_scope)

        reason = decision_reason or "Approved via operator workbench API."

        try:
            if decision == OperatorApprovalDecision.APPROVE:
                decided_state = self._skill_run_service.approve_run(
                    run_id=approval_id,
                    approver=actor,
                    reason=reason,
                )
            else:
                decided_state = self._skill_run_service.reject_run(
                    run_id=approval_id,
                    rejector=actor,
                    reason=reason,
                )
        except SkillRunNotFoundError as exc:
            raise OperatorApprovalActionNotFoundError(
                f"Approval not found: {approval_id}"
            ) from exc
        except SkillRunNotPausedError as exc:
            raise OperatorApprovalActionConflictError(
                f"Approval is not pending: {approval_id}"
            ) from exc

        return _decision_response(
            approval_id=approval_id,
            state=decided_state,
            decision=decision,
            actor=actor,
            decision_reason=reason,
            fallback_side_effect_id=side_effect_id,
            fallback_args_hash=args_hash,
        )

    def _pending_state(self, approval_id: str) -> SkillGraphState:
        try:
            state = self._skill_run_service.get_run(approval_id)
        except SkillRunNotFoundError as exc:
            raise OperatorApprovalActionNotFoundError(
                f"Approval not found: {approval_id}"
            ) from exc

        if (
            state.get("status") != TaskStatus.PAUSED_FOR_APPROVAL
            or state.get("approval_request") is None
        ):
            raise OperatorApprovalActionConflictError(
                f"Approval is not pending: {approval_id}"
            )

        return state


def _assert_scope(actor: IdentityContext, required_scope: str) -> None:
    if required_scope not in actor.scopes:
        raise OperatorApprovalActionForbiddenError(
            f"Actor lacks required scope: {required_scope}"
        )


def _assert_expected_value(
    *,
    label: str,
    expected: str | None,
    actual: str | None,
) -> None:
    if expected is None:
        return

    if actual is None:
        raise OperatorApprovalActionConflictError(
            f"Current approval has no {label} to compare."
        )

    if expected != actual:
        raise OperatorApprovalActionConflictError(
            f"Expected {label} does not match current approval."
        )


def _decision_response(
    *,
    approval_id: str,
    state: SkillGraphState,
    decision: OperatorApprovalDecision,
    actor: IdentityContext,
    decision_reason: str,
    fallback_side_effect_id: str | None,
    fallback_args_hash: str | None,
) -> OperatorApprovalDecisionResponse:
    side_effect_id = _side_effect_id(state) or fallback_side_effect_id
    args_hash = _args_hash(state) or fallback_args_hash

    return OperatorApprovalDecisionResponse(
        approval_id=approval_id,
        run_id=state["run_id"],
        decision=decision,
        status=state["status"].value,
        approval_status=_approval_status_for_decision(decision),
        actor=OperatorApprovalActorResponse(
            user_id=actor.user_id,
            role=actor.role,
            scopes=list(actor.scopes),
        ),
        decision_reason=decision_reason,
        side_effect_id=side_effect_id,
        args_hash=args_hash,
        audit_event_count=len(state.get("audit_trail", [])),
        execution_mode=OperatorExecutionModeResponse(),
        message=_message_for_decision(decision, state),
    )


def _message_for_decision(
    decision: OperatorApprovalDecision,
    state: SkillGraphState,
) -> str:
    if decision == OperatorApprovalDecision.APPROVE:
        return "Approval accepted through operator workbench API."

    return (
        state.get("final_report")
        or "Approval rejected through operator workbench API."
    )


def _approval_status_for_decision(decision: OperatorApprovalDecision) -> str:
    if decision == OperatorApprovalDecision.APPROVE:
        return "approved"
    return "rejected"


def _side_effect_id(state: SkillGraphState) -> str | None:
    return _first_metadata_value(
        state.get("audit_trail", []),
        "side_effect_id",
    ) or _computed_github_side_effect_id(state)


def _args_hash(state: SkillGraphState) -> str | None:
    return _first_metadata_value(
        state.get("audit_trail", []),
        "validated_arguments_hash",
    ) or _first_metadata_value(
        state.get("audit_trail", []),
        "args_hash",
    ) or _computed_github_args_hash(state)


def _computed_github_side_effect_id(state: SkillGraphState) -> str | None:
    github_action = _github_action_identity(state)
    if github_action is None:
        return None

    step_id, argument_hash = github_action
    return build_side_effect_id(
        skill_run_id=state["run_id"],
        step_id=step_id,
        tool_name=GITHUB_COMMENT_TOOL_NAME,
        validated_arguments_hash=argument_hash,
    )


def _computed_github_args_hash(state: SkillGraphState) -> str | None:
    github_action = _github_action_identity(state)
    if github_action is None:
        return None

    _, argument_hash = github_action
    return argument_hash


def _github_action_identity(state: SkillGraphState) -> tuple[str, str] | None:
    validation_result = state.get("validation_result")
    arguments_by_step_id = validated_step_arguments_by_id(validation_result)

    if arguments_by_step_id is None:
        return None

    for step in validated_steps(validation_result):
        if step.tool_name != GITHUB_COMMENT_TOOL_NAME:
            continue

        arguments = arguments_by_step_id.get(step.step_id)
        if arguments is None:
            return None

        return step.step_id, validated_arguments_hash(arguments)

    return None


def _first_metadata_value(
    audit_trail: list[AuditEvent],
    key: str,
) -> str | None:
    for event in audit_trail:
        value = event.metadata.get(key)
        if isinstance(value, str):
            return value
    return None
