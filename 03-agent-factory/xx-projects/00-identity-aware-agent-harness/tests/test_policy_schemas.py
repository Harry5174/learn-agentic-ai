import pytest
from pydantic import ValidationError

from app.policy.schemas import PolicyDecision, PolicyDecisionType


def test_valid_allow_decision_creates_successfully() -> None:
    decision = PolicyDecision(
        decision=PolicyDecisionType.ALLOW,
        tool_name="github_list_issues",
        reason="Viewer has read scope.",
        required_scopes=["github:issues:read"],
        missing_scopes=[],
    )

    assert decision.decision == PolicyDecisionType.ALLOW
    assert decision.tool_name == "github_list_issues"
    assert decision.missing_scopes == []


def test_valid_deny_decision_with_missing_scopes() -> None:
    decision = PolicyDecision(
        decision=PolicyDecisionType.DENY,
        tool_name="github_create_issue",
        reason="Missing required write scope.",
        required_scopes=["github:issues:write"],
        missing_scopes=["github:issues:write"],
    )

    assert decision.decision == PolicyDecisionType.DENY
    assert decision.missing_scopes == ["github:issues:write"]


def test_invalid_decision_type_fails() -> None:
    with pytest.raises(ValidationError):
        PolicyDecision(
            decision="maybe",
            tool_name="github_list_issues",
            reason="Invalid decision.",
        )


def test_required_and_missing_scope_lists_are_independent() -> None:
    first = PolicyDecision(
        decision=PolicyDecisionType.ALLOW,
        tool_name="tool_one",
        reason="Allowed.",
    )
    second = PolicyDecision(
        decision=PolicyDecisionType.ALLOW,
        tool_name="tool_two",
        reason="Allowed.",
    )

    first.required_scopes.append("scope:one")
    first.missing_scopes.append("scope:missing")

    assert first.required_scopes == ["scope:one"]
    assert first.missing_scopes == ["scope:missing"]
    assert second.required_scopes == []
    assert second.missing_scopes == []