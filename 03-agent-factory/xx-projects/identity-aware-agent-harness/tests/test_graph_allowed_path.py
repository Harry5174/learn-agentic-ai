from app.audit.schemas import AuditEventType
from app.graph.builder import build_harness_graph
from app.identity.config import VIEWER_API_KEY
from app.identity.resolver import resolve_identity_from_api_key
from app.policy.schemas import PolicyDecisionType
from app.state.schemas import TaskStatus


def test_viewer_inspect_task_completes_allowed_path() -> None:
    graph = build_harness_graph()

    result = graph.invoke(
        {
            "task_id": "task-allowed-1",
            "user_query": "inspect sandbox issues",
            "identity": resolve_identity_from_api_key(VIEWER_API_KEY),
            "audit_trail": [],
        }
    )

    assert result["selected_tool_name"] == "inspect_sandbox_issues"
    assert result["policy_decision"].decision == PolicyDecisionType.ALLOW
    assert result["tool_result"] is not None
    assert result["tool_result"].tool_name == "inspect_sandbox_issues"
    assert result["tool_result"].dry_run is True
    assert result["status"] == TaskStatus.COMPLETED
    assert result["final_report"] == "Task completed successfully using dry-run execution."


def test_viewer_inspect_task_audit_contains_expected_events() -> None:
    graph = build_harness_graph()

    result = graph.invoke(
        {
            "task_id": "task-allowed-2",
            "user_query": "inspect sandbox issues",
            "identity": resolve_identity_from_api_key(VIEWER_API_KEY),
            "audit_trail": [],
        }
    )

    event_types = [event.event_type for event in result["audit_trail"]]

    assert AuditEventType.TASK_CREATED in event_types
    assert AuditEventType.TOOL_SELECTED in event_types
    assert AuditEventType.PERMISSION_CHECKED in event_types
    assert AuditEventType.TOOL_EXECUTED in event_types
    assert AuditEventType.TASK_COMPLETED in event_types


def test_viewer_inspect_task_executes_only_after_allow_decision() -> None:
    graph = build_harness_graph()

    result = graph.invoke(
        {
            "task_id": "task-allowed-3",
            "user_query": "inspect sandbox issues",
            "identity": resolve_identity_from_api_key(VIEWER_API_KEY),
            "audit_trail": [],
        }
    )

    assert result["policy_decision"].decision == PolicyDecisionType.ALLOW
    assert result["tool_result"] is not None
    assert result["tool_result"].success is True