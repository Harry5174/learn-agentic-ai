from datetime import datetime

import pytest
from pydantic import ValidationError

from app.identity.schemas import Role
from app.skills.schemas import (
    ProposalAuditEvent,
    ProposalValidationStatus,
    SkillStep,
)
from app.tools.schemas import RiskLevel


def test_proposal_audit_event_creates_successfully() -> None:
    step = SkillStep(
        step_id="draft_comment",
        description="Draft a comment.",
        tool_name="draft_issue_comment",
        required_scopes=["tools:draft"],
        risk_level=RiskLevel.MEDIUM,
    )

    event = ProposalAuditEvent(
        task_id="task-123",
        user_id="user-123",
        role=Role.OPERATOR,
        scopes=["tools:draft"],
        proposed_skill_id="draft_sandbox_issue_comment",
        proposed_skill_version="1.0",
        proposed_steps=[step],
        proposed_tool_names=["draft_issue_comment"],
        validation_status=ProposalValidationStatus.NOT_VALIDATED,
        rejection_reasons=[],
        risk_level=RiskLevel.MEDIUM,
        approval_required=True,
    )

    assert event.task_id == "task-123"
    assert event.user_id == "user-123"
    assert event.role == Role.OPERATOR
    assert event.scopes == ["tools:draft"]
    assert event.proposed_tool_names == ["draft_issue_comment"]
    assert event.validation_status == ProposalValidationStatus.NOT_VALIDATED
    assert event.approval_required is True


def test_proposal_audit_event_defaults_to_not_validated() -> None:
    step = SkillStep(
        step_id="inspect_issues",
        description="Inspect issues.",
        tool_name="inspect_sandbox_issues",
        required_scopes=["tools:inspect"],
        risk_level=RiskLevel.LOW,
    )

    event = ProposalAuditEvent(
        task_id="task-123",
        user_id="user-123",
        role=Role.VIEWER,
        scopes=["tools:inspect"],
        proposed_skill_id="inspect_sandbox_health",
        proposed_skill_version="1.0",
        proposed_steps=[step],
        risk_level=RiskLevel.LOW,
        approval_required=False,
    )

    assert event.validation_status == ProposalValidationStatus.NOT_VALIDATED
    assert event.proposed_tool_names == []
    assert event.rejection_reasons == []


def test_proposal_audit_event_can_capture_rejection_reasons() -> None:
    step = SkillStep(
        step_id="simulate_workflow",
        description="Simulate workflow.",
        tool_name="trigger_workflow_dry_run",
        required_scopes=["tools:trigger_workflow"],
        risk_level=RiskLevel.HIGH,
    )

    event = ProposalAuditEvent(
        task_id="task-123",
        user_id="user-123",
        role=Role.VIEWER,
        scopes=["tools:inspect"],
        proposed_skill_id="simulate_sandbox_workflow",
        proposed_skill_version="1.0",
        proposed_steps=[step],
        proposed_tool_names=["trigger_workflow_dry_run"],
        validation_status=ProposalValidationStatus.REJECTED,
        rejection_reasons=["Missing scope: tools:trigger_workflow"],
        risk_level=RiskLevel.HIGH,
        approval_required=True,
    )

    assert event.validation_status == ProposalValidationStatus.REJECTED
    assert event.rejection_reasons == ["Missing scope: tools:trigger_workflow"]
    assert event.risk_level == RiskLevel.HIGH


def test_proposal_validation_status_allows_expected_values() -> None:
    assert ProposalValidationStatus.NOT_VALIDATED == "not_validated"
    assert ProposalValidationStatus.ACCEPTED == "accepted"
    assert ProposalValidationStatus.REJECTED == "rejected"


def test_invalid_proposal_validation_status_fails() -> None:
    with pytest.raises(ValidationError):
        ProposalAuditEvent(
            task_id="task-123",
            user_id="user-123",
            role=Role.OPERATOR,
            proposed_skill_id="draft_sandbox_issue_comment",
            proposed_skill_version="1.0",
            proposed_steps=[],
            validation_status="maybe",
            risk_level=RiskLevel.MEDIUM,
            approval_required=True,
        )


def test_proposal_audit_timestamp_is_timezone_aware() -> None:
    event = ProposalAuditEvent(
        task_id="task-123",
        user_id="user-123",
        role=Role.ADMIN,
        proposed_skill_id="inspect_sandbox_health",
        proposed_skill_version="1.0",
        proposed_steps=[],
        risk_level=RiskLevel.LOW,
        approval_required=False,
    )

    assert isinstance(event.timestamp, datetime)
    assert event.timestamp.tzinfo is not None
    assert event.timestamp.utcoffset() is not None
