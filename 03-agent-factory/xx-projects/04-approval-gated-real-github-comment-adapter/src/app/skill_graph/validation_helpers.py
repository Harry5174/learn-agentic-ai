from typing import Any

from app.approval.schemas import ApprovalStatus
from app.policy.schemas import PolicyDecision, PolicyDecisionType
from app.skills.argument_schemas import ArgumentValidationStatus, ValidatedSkillPlan
from app.skills.schemas import (
    ProposalValidationResult,
    ProposalValidationStatus,
    SkillStep,
)
from app.skill_graph.state import SkillGraphState


def validation_accepted(
    validation_result: ProposalValidationResult | None,
) -> bool:
    return accepted_validated_skill_plan(validation_result) is not None


def accepted_validated_skill_plan(
    validation_result: ProposalValidationResult | None,
) -> ValidatedSkillPlan | None:
    if (
        validation_result is None
        or validation_result.status != ProposalValidationStatus.ACCEPTED
        or validation_result.skill is None
        or validation_result.proposal is None
    ):
        return None

    validated_skill_plan = validation_result.validated_skill_plan

    if (
        validated_skill_plan is None
        or validated_skill_plan.status != ArgumentValidationStatus.ACCEPTED
        or validated_skill_plan.skill_id != validation_result.skill.skill_id
        or validated_skill_plan.skill_version != validation_result.skill.version
    ):
        return None

    return validated_skill_plan


def validated_step_arguments_by_id(
    validation_result: ProposalValidationResult | None,
) -> dict[str, dict[str, Any]] | None:
    validated_skill_plan = accepted_validated_skill_plan(validation_result)

    if validated_skill_plan is None:
        return None

    arguments_by_step_id: dict[str, dict[str, Any]] = {}

    for step_arguments in validated_skill_plan.step_arguments:
        if step_arguments.step_id in arguments_by_step_id:
            return None

        arguments_by_step_id[step_arguments.step_id] = dict(step_arguments.arguments)

    return arguments_by_step_id


def validated_steps(
    validation_result: ProposalValidationResult | None,
) -> list[SkillStep]:
    if not validation_accepted(validation_result):
        return []

    step_by_id = {step.step_id: step for step in validation_result.skill.steps}

    return [
        step_by_id[proposed_step.step_id]
        for proposed_step in validation_result.proposal.steps
        if proposed_step.step_id in step_by_id
    ]


def first_approval_policy_decision(
    policy_decisions: list[PolicyDecision],
) -> PolicyDecision | None:
    for policy_decision in policy_decisions:
        if policy_decision.decision == PolicyDecisionType.REQUIRE_APPROVAL:
            return policy_decision

    return None


def tool_arguments_for_decision(
    state: SkillGraphState,
    policy_decision: PolicyDecision,
) -> dict[str, Any]:
    validation_result = state.get("validation_result")
    arguments_by_step_id = validated_step_arguments_by_id(validation_result)

    if arguments_by_step_id is None:
        return {}

    for step in validated_steps(validation_result):
        if step.tool_name == policy_decision.tool_name:
            return dict(arguments_by_step_id.get(step.step_id, {}))

    return {}


def execution_allowed(state: SkillGraphState) -> bool:
    validation_result = state.get("validation_result")

    if not validation_accepted(validation_result):
        return False

    policy_decisions = state.get("policy_decisions", [])

    if not policy_decisions:
        return False

    if any(
        decision.decision == PolicyDecisionType.DENY
        for decision in policy_decisions
    ):
        return False

    approval_required = any(
        decision.decision == PolicyDecisionType.REQUIRE_APPROVAL
        for decision in policy_decisions
    )

    if not approval_required:
        return all(
            decision.decision == PolicyDecisionType.ALLOW
            for decision in policy_decisions
        )

    approval_decision = state.get("approval_decision")

    return (
        approval_decision is not None
        and approval_decision.status == ApprovalStatus.APPROVED
    )
