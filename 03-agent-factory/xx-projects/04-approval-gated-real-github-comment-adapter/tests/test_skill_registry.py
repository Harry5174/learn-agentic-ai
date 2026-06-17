import pytest

from app.skills.errors import UnknownSkillError
from app.skills.registry import build_default_skill_registry
from app.tools.registry import build_default_tool_registry
from app.tools.schemas import RiskLevel


def test_default_registry_includes_a3_3_github_comment_skill() -> None:
    registry = build_default_skill_registry()

    skill_ids = {skill.skill_id for skill in registry.list_skills()}

    assert skill_ids == {
        "inspect_sandbox_health",
        "draft_sandbox_issue_comment",
        "simulate_sandbox_workflow",
        "post_github_issue_comment",
    }


def test_get_skill_returns_skill_by_id() -> None:
    registry = build_default_skill_registry()

    skill = registry.get_skill("draft_sandbox_issue_comment")

    assert skill.skill_id == "draft_sandbox_issue_comment"
    assert skill.version == "1.0"
    assert skill.allowed_tool_names == ["draft_issue_comment"]


def test_get_skill_returns_skill_by_id_and_version() -> None:
    registry = build_default_skill_registry()

    skill = registry.get_skill("simulate_sandbox_workflow", version="1.0")

    assert skill.skill_id == "simulate_sandbox_workflow"
    assert skill.version == "1.0"
    assert skill.risk_level == RiskLevel.HIGH


def test_has_skill_reports_success_and_failure() -> None:
    registry = build_default_skill_registry()

    assert registry.has_skill("inspect_sandbox_health") is True
    assert registry.has_skill("inspect_sandbox_health", version="1.0") is True
    assert registry.has_skill("inspect_sandbox_health", version="2.0") is False
    assert registry.has_skill("not_registered") is False


def test_unknown_skill_raises_custom_error() -> None:
    registry = build_default_skill_registry()

    with pytest.raises(UnknownSkillError, match="Unknown skill: not_registered"):
        registry.get_skill("not_registered")


def test_builtin_skills_reference_known_dry_run_tool_names() -> None:
    skill_registry = build_default_skill_registry()
    tool_registry = build_default_tool_registry()
    known_tool_names = {tool.name for tool in tool_registry.list_tools()}

    for skill in skill_registry.list_skills():
        assert set(skill.allowed_tool_names).issubset(known_tool_names)


def test_registry_exposes_allowed_tools_required_scopes_and_risk() -> None:
    registry = build_default_skill_registry()

    inspect_skill = registry.get_skill("inspect_sandbox_health")
    draft_skill = registry.get_skill("draft_sandbox_issue_comment")
    workflow_skill = registry.get_skill("simulate_sandbox_workflow")
    github_skill = registry.get_skill("post_github_issue_comment")

    assert inspect_skill.allowed_tool_names == ["inspect_sandbox_issues"]
    assert inspect_skill.required_scopes == ["tools:inspect"]
    assert inspect_skill.risk_level == RiskLevel.LOW

    assert draft_skill.allowed_tool_names == ["draft_issue_comment"]
    assert draft_skill.required_scopes == ["tools:draft"]
    assert draft_skill.risk_level == RiskLevel.MEDIUM

    assert workflow_skill.allowed_tool_names == ["trigger_workflow_dry_run"]
    assert workflow_skill.required_scopes == ["tools:trigger_workflow"]
    assert workflow_skill.risk_level == RiskLevel.HIGH

    assert github_skill.allowed_tool_names == ["post_github_issue_comment"]
    assert github_skill.required_scopes == ["tools:post_github_comment"]
    assert github_skill.risk_level == RiskLevel.HIGH


def test_registry_exposes_step_metadata() -> None:
    registry = build_default_skill_registry()

    skill = registry.get_skill("simulate_sandbox_workflow")
    step = skill.steps[0]

    assert step.step_id == "simulate_workflow"
    assert step.tool_name == "trigger_workflow_dry_run"
    assert step.required_scopes == ["tools:trigger_workflow"]
    assert step.risk_level == RiskLevel.HIGH
