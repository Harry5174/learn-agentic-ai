import pytest
from pydantic import ValidationError

from app.skills.argument_schemas import (
    FORBIDDEN_ARGUMENT_NAMES,
    ArgumentValidationIssue,
    ArgumentValidationStatus,
    ArgumentValueType,
    ProposedStepArguments,
    ToolArgumentSpec,
    ValidatedSkillPlan,
    ValidatedStepArguments,
)


def test_tool_argument_spec_accepts_scalar_value_types() -> None:
    specs = [
        ToolArgumentSpec(name="repository", value_type=ArgumentValueType.STRING),
        ToolArgumentSpec(name="issue_id", value_type=ArgumentValueType.INTEGER),
        ToolArgumentSpec(name="dry_run", value_type=ArgumentValueType.BOOLEAN),
    ]

    assert [spec.value_type for spec in specs] == [
        ArgumentValueType.STRING,
        ArgumentValueType.INTEGER,
        ArgumentValueType.BOOLEAN,
    ]


def test_tool_argument_spec_rejects_object_and_list_value_types() -> None:
    with pytest.raises(ValidationError):
        ToolArgumentSpec(name="payload", value_type="object")

    with pytest.raises(ValidationError):
        ToolArgumentSpec(name="items", value_type="list")


def test_tool_argument_spec_forbids_extra_fields() -> None:
    with pytest.raises(ValidationError):
        ToolArgumentSpec(
            name="repository",
            value_type=ArgumentValueType.STRING,
            unexpected=True,
        )


def test_proposed_step_arguments_store_raw_untrusted_arguments() -> None:
    proposed = ProposedStepArguments(
        step_id="draft_comment",
        arguments={
            "issue_id": 1,
            "comment_body": "Draft a response.",
            "raw_payload": {"nested": ["untrusted", "not_validated"]},
        },
    )

    assert proposed.step_id == "draft_comment"
    assert proposed.arguments["raw_payload"] == {
        "nested": ["untrusted", "not_validated"]
    }


def test_proposed_step_arguments_forbid_extra_top_level_fields() -> None:
    with pytest.raises(ValidationError):
        ProposedStepArguments(
            step_id="draft_comment",
            arguments={"issue_id": 1},
            tool_name="draft_issue_comment",
        )


def test_validated_step_arguments_store_only_scalar_arguments() -> None:
    validated = ValidatedStepArguments(
        step_id="simulate_workflow",
        arguments={
            "workflow_name": "ci.yml",
            "attempt": 1,
            "dry_run": True,
        },
    )

    assert validated.arguments == {
        "workflow_name": "ci.yml",
        "attempt": 1,
        "dry_run": True,
    }


def test_validated_step_arguments_reject_object_and_list_values() -> None:
    with pytest.raises(ValidationError):
        ValidatedStepArguments(
            step_id="simulate_workflow",
            arguments={"payload": {"ref": "main"}},
        )

    with pytest.raises(ValidationError):
        ValidatedStepArguments(
            step_id="simulate_workflow",
            arguments={"refs": ["main"]},
        )


def test_validated_skill_plan_supports_accepted_and_rejected_only() -> None:
    accepted = ValidatedSkillPlan(
        status=ArgumentValidationStatus.ACCEPTED,
        skill_id="inspect_sandbox_health",
        skill_version="1.0",
        step_arguments=[
            ValidatedStepArguments(
                step_id="inspect_issues",
                arguments={"repository": "sandbox/demo-repo"},
            )
        ],
    )
    rejected = ValidatedSkillPlan(
        status=ArgumentValidationStatus.REJECTED,
        skill_id="inspect_sandbox_health",
        skill_version="1.0",
        issues=[
            ArgumentValidationIssue(
                reason_code="forbidden_argument_name",
                argument_name="identity",
                message="Argument name is reserved for the harness.",
            )
        ],
    )

    assert accepted.status == ArgumentValidationStatus.ACCEPTED
    assert rejected.status == ArgumentValidationStatus.REJECTED


def test_validated_skill_plan_rejects_partially_accepted_status() -> None:
    with pytest.raises(ValidationError):
        ValidatedSkillPlan(
            status="partially_accepted",
            skill_id="inspect_sandbox_health",
            skill_version="1.0",
        )


def test_argument_validation_issue_carries_safe_reason_and_message() -> None:
    issue = ArgumentValidationIssue(
        step_id="inspect_issues",
        argument_name="identity",
        reason_code="forbidden_argument_name",
        message="Argument name is reserved for the harness.",
    )

    assert issue.step_id == "inspect_issues"
    assert issue.argument_name == "identity"
    assert issue.reason_code == "forbidden_argument_name"
    assert issue.message == "Argument name is reserved for the harness."


def test_forbidden_argument_names_include_identity_and_control_plane_fields() -> None:
    assert {
        "user_id",
        "role",
        "scopes",
        "identity",
        "api_key",
        "approval_decision",
        "policy_override",
        "risk_level",
        "tool_name",
        "skill_id",
        "skill_version",
    }.issubset(FORBIDDEN_ARGUMENT_NAMES)


def test_sensitive_argument_spec_can_be_marked_sensitive() -> None:
    spec = ToolArgumentSpec(
        name="comment_body",
        value_type=ArgumentValueType.STRING,
        sensitive=True,
        notes="May contain user-provided text in future integrations.",
    )

    assert spec.sensitive is True


def test_redacted_argument_names_are_representable_on_validated_step_arguments() -> None:
    validated = ValidatedStepArguments(
        step_id="draft_comment",
        arguments={"comment_body": "Safe local demo text."},
        redacted_argument_names=["comment_body"],
    )

    assert validated.redacted_argument_names == ["comment_body"]
