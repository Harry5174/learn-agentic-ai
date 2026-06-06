from typing import Literal

from app.graph.state import HarnessGraphState
from app.policy.schemas import PolicyDecisionType
from app.state.schemas import TaskStatus


GraphRoute = Literal[
    "execute_tool",
    "finalize_denial",
    "pause_for_approval",
    "generate_report",
]

ApprovalRoute = Literal[
    "execute_tool",
    "finalize_rejection",
    "generate_report",
]


def route_after_interpret_task(state: HarnessGraphState) -> Literal["policy_guard", "generate_report"]:
    """Route after task interpretation.

    Unknown tasks are marked FAILED and routed directly to report generation.
    """

    if state.get("status") == TaskStatus.FAILED:
        return "generate_report"

    return "policy_guard"

def route_after_approval_decision(state: HarnessGraphState) -> ApprovalRoute:
    """Route after an approval decision is injected on resume."""

    if state.get("status") == TaskStatus.RUNNING:
        return "execute_tool"

    if state.get("status") == TaskStatus.REJECTED:
        return "finalize_rejection"

    return "generate_report"


def route_after_policy_guard(state: HarnessGraphState) -> GraphRoute:
    """Route based on deterministic policy decision."""

    decision = state.get("policy_decision")

    if decision is None:
        return "generate_report"

    if decision.decision == PolicyDecisionType.ALLOW:
        return "execute_tool"

    if decision.decision == PolicyDecisionType.DENY:
        return "finalize_denial"

    if decision.decision == PolicyDecisionType.REQUIRE_APPROVAL:
        return "pause_for_approval"

    return "generate_report"