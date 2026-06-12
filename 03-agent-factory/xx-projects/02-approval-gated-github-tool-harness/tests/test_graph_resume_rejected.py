from langgraph.types import Command

from app.approval.schemas import ApprovalDecision, ApprovalStatus
from app.audit.schemas import AuditEventType
from app.graph.builder import build_harness_graph
from app.identity.config import ADMIN_API_KEY, OPERATOR_API_KEY, VIEWER_API_KEY
from app.identity.resolver import resolve_identity_from_api_key
from app.identity.schemas import Role
from app.state.schemas import TaskStatus


def _config(task_id: str) -> dict:
    """Build a LangGraph config with a unique thread_id."""
    return {"configurable": {"thread_id": task_id}}


def _pause_graph_for_operator(graph, task_id: str, config: dict) -> None:
    """Helper: submit a high-risk task as operator and pause the graph."""
    operator_identity = resolve_identity_from_api_key(OPERATOR_API_KEY)
    graph.invoke(
        {
            "task_id": task_id,
            "user_query": "trigger workflow",
            "identity": operator_identity,
            "audit_trail": [],
        },
        config=config,
    )


def test_admin_rejects_high_risk_task() -> None:
    """Admin rejects a high-risk task; tool does not execute."""
    graph = build_harness_graph()
    task_id = "task-resume-rejected-1"
    config = _config(task_id)

    admin_identity = resolve_identity_from_api_key(ADMIN_API_KEY)

    _pause_graph_for_operator(graph, task_id, config)

    snapshot = graph.get_state(config)
    assert snapshot.values["status"] == TaskStatus.PAUSED_FOR_APPROVAL

    rejection = ApprovalDecision(
        task_id=task_id,
        tool_name="trigger_workflow_dry_run",
        status=ApprovalStatus.REJECTED,
        decided_by=admin_identity.user_id,
        decider_role=Role.ADMIN,
        reason="Rejected: not appropriate for current sprint.",
    )

    result = graph.invoke(
        Command(
            resume={
                "approval_decision": rejection.model_dump(mode="json"),
                "approval_actor": admin_identity.model_dump(mode="json"),
            }
        ),
        config=config,
    )

    assert result["status"] == TaskStatus.REJECTED
    assert result.get("tool_result") is None
    assert result["final_report"].startswith("Task rejected:")


def test_admin_rejection_audit_trail() -> None:
    """Rejection audit trail contains APPROVAL_REJECTED but not TOOL_EXECUTED."""
    graph = build_harness_graph()
    task_id = "task-resume-rejected-2"
    config = _config(task_id)

    admin_identity = resolve_identity_from_api_key(ADMIN_API_KEY)

    _pause_graph_for_operator(graph, task_id, config)

    rejection = ApprovalDecision(
        task_id=task_id,
        tool_name="trigger_workflow_dry_run",
        status=ApprovalStatus.REJECTED,
        decided_by=admin_identity.user_id,
        decider_role=Role.ADMIN,
        reason="Rejected.",
    )

    result = graph.invoke(
        Command(
            resume={
                "approval_decision": rejection.model_dump(mode="json"),
                "approval_actor": admin_identity.model_dump(mode="json"),
            }
        ),
        config=config,
    )

    event_types = [event.event_type for event in result["audit_trail"]]

    assert AuditEventType.APPROVAL_REJECTED in event_types
    assert AuditEventType.TOOL_EXECUTED not in event_types
    assert AuditEventType.TASK_COMPLETED not in event_types


def test_operator_cannot_approve_high_risk_task() -> None:
    """Operator lacks approval:approve scope; tool must not execute."""
    graph = build_harness_graph()
    task_id = "task-resume-invalid-operator-1"
    config = _config(task_id)

    operator_identity = resolve_identity_from_api_key(OPERATOR_API_KEY)

    _pause_graph_for_operator(graph, task_id, config)

    approval = ApprovalDecision(
        task_id=task_id,
        tool_name="trigger_workflow_dry_run",
        status=ApprovalStatus.APPROVED,
        decided_by=operator_identity.user_id,
        decider_role=Role.OPERATOR,
        reason="Operator attempting to approve.",
    )

    result = graph.invoke(
        Command(
            resume={
                "approval_decision": approval.model_dump(mode="json"),
                "approval_actor": operator_identity.model_dump(mode="json"),
            }
        ),
        config=config,
    )

    assert result["status"] == TaskStatus.FAILED
    assert result.get("tool_result") is None
    assert "approval:approve" in result.get("resume_error", "")

    event_types = [event.event_type for event in result["audit_trail"]]
    assert AuditEventType.TOOL_EXECUTED not in event_types


def test_viewer_cannot_approve_high_risk_task() -> None:
    """Viewer lacks approval:approve scope; tool must not execute."""
    graph = build_harness_graph()
    task_id = "task-resume-invalid-viewer-1"
    config = _config(task_id)

    viewer_identity = resolve_identity_from_api_key(VIEWER_API_KEY)

    _pause_graph_for_operator(graph, task_id, config)

    approval = ApprovalDecision(
        task_id=task_id,
        tool_name="trigger_workflow_dry_run",
        status=ApprovalStatus.APPROVED,
        decided_by=viewer_identity.user_id,
        decider_role=Role.VIEWER,
        reason="Viewer attempting to approve.",
    )

    result = graph.invoke(
        Command(
            resume={
                "approval_decision": approval.model_dump(mode="json"),
                "approval_actor": viewer_identity.model_dump(mode="json"),
            }
        ),
        config=config,
    )

    assert result["status"] == TaskStatus.FAILED
    assert result.get("tool_result") is None
    assert "approval:approve" in result.get("resume_error", "")

    event_types = [event.event_type for event in result["audit_trail"]]
    assert AuditEventType.TOOL_EXECUTED not in event_types


def test_viewer_cannot_reject_high_risk_task() -> None:
    """Viewer lacks approval:reject scope; rejection must fail."""
    graph = build_harness_graph()
    task_id = "task-resume-invalid-viewer-reject-1"
    config = _config(task_id)

    viewer_identity = resolve_identity_from_api_key(VIEWER_API_KEY)

    _pause_graph_for_operator(graph, task_id, config)

    rejection = ApprovalDecision(
        task_id=task_id,
        tool_name="trigger_workflow_dry_run",
        status=ApprovalStatus.REJECTED,
        decided_by=viewer_identity.user_id,
        decider_role=Role.VIEWER,
        reason="Viewer attempting to reject.",
    )

    result = graph.invoke(
        Command(
            resume={
                "approval_decision": rejection.model_dump(mode="json"),
                "approval_actor": viewer_identity.model_dump(mode="json"),
            }
        ),
        config=config,
    )

    assert result["status"] == TaskStatus.FAILED
    assert result.get("tool_result") is None
    assert "approval:reject" in result.get("resume_error", "")

    event_types = [event.event_type for event in result["audit_trail"]]
    assert AuditEventType.TOOL_EXECUTED not in event_types
