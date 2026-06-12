import pytest

from app.tools.errors import UnknownToolError
from app.tools.registry import build_default_tool_registry
from app.tools.schemas import RiskLevel


def test_default_registry_includes_exactly_three_tools() -> None:
    registry = build_default_tool_registry()

    tool_names = {tool.name for tool in registry.list_tools()}

    assert tool_names == {
        "inspect_sandbox_issues",
        "draft_issue_comment",
        "trigger_workflow_dry_run",
    }


def test_post_github_issue_comment_is_not_registered_yet() -> None:
    registry = build_default_tool_registry()

    tool_names = {tool.name for tool in registry.list_tools()}

    assert "post_github_issue_comment" not in tool_names


def test_list_tools_returns_metadata_for_all_tools() -> None:
    registry = build_default_tool_registry()

    tools = registry.list_tools()

    assert len(tools) == 3
    assert all(tool.name for tool in tools)
    assert all(tool.description for tool in tools)
    assert all(tool.required_scopes for tool in tools)
    assert all(tool.risk_level for tool in tools)


def test_get_tool_returns_correct_tool_spec() -> None:
    registry = build_default_tool_registry()

    tool = registry.get_tool("draft_issue_comment")

    assert tool.name == "draft_issue_comment"
    assert tool.required_scopes == ["tools:draft"]
    assert tool.risk_level == RiskLevel.MEDIUM


def test_unknown_tool_raises_custom_error() -> None:
    registry = build_default_tool_registry()

    with pytest.raises(UnknownToolError, match="Unknown tool"):
        registry.get_tool("not_registered")


def test_tool_metadata_includes_required_scopes() -> None:
    registry = build_default_tool_registry()

    inspect_tool = registry.get_tool("inspect_sandbox_issues")
    draft_tool = registry.get_tool("draft_issue_comment")
    workflow_tool = registry.get_tool("trigger_workflow_dry_run")

    assert inspect_tool.required_scopes == ["tools:inspect"]
    assert draft_tool.required_scopes == ["tools:draft"]
    assert workflow_tool.required_scopes == ["tools:trigger_workflow"]


def test_high_risk_tool_is_marked_high() -> None:
    registry = build_default_tool_registry()

    tool = registry.get_tool("trigger_workflow_dry_run")

    assert tool.risk_level == RiskLevel.HIGH


def test_registry_executes_registered_tool_by_name() -> None:
    registry = build_default_tool_registry()

    result = registry.execute("inspect_sandbox_issues", arguments={})

    assert result.tool_name == "inspect_sandbox_issues"
    assert result.success is True
    assert result.dry_run is True


def test_registry_cannot_execute_unregistered_tool() -> None:
    registry = build_default_tool_registry()

    with pytest.raises(UnknownToolError, match="Unknown tool"):
        registry.execute("not_registered", arguments={})


def test_registry_execution_requires_explicit_tool_name() -> None:
    registry = build_default_tool_registry()

    with pytest.raises(UnknownToolError, match="Unknown tool"):
        registry.execute("", arguments={})


def test_registry_does_not_perform_policy_or_permission_checks() -> None:
    registry = build_default_tool_registry()

    result = registry.execute(
        "trigger_workflow_dry_run",
        arguments={"workflow_name": "ci.yml", "ref": "main"},
    )

    assert result.success is True
    assert result.dry_run is True
    assert result.result["would_trigger"] is False
