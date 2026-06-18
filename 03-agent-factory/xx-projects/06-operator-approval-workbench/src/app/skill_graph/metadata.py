from typing import Any

from app.audit.logger import create_audit_event
from app.audit.schemas import AuditEvent, AuditEventType
from app.skills.schemas import ProposalValidationResult, ProposalValidationStatus
from app.tools.github_comment import GITHUB_COMMENT_TOOL_NAME
from app.tools.schemas import ToolExecutionResult


def create_proposal_event(
    run_id: str,
    actor_id: str,
    proposal,
) -> AuditEvent:
    return create_audit_event(
        task_id=run_id,
        event_type=AuditEventType.TOOL_SELECTED,
        actor_id=actor_id,
        message="Skill proposal was produced.",
        tool_name=proposal.steps[0].tool_name if proposal.steps else None,
        metadata={
            "kind": "skill_proposal",
            "skill_id": proposal.proposed_skill_id,
            "skill_version": proposal.proposed_skill_version,
            "step_ids": [step.step_id for step in proposal.steps],
            "tool_names": [step.tool_name for step in proposal.steps],
            "rationale": proposal.rationale,
        },
    )


def create_validation_event(
    run_id: str,
    actor_id: str,
    validation_result: ProposalValidationResult,
) -> AuditEvent:
    risk_level = validation_result.risk_level

    return create_audit_event(
        task_id=run_id,
        event_type=AuditEventType.PERMISSION_CHECKED,
        actor_id=actor_id,
        message="Proposal validation completed.",
        metadata={
            "kind": "proposal_validation",
            "status": validation_result.status.value,
            "rejection_reasons": [
                reason.value for reason in validation_result.rejection_reasons
            ],
            "required_scopes": list(validation_result.required_scopes),
            "risk_level": None if risk_level is None else risk_level.value,
            "approval_required": validation_result.approval_required,
            **argument_validation_metadata(validation_result),
            **github_comment_validation_metadata(validation_result),
        },
    )


def github_comment_approval_metadata(
    *,
    tool_name: str,
    concept: str,
) -> dict[str, Any] | None:
    if tool_name != GITHUB_COMMENT_TOOL_NAME:
        return None

    return {
        "kind": "github_comment_approval",
        "github_comment_audit_concept": concept,
        "approval_binding": "validated_tool_arguments_in_current_graph_state",
        "approval_binding_limitation": (
            "ApprovalDecision does not persist validated_arguments_hash or "
            "side_effect_id in A3.3."
        ),
        "client_called": False,
    }


def github_comment_execution_metadata(
    *,
    tool_name: str,
    result: ToolExecutionResult,
) -> dict[str, Any] | None:
    if tool_name != GITHUB_COMMENT_TOOL_NAME:
        return None

    result_payload = dict(result.result)
    ledger_hit = bool(result_payload.get("ledger_hit"))
    client_called = bool(result_payload.get("client_called"))
    skipped = bool(result_payload.get("skipped"))
    concepts = ["github_comment_side_effect_id_computed"]

    concepts.append(
        "github_comment_ledger_hit"
        if ledger_hit
        else "github_comment_ledger_miss"
    )
    concepts.append(
        "github_comment_client_called"
        if client_called
        else "github_comment_client_not_called"
    )

    if result.success and skipped:
        concepts.append("github_comment_skipped")
    elif result.success:
        concepts.append("github_comment_executed")
    else:
        concepts.append("github_comment_failed")

    return {
        "kind": "github_comment_side_effect",
        "github_comment_audit_concepts": concepts,
        "mode": result_payload.get("mode"),
        "repository": result_payload.get("repository"),
        "issue_number": result_payload.get("issue_number"),
        "validated_arguments_hash": result_payload.get("validated_arguments_hash"),
        "side_effect_id": result_payload.get("side_effect_id"),
        "side_effect_status": result_payload.get("side_effect_status"),
        "ledger_hit": ledger_hit,
        "ledger_miss": bool(result_payload.get("ledger_miss")),
        "client_called": client_called,
        "skipped": skipped,
        "error_type": result_payload.get("error_type"),
        "real_github_network_call": False,
    }


def argument_validation_metadata(
    validation_result: ProposalValidationResult,
) -> dict[str, Any]:
    validated_skill_plan = validation_result.validated_skill_plan

    if validated_skill_plan is None:
        return {
            "argument_validation_status": None,
            "validated_argument_names": {},
            "redacted_argument_names": {},
            "argument_validation_issue_codes": [],
        }

    return {
        "argument_validation_status": validated_skill_plan.status.value,
        "validated_argument_names": {
            step_arguments.step_id: list(step_arguments.arguments)
            for step_arguments in validated_skill_plan.step_arguments
        },
        "redacted_argument_names": {
            step_arguments.step_id: list(step_arguments.redacted_argument_names)
            for step_arguments in validated_skill_plan.step_arguments
        },
        "argument_validation_issue_codes": [
            issue.reason_code for issue in validated_skill_plan.issues
        ],
    }


def github_comment_validation_metadata(
    validation_result: ProposalValidationResult,
) -> dict[str, Any]:
    proposal = validation_result.proposal
    skill = validation_result.skill
    skill_id = skill.skill_id if skill is not None else None

    if skill_id is None and proposal is not None:
        skill_id = proposal.proposed_skill_id

    if skill_id != GITHUB_COMMENT_TOOL_NAME:
        return {}

    validation_passed = validation_result.status == ProposalValidationStatus.ACCEPTED

    return {
        "github_comment_audit_concept": (
            "github_comment_validation_passed"
            if validation_passed
            else "github_comment_validation_failed"
        ),
    }
