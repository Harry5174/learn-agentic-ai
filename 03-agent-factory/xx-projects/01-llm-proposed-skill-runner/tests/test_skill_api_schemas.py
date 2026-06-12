from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from app.api.skill_schemas import (
    ProposerMode,
    SkillRunApprovalRequest,
    SkillRunApprovalStatusResponse,
    SkillRunAuditEventResponse,
    SkillRunAuditResponse,
    SkillRunCreateRequest,
    SkillRunErrorResponse,
    SkillRunStatusResponse,
    SkillRunSummaryResponse,
    SkillStepSummaryResponse,
    SkillSummaryResponse,
    SkillValidationStatusResponse,
)
from app.tools.schemas import RiskLevel


def test_skill_run_create_request_exists() -> None:
    request = SkillRunCreateRequest(
        task="Inspect sandbox health.",
        proposer_mode=ProposerMode.FAKE,
        requested_skill_id="inspect_sandbox_health",
    )

    assert request.task == "Inspect sandbox health."
    assert request.proposer_mode == ProposerMode.FAKE
    assert request.requested_skill_id == "inspect_sandbox_health"


def test_skill_run_summary_response_exists() -> None:
    response = SkillRunSummaryResponse(
        run_id="run-123",
        status=SkillRunStatusResponse.COMPLETED,
        task="Inspect sandbox health.",
        proposer_mode=ProposerMode.FAKE,
        selected_skill_id="inspect_sandbox_health",
        selected_skill_version="1.0",
        validation_status=SkillValidationStatusResponse.ACCEPTED,
        approval_required=False,
        approval_status=SkillRunApprovalStatusResponse.NOT_REQUIRED,
        risk_level=RiskLevel.LOW,
        final_report="Skill run completed.",
    )

    assert response.run_id == "run-123"
    assert response.status == SkillRunStatusResponse.COMPLETED
    assert response.final_report == "Skill run completed."


def test_skill_run_approval_request_exists() -> None:
    request = SkillRunApprovalRequest(
        reason="Approved for dry-run execution.",
        comment="Looks safe for the demo.",
    )

    assert request.reason == "Approved for dry-run execution."
    assert request.comment == "Looks safe for the demo."


def test_skill_run_audit_response_exists() -> None:
    event = SkillRunAuditEventResponse(
        event_type="task_created",
        timestamp=datetime.now(timezone.utc),
        message="Skill run was created.",
        metadata={"run_id": "run-123"},
    )
    response = SkillRunAuditResponse(run_id="run-123", events=[event])

    assert response.run_id == "run-123"
    assert response.events == [event]


def test_skill_summary_response_exists() -> None:
    step = SkillStepSummaryResponse(
        step_id="inspect_issues",
        description="Inspect sandbox issues using dry-run data.",
        tool_name="inspect_sandbox_issues",
        risk_level=RiskLevel.LOW,
        required_scopes=["tools:inspect"],
    )
    response = SkillSummaryResponse(
        skill_id="inspect_sandbox_health",
        version="1.0",
        name="Inspect sandbox health",
        description="Inspect predictable sandbox issue status data.",
        required_scopes=["tools:inspect"],
        risk_level=RiskLevel.LOW,
        steps=[step],
    )

    assert response.skill_id == "inspect_sandbox_health"
    assert response.steps == [step]


@pytest.mark.parametrize(
    "forbidden_field",
    [
        "user_id",
        "role",
        "scopes",
        "identity",
        "api_key",
        "api_key_id",
        "policy_decision",
        "risk_override",
        "trusted_tool_names",
    ],
)
def test_create_request_rejects_identity_and_policy_fields(
    forbidden_field: str,
) -> None:
    with pytest.raises(ValidationError):
        SkillRunCreateRequest(
            task="Inspect sandbox health.",
            **{forbidden_field: "attacker-controlled"},
        )


