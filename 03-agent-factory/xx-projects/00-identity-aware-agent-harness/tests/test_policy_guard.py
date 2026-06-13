from app.identity.config import ADMIN_API_KEY, OPERATOR_API_KEY, VIEWER_API_KEY
from app.identity.resolver import resolve_identity_from_api_key
from app.policy.guard import evaluate_tool_permission
from app.policy.schemas import PolicyDecisionType
from app.tools.registry import build_default_tool_registry
from app.tools.schemas import RiskLevel, ToolSpec


def _identity(api_key: str):
    return resolve_identity_from_api_key(api_key)


def _tool(tool_name: str):
    registry = build_default_tool_registry()
    return registry.get_tool(tool_name)


def test_viewer_can_inspect_sandbox_issues() -> None:
    decision = evaluate_tool_permission(
        _identity(VIEWER_API_KEY),
        _tool("inspect_sandbox_issues"),
    )

    assert decision.decision == PolicyDecisionType.ALLOW
    assert decision.tool_name == "inspect_sandbox_issues"
    assert decision.required_scopes == ["tools:inspect"]
    assert decision.missing_scopes == []


def test_viewer_cannot_draft_issue_comment() -> None:
    decision = evaluate_tool_permission(
        _identity(VIEWER_API_KEY),
        _tool("draft_issue_comment"),
    )

    assert decision.decision == PolicyDecisionType.DENY
    assert decision.tool_name == "draft_issue_comment"
    assert decision.required_scopes == ["tools:draft"]
    assert decision.missing_scopes == ["tools:draft"]


def test_viewer_cannot_trigger_workflow_dry_run() -> None:
    decision = evaluate_tool_permission(
        _identity(VIEWER_API_KEY),
        _tool("trigger_workflow_dry_run"),
    )

    assert decision.decision == PolicyDecisionType.DENY
    assert decision.tool_name == "trigger_workflow_dry_run"
    assert decision.required_scopes == ["tools:trigger_workflow"]
    assert decision.missing_scopes == ["tools:trigger_workflow"]


def test_operator_can_inspect_sandbox_issues() -> None:
    decision = evaluate_tool_permission(
        _identity(OPERATOR_API_KEY),
        _tool("inspect_sandbox_issues"),
    )

    assert decision.decision == PolicyDecisionType.ALLOW
    assert decision.missing_scopes == []


def test_operator_can_draft_issue_comment() -> None:
    decision = evaluate_tool_permission(
        _identity(OPERATOR_API_KEY),
        _tool("draft_issue_comment"),
    )

    assert decision.decision == PolicyDecisionType.ALLOW
    assert decision.missing_scopes == []


def test_operator_requires_approval_for_workflow_trigger() -> None:
    decision = evaluate_tool_permission(
        _identity(OPERATOR_API_KEY),
        _tool("trigger_workflow_dry_run"),
    )

    assert decision.decision == PolicyDecisionType.REQUIRE_APPROVAL
    assert decision.tool_name == "trigger_workflow_dry_run"
    assert decision.required_scopes == ["tools:trigger_workflow"]
    assert decision.missing_scopes == ["tools:trigger_workflow"]


def test_admin_can_inspect_sandbox_issues() -> None:
    decision = evaluate_tool_permission(
        _identity(ADMIN_API_KEY),
        _tool("inspect_sandbox_issues"),
    )

    assert decision.decision == PolicyDecisionType.ALLOW
    assert decision.missing_scopes == []


def test_admin_can_draft_issue_comment() -> None:
    decision = evaluate_tool_permission(
        _identity(ADMIN_API_KEY),
        _tool("draft_issue_comment"),
    )

    assert decision.decision == PolicyDecisionType.ALLOW
    assert decision.missing_scopes == []


def test_admin_requires_approval_for_workflow_trigger() -> None:
    decision = evaluate_tool_permission(
        _identity(ADMIN_API_KEY),
        _tool("trigger_workflow_dry_run"),
    )

    assert decision.decision == PolicyDecisionType.REQUIRE_APPROVAL
    assert decision.tool_name == "trigger_workflow_dry_run"
    assert decision.required_scopes == ["tools:trigger_workflow"]
    assert decision.missing_scopes == []


def test_admin_does_not_bypass_high_risk_approval() -> None:
    decision = evaluate_tool_permission(
        _identity(ADMIN_API_KEY),
        _tool("trigger_workflow_dry_run"),
    )

    assert decision.decision != PolicyDecisionType.ALLOW
    assert decision.decision == PolicyDecisionType.REQUIRE_APPROVAL


def test_identity_missing_required_low_risk_scope_gets_denied() -> None:
    identity = _identity(VIEWER_API_KEY)
    tool = ToolSpec(
        name="custom_low_risk_tool",
        description="Custom low-risk tool.",
        required_scopes=["tools:custom_low"],
        risk_level=RiskLevel.LOW,
    )

    decision = evaluate_tool_permission(identity, tool)

    assert decision.decision == PolicyDecisionType.DENY
    assert decision.missing_scopes == ["tools:custom_low"]


def test_identity_missing_required_medium_risk_scope_gets_denied() -> None:
    identity = _identity(VIEWER_API_KEY)
    tool = ToolSpec(
        name="custom_medium_risk_tool",
        description="Custom medium-risk tool.",
        required_scopes=["tools:custom_medium"],
        risk_level=RiskLevel.MEDIUM,
    )

    decision = evaluate_tool_permission(identity, tool)

    assert decision.decision == PolicyDecisionType.DENY
    assert decision.missing_scopes == ["tools:custom_medium"]


def test_decision_shape_includes_required_fields() -> None:
    decision = evaluate_tool_permission(
        _identity(VIEWER_API_KEY),
        _tool("draft_issue_comment"),
    )

    assert decision.tool_name == "draft_issue_comment"
    assert decision.reason
    assert decision.required_scopes == ["tools:draft"]
    assert decision.missing_scopes == ["tools:draft"]
    assert decision.decision in {
        PolicyDecisionType.ALLOW,
        PolicyDecisionType.DENY,
        PolicyDecisionType.REQUIRE_APPROVAL,
    }


def test_high_risk_tool_never_returns_allow() -> None:
    for api_key in [VIEWER_API_KEY, OPERATOR_API_KEY, ADMIN_API_KEY]:
        decision = evaluate_tool_permission(
            _identity(api_key),
            _tool("trigger_workflow_dry_run"),
        )

        assert decision.decision != PolicyDecisionType.ALLOW


def test_policy_guard_does_not_execute_tools() -> None:
    tool = _tool("trigger_workflow_dry_run")

    decision = evaluate_tool_permission(_identity(ADMIN_API_KEY), tool)

    assert decision.tool_name == "trigger_workflow_dry_run"
    assert not hasattr(decision, "result")
    assert not hasattr(decision, "dry_run")