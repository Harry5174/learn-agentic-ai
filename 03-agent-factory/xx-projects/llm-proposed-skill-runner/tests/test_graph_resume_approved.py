from langgraph.types import Command

from app.approval.schemas import ApprovalDecision, ApprovalStatus
from app.audit.schemas import AuditEventType
from app.graph.builder import build_harness_graph
from app.identity.config import ADMIN_API_KEY, OPERATOR_API_KEY
from app.identity.resolver import resolve_identity_from_api_key
from app.identity.schemas import Role
from app.state.schemas import TaskStatus


def _config(task_id: str) -> dict:
    """Build a LangGraph config with a unique thread_id."""
    return {"configurable": {"thread_id": task_id}}


def test_admin_approves_operator_high_risk_task() -> None:
    """Admin approves an operator-submitted high-risk task; tool executes."""
    graph = build_harness_graph()
    task_id = "task-resume-approved-1"
    config = _config(task_id)

    operator_identity = resolve_identity_from_api_key(OPERATOR_API_KEY)
    admin_identity = resolve_identity_from_api_key(ADMIN_API_KEY)

    # Phase 1: operator submits high-risk task → graph pauses
    graph.invoke(
        {
            "task_id": task_id,
            "user_query": "trigger workflow",
            "identity": operator_identity,
            "audit_trail": [],
        },
        config=config,
    )

    snapshot = graph.get_state(config)
    assert snapshot.values["status"] == TaskStatus.PAUSED_FOR_APPROVAL

    # Phase 2: admin resumes with approval
    approval_decision = ApprovalDecision(
        task_id=task_id,
        tool_name="trigger_workflow_dry_run",
        status=ApprovalStatus.APPROVED,
        decided_by=admin_identity.user_id,
        decider_role=Role.ADMIN,
        reason="Approved by admin for dry-run execution.",
    )

    result = graph.invoke(
        Command(
            resume={
                "approval_decision": approval_decision.model_dump(mode="json"),
                "approval_actor": admin_identity.model_dump(mode="json"),
            }
        ),
        config=config,
    )

    assert result["status"] == TaskStatus.COMPLETED
    assert result["tool_result"] is not None
    assert result["tool_result"].tool_name == "trigger_workflow_dry_run"
    assert result["tool_result"].dry_run is True
    assert result["tool_result"].success is True


def test_admin_approval_audit_trail_is_complete() -> None:
    """After admin approval and execution, audit trail contains all events."""
    graph = build_harness_graph()
    task_id = "task-resume-approved-2"
    config = _config(task_id)

    operator_identity = resolve_identity_from_api_key(OPERATOR_API_KEY)
    admin_identity = resolve_identity_from_api_key(ADMIN_API_KEY)

    graph.invoke(
        {
            "task_id": task_id,
            "user_query": "trigger workflow",
            "identity": operator_identity,
            "audit_trail": [],
        },
        config=config,
    )

    approval_decision = ApprovalDecision(
        task_id=task_id,
        tool_name="trigger_workflow_dry_run",
        status=ApprovalStatus.APPROVED,
        decided_by=admin_identity.user_id,
        decider_role=Role.ADMIN,
        reason="Approved.",
    )

    result = graph.invoke(
        Command(
            resume={
                "approval_decision": approval_decision.model_dump(mode="json"),
                "approval_actor": admin_identity.model_dump(mode="json"),
            }
        ),
        config=config,
    )

    event_types = [event.event_type for event in result["audit_trail"]]

    assert AuditEventType.TASK_CREATED in event_types
    assert AuditEventType.TOOL_SELECTED in event_types
    assert AuditEventType.PERMISSION_CHECKED in event_types
    assert AuditEventType.APPROVAL_REQUESTED in event_types
    assert AuditEventType.APPROVAL_GRANTED in event_types
    assert AuditEventType.TOOL_EXECUTED in event_types
    assert AuditEventType.TASK_COMPLETED in event_types


def test_admin_approves_admin_submitted_high_risk_task() -> None:
    """Admin submits and another admin-scope user approves; tool executes."""
    graph = build_harness_graph()
    task_id = "task-resume-approved-3"
    config = _config(task_id)

    admin_identity = resolve_identity_from_api_key(ADMIN_API_KEY)

    graph.invoke(
        {
            "task_id": task_id,
            "user_query": "trigger workflow",
            "identity": admin_identity,
            "audit_trail": [],
        },
        config=config,
    )

    snapshot = graph.get_state(config)
    assert snapshot.values["status"] == TaskStatus.PAUSED_FOR_APPROVAL

    approval_decision = ApprovalDecision(
        task_id=task_id,
        tool_name="trigger_workflow_dry_run",
        status=ApprovalStatus.APPROVED,
        decided_by=admin_identity.user_id,
        decider_role=Role.ADMIN,
        reason="Self-approved for dry-run.",
    )

    result = graph.invoke(
        Command(
            resume={
                "approval_decision": approval_decision.model_dump(mode="json"),
                "approval_actor": admin_identity.model_dump(mode="json"),
            }
        ),
        config=config,
    )

    assert result["status"] == TaskStatus.COMPLETED
    assert result["tool_result"] is not None
    assert result["tool_result"].success is True
