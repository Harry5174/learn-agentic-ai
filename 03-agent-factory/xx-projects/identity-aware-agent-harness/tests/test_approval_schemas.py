import pytest
from pydantic import ValidationError

from app.approval.schemas import (
    ApprovalDecision,
    ApprovalRequest,
    ApprovalStatus,
)
from app.identity.schemas import Role
from app.tools.schemas import RiskLevel


def test_valid_approval_request_creates_successfully() -> None:
    request = ApprovalRequest(
        task_id="task-123",
        tool_name="github_create_issue",
        tool_arguments={"title": "Bug report"},
        risk_level=RiskLevel.HIGH,
        requested_by="user-123",
        reason="High-risk tool requires approval.",
    )

    assert request.task_id == "task-123"
    assert request.risk_level == RiskLevel.HIGH
    assert request.tool_arguments == {"title": "Bug report"}


def test_valid_approval_decision_creates_successfully() -> None:
    decision = ApprovalDecision(
        task_id="task-123",
        tool_name="github_create_issue",
        status=ApprovalStatus.APPROVED,
        decided_by="admin-123",
        decider_role=Role.ADMIN,
        reason="Approved for dry-run execution.",
    )

    assert decision.status == ApprovalStatus.APPROVED
    assert decision.decider_role == Role.ADMIN


def test_invalid_approval_status_fails() -> None:
    with pytest.raises(ValidationError):
        ApprovalDecision(
            task_id="task-123",
            tool_name="github_create_issue",
            status="pending",
            decided_by="admin-123",
            decider_role=Role.ADMIN,
        )


def test_approval_decision_requires_decided_by() -> None:
    with pytest.raises(ValidationError):
        ApprovalDecision(
            task_id="task-123",
            tool_name="github_create_issue",
            status=ApprovalStatus.APPROVED,
            decider_role=Role.ADMIN,
        )


def test_tool_arguments_default_is_not_shared() -> None:
    first = ApprovalRequest(
        task_id="task-1",
        tool_name="tool_one",
        risk_level=RiskLevel.HIGH,
        requested_by="user-1",
        reason="Needs approval.",
    )
    second = ApprovalRequest(
        task_id="task-2",
        tool_name="tool_two",
        risk_level=RiskLevel.HIGH,
        requested_by="user-2",
        reason="Needs approval.",
    )

    first.tool_arguments["value"] = 1

    assert first.tool_arguments == {"value": 1}
    assert second.tool_arguments == {}