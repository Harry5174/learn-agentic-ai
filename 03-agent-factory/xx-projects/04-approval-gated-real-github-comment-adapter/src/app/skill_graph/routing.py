from typing import Literal

from app.policy.schemas import PolicyDecision, PolicyDecisionType
from app.skill_graph.state import SkillGraphState
from app.skill_graph.validation_helpers import validation_accepted
from app.state.schemas import TaskStatus


GraphRoute = Literal[
    "evaluate_policy",
    "execute_validated_steps",
    "finalize_denial",
    "finalize_failure",
    "finalize_rejection",
    "finalize_success",
    "finalize_validation_failure",
    "pause_for_approval",
]


def route_after_validation(state: SkillGraphState) -> GraphRoute:
    validation_result = state.get("validation_result")

    if validation_accepted(validation_result):
        return "evaluate_policy"

    return "finalize_validation_failure"


def route_after_policy(state: SkillGraphState) -> GraphRoute:
    status = state.get("status")

    if status == TaskStatus.RUNNING:
        return "execute_validated_steps"

    if status == TaskStatus.PAUSED_FOR_APPROVAL:
        return "pause_for_approval"

    if status == TaskStatus.DENIED:
        return "finalize_denial"

    return "finalize_failure"


def route_after_execution(state: SkillGraphState) -> GraphRoute:
    if state.get("status") == TaskStatus.RUNNING:
        return "finalize_success"

    return "finalize_failure"


def route_after_approval_decision(state: SkillGraphState) -> GraphRoute:
    status = state.get("status")

    if status == TaskStatus.RUNNING:
        return "execute_validated_steps"

    if status == TaskStatus.REJECTED:
        return "finalize_rejection"

    return "finalize_failure"


def status_from_policy_decisions(
    policy_decisions: list[PolicyDecision],
) -> TaskStatus:
    if not policy_decisions:
        return TaskStatus.FAILED

    if any(
        decision.decision == PolicyDecisionType.DENY
        for decision in policy_decisions
    ):
        return TaskStatus.DENIED

    if any(
        decision.decision == PolicyDecisionType.REQUIRE_APPROVAL
        for decision in policy_decisions
    ):
        return TaskStatus.PAUSED_FOR_APPROVAL

    return TaskStatus.RUNNING