@pytest.mark.parametrize(
    "forbidden_field",
    [
        "user_id",
        "role",
        "scopes",
        "identity",
        "approval_authority",
        "policy_override",
        "approval_decision",
    ],
)
def test_approval_request_rejects_identity_and_authority_fields(
    forbidden_field: str,
) -> None:
    with pytest.raises(ValidationError):
        SkillRunApprovalRequest(
            reason="Please approve this.",
            **{forbidden_field: "attacker-controlled"},
        )


def test_skill_summary_response_can_use_safe_skill_metadata() -> None:
    response = SkillSummaryResponse(
        skill_id="simulate_sandbox_workflow",
        version="1.0",
        name="Simulate sandbox workflow",
        description="Simulate a workflow trigger without executing it.",
        required_scopes=["tools:trigger_workflow"],
        risk_level=RiskLevel.HIGH,
        steps=[
            SkillStepSummaryResponse(
                step_id="simulate_workflow",
                description="Simulate a high-risk workflow trigger.",
                tool_name="trigger_workflow_dry_run",
                risk_level=RiskLevel.HIGH,
                required_scopes=["tools:trigger_workflow"],
            )
        ],
    )
    dumped = response.model_dump()

    assert dumped["skill_id"] == "simulate_sandbox_workflow"
    assert dumped["steps"][0]["tool_name"] == "trigger_workflow_dry_run"
    assert "callable" not in dumped["steps"][0]
    assert "handler" not in dumped["steps"][0]
    assert "allowed_args_schema" not in dumped["steps"][0]


def test_skill_run_summary_does_not_require_graph_or_checkpointer_internals() -> None:
    response = SkillRunSummaryResponse(
        run_id="run-123",
        status=SkillRunStatusResponse.PAUSED_FOR_APPROVAL,
        task="Simulate sandbox workflow.",
        proposer_mode=ProposerMode.FAKE,
        selected_skill_id="simulate_sandbox_workflow",
        selected_skill_version="1.0",
        validation_status=SkillValidationStatusResponse.ACCEPTED,
        approval_required=True,
        approval_status=SkillRunApprovalStatusResponse.PENDING,
        risk_level=RiskLevel.HIGH,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    dumped = response.model_dump()

    assert dumped["run_id"] == "run-123"
    assert "checkpoint" not in dumped
    assert "graph" not in dumped
    assert "identity" not in dumped
    assert "approval_actor" not in dumped


def test_audit_response_is_json_friendly() -> None:
    response = SkillRunAuditResponse(
        run_id="run-123",
        events=[
            SkillRunAuditEventResponse(
                event_type="proposal_validated",
                timestamp=datetime.now(timezone.utc),
                message="Proposal was accepted.",
                metadata={
                    "risk_level": "low",
                    "approval_required": False,
                    "tool_names": ["inspect_sandbox_issues"],
                },
            )
        ],
    )

    dumped_json = response.model_dump_json()

    assert '"run_id":"run-123"' in dumped_json
    assert "proposal_validated" in dumped_json


def test_error_response_does_not_expose_stack_traces() -> None:
    response = SkillRunErrorResponse(
        error_code="skill_run_not_found",
        message="Skill run not found.",
        details={"run_id": "run-123"},
    )
    dumped = response.model_dump()

    assert dumped == {
        "error_code": "skill_run_not_found",
        "message": "Skill run not found.",
        "details": {"run_id": "run-123"},
    }
    assert "stack_trace" not in dumped
    assert "traceback" not in dumped

    with pytest.raises(ValidationError):
        SkillRunErrorResponse(
            error_code="internal_error",
            message="Internal error.",
            stack_trace="Traceback...",
        )


def test_proposer_mode_is_constrained_to_fake_or_llm() -> None:
    fake_request = SkillRunCreateRequest(
        task="Inspect sandbox health.",
        proposer_mode="fake",
    )
    llm_request = SkillRunCreateRequest(
        task="Inspect sandbox health.",
        proposer_mode="llm",
    )

    assert fake_request.proposer_mode == ProposerMode.FAKE
    assert llm_request.proposer_mode == ProposerMode.LLM

    with pytest.raises(ValidationError):
        SkillRunCreateRequest(
            task="Inspect sandbox health.",
            proposer_mode="manual",
        )
