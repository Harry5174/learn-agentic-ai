import pytest
from pydantic import ValidationError

from app.tools.schemas import RiskLevel, ToolCallRequest, ToolSpec


def test_valid_tool_spec_creates_successfully() -> None:
    spec = ToolSpec(
        name="github_create_issue",
        description="Create a GitHub issue in dry-run mode.",
        required_scopes=["github:issues:write"],
        risk_level=RiskLevel.HIGH,
    )

    assert spec.name == "github_create_issue"
    assert spec.required_scopes == ["github:issues:write"]
    assert spec.risk_level == RiskLevel.HIGH


def test_valid_tool_call_request_creates_successfully() -> None:
    request = ToolCallRequest(
        tool_name="github_list_issues",
        arguments={"repo": "owner/project"},
        risk_level=RiskLevel.LOW,
    )

    assert request.tool_name == "github_list_issues"
    assert request.arguments == {"repo": "owner/project"}
    assert request.risk_level == RiskLevel.LOW


def test_invalid_risk_level_fails() -> None:
    with pytest.raises(ValidationError):
        ToolSpec(
            name="dangerous_tool",
            description="Invalid risk level test.",
            required_scopes=[],
            risk_level="critical",
        )


def test_mutable_defaults_are_not_shared() -> None:
    first_spec = ToolSpec(
        name="tool_one",
        description="First tool.",
        risk_level=RiskLevel.LOW,
    )
    second_spec = ToolSpec(
        name="tool_two",
        description="Second tool.",
        risk_level=RiskLevel.LOW,
    )

    first_spec.required_scopes.append("scope:one")

    assert first_spec.required_scopes == ["scope:one"]
    assert second_spec.required_scopes == []

    first_request = ToolCallRequest(tool_name="tool_one")
    second_request = ToolCallRequest(tool_name="tool_two")

    first_request.arguments["value"] = 1

    assert first_request.arguments == {"value": 1}
    assert second_request.arguments == {}