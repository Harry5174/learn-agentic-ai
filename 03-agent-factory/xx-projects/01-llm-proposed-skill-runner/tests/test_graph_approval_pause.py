from app.audit.schemas import AuditEventType
from app.graph.builder import build_harness_graph
from app.identity.config import ADMIN_API_KEY, OPERATOR_API_KEY
from app.identity.resolver import resolve_identity_from_api_key
from app.policy.schemas import PolicyDecisionType
from app.state.schemas import TaskStatus
from app.tools.schemas import RiskLevel


def _config(task_id: str) -> dict:
    """Build a LangGraph config with a unique thread_id."""
    return {"configurable": {"thread_id": task_id}}


def test_operator_trigger_workflow_pauses_for_approval() -> None:
    graph = build_harness_graph()
    task_id = "task-approval-operator-1"
    config = _config(task_id)

    graph.invoke(
        {
            "task_id": task_id,
            "user_query": "trigger workflow",
            "identity": resolve_identity_from_api_key(OPERATOR_API_KEY),
            "audit_trail": [],
        },
        config=config,
    )

    snapshot = graph.get_state(config)
    result = snapshot.values

    assert result["selected_tool_name"] == "trigger_workflow_dry_run"
    assert result["policy_decision"].decision == PolicyDecisionType.REQUIRE_APPROVAL
    assert result["approval_request"] is not None
    assert result["approval_request"].tool_name == "trigger_workflow_dry_run"
    assert result["approval_request"].risk_level == RiskLevel.HIGH
    assert result["status"] == TaskStatus.PAUSED_FOR_APPROVAL
    assert result.get("tool_result") is None


def test_operator_trigger_workflow_audit_contains_approval_requested() -> None:
    graph = build_harness_graph()
    task_id = "task-approval-operator-2"
    config = _config(task_id)

    graph.invoke(
        {
            "task_id": task_id,
            "user_query": "trigger workflow",
            "identity": resolve_identity_from_api_key(OPERATOR_API_KEY),
            "audit_trail": [],
        },
        config=config,
    )

    snapshot = graph.get_state(config)
    result = snapshot.values

    event_types = [event.event_type for event in result["audit_trail"]]

    assert AuditEventType.TASK_CREATED in event_types
    assert AuditEventType.TOOL_SELECTED in event_types
    assert AuditEventType.PERMISSION_CHECKED in event_types
    assert AuditEventType.APPROVAL_REQUESTED in event_types
    assert AuditEventType.TOOL_EXECUTED not in event_types
    assert AuditEventType.TASK_COMPLETED not in event_types


def test_admin_trigger_workflow_pauses_for_approval() -> None:
    graph = build_harness_graph()
    task_id = "task-approval-admin-1"
    config = _config(task_id)

    graph.invoke(
        {
            "task_id": task_id,
            "user_query": "trigger workflow",
            "identity": resolve_identity_from_api_key(ADMIN_API_KEY),
            "audit_trail": [],
        },
        config=config,
    )

    snapshot = graph.get_state(config)
    result = snapshot.values

    assert result["selected_tool_name"] == "trigger_workflow_dry_run"
    assert result["policy_decision"].decision == PolicyDecisionType.REQUIRE_APPROVAL
    assert result["approval_request"] is not None
    assert result["status"] == TaskStatus.PAUSED_FOR_APPROVAL
    assert result.get("tool_result") is None


def test_admin_does_not_bypass_approval_in_graph() -> None:
    graph = build_harness_graph()
    task_id = "task-approval-admin-2"
    config = _config(task_id)

    graph.invoke(
        {
            "task_id": task_id,
            "user_query": "trigger workflow",
            "identity": resolve_identity_from_api_key(ADMIN_API_KEY),
            "audit_trail": [],
        },
        config=config,
    )

    snapshot = graph.get_state(config)
    result = snapshot.values

    event_types = [event.event_type for event in result["audit_trail"]]

    assert result["policy_decision"].decision == PolicyDecisionType.REQUIRE_APPROVAL
    assert result["status"] == TaskStatus.PAUSED_FOR_APPROVAL
    assert result.get("tool_result") is None
    assert AuditEventType.APPROVAL_REQUESTED in event_types
    assert AuditEventType.TOOL_EXECUTED not in event_types


def test_high_risk_tool_never_executes_before_approval() -> None:
    graph = build_harness_graph()

    for api_key in [OPERATOR_API_KEY, ADMIN_API_KEY]:
        task_id = f"task-high-risk-{api_key}"
        config = _config(task_id)

        graph.invoke(
            {
                "task_id": task_id,
                "user_query": "trigger workflow",
                "identity": resolve_identity_from_api_key(api_key),
                "audit_trail": [],
            },
            config=config,
        )

        snapshot = graph.get_state(config)
        result = snapshot.values

        event_types = [event.event_type for event in result["audit_trail"]]

        assert result["status"] == TaskStatus.PAUSED_FOR_APPROVAL
        assert result.get("tool_result") is None
        assert AuditEventType.TOOL_EXECUTED not in event_types