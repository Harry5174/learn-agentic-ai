import pytest
from pydantic import ValidationError

from app.skills.argument_schemas import ArgumentValueType, ToolArgumentSpec
from app.skills.schemas import (
    SkillProposal,
    SkillProposalStep,
    SkillRunResult,
    SkillRunStatus,
    SkillSpec,
    SkillStep,
)
from app.tools.schemas import RiskLevel, ToolExecutionResult


def test_skill_step_creates_successfully() -> None:
    step = SkillStep(
        step_id="inspect_issues",
        description="Inspect sandbox issues.",
        tool_name="inspect_sandbox_issues",
        allowed_args_schema={
            "type": "object",
            "properties": {"repository": {"type": "string"}},
        },
        required_scopes=["tools:inspect"],
        risk_level=RiskLevel.LOW,
    )

    assert step.step_id == "inspect_issues"
    assert step.tool_name == "inspect_sandbox_issues"
    assert step.required_scopes == ["tools:inspect"]
    assert step.risk_level == RiskLevel.LOW


def test_skill_spec_creates_successfully() -> None:
    step = SkillStep(
        step_id="draft_comment",
        description="Draft a dry-run comment.",
        tool_name="draft_issue_comment",
        required_scopes=["tools:draft"],
        risk_level=RiskLevel.MEDIUM,
    )

    spec = SkillSpec(
        skill_id="draft_sandbox_issue_comment",
        version="1.0",
        name="Draft sandbox issue comment",
        description="Draft an issue comment without posting it.",
        steps=[step],
        required_scopes=["tools:draft"],
        risk_level=RiskLevel.MEDIUM,
        tags=["draft"],
    )

    assert spec.skill_id == "draft_sandbox_issue_comment"
    assert spec.steps == [step]
    assert spec.allowed_tool_names == ["draft_issue_comment"]
    assert spec.tags == ["draft"]


def test_skill_proposal_creates_successfully() -> None:
    step = SkillProposalStep(
        step_id="simulate_workflow",
        description="Simulate a workflow trigger.",
        tool_name="trigger_workflow_dry_run",
        required_scopes=["tools:trigger_workflow"],
        risk_level=RiskLevel.HIGH,
        arguments={"workflow_name": "ci.yml", "ref": "main"},
    )

    proposal = SkillProposal(
        proposed_skill_id="simulate_sandbox_workflow",
        proposed_skill_version="1.0",
        rationale="The user asked to see what would happen.",
        steps=[step],
    )

    assert proposal.proposed_skill_id == "simulate_sandbox_workflow"
    assert proposal.proposed_skill_version == "1.0"
    assert proposal.steps == [step]
    assert proposal.steps[0].arguments == {"workflow_name": "ci.yml", "ref": "main"}


def test_skill_run_result_creates_successfully() -> None:
    tool_result = ToolExecutionResult(
        tool_name="inspect_sandbox_issues",
        success=True,
        result={"issues": []},
        dry_run=True,
    )

    result = SkillRunResult(
        run_id="run-123",
        status=SkillRunStatus.COMPLETED,
        skill_id="inspect_sandbox_health",
        skill_version="1.0",
        step_results=[tool_result],
        message="Skill completed.",
    )

    assert result.run_id == "run-123"
    assert result.status == SkillRunStatus.COMPLETED
    assert result.step_results == [tool_result]


def test_invalid_skill_run_status_fails() -> None:
    with pytest.raises(ValidationError):
        SkillRunResult(
            run_id="run-123",
            status="paused",
            skill_id="inspect_sandbox_health",
            skill_version="1.0",
        )


def test_mutable_defaults_are_not_shared() -> None:
    first_step = SkillStep(
        step_id="step_one",
        description="First step.",
        tool_name="inspect_sandbox_issues",
        risk_level=RiskLevel.LOW,
    )
    second_step = SkillStep(
        step_id="step_two",
        description="Second step.",
        tool_name="inspect_sandbox_issues",
        risk_level=RiskLevel.LOW,
    )

    first_step.required_scopes.append("tools:inspect")
    first_step.allowed_args_schema["repository"] = "sandbox/demo-repo"
    argument_spec = ToolArgumentSpec(
        name="repository",
        value_type=ArgumentValueType.STRING,
    )
    first_step.argument_specs.append(argument_spec)

    assert first_step.required_scopes == ["tools:inspect"]
    assert second_step.required_scopes == []
    assert first_step.allowed_args_schema == {"repository": "sandbox/demo-repo"}
    assert second_step.allowed_args_schema == {}
    assert first_step.argument_specs == [argument_spec]
    assert second_step.argument_specs == []


def test_skill_proposal_step_argument_defaults_are_not_shared() -> None:
    first_step = SkillProposalStep(
        step_id="step_one",
        description="First step.",
        tool_name="inspect_sandbox_issues",
        risk_level=RiskLevel.LOW,
    )
    second_step = SkillProposalStep(
        step_id="step_two",
        description="Second step.",
        tool_name="inspect_sandbox_issues",
        risk_level=RiskLevel.LOW,
    )

    first_step.arguments["repository"] = "sandbox/demo-repo"

    assert first_step.arguments == {"repository": "sandbox/demo-repo"}
    assert second_step.arguments == {}
