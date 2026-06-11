from app.audit.schemas import AuditEventType
from app.graph.builder import build_harness_graph
from app.identity.config import VIEWER_API_KEY
from app.identity.resolver import resolve_identity_from_api_key
from app.policy.schemas import PolicyDecisionType
from app.state.schemas import TaskStatus


def _config(task_id: str) -> dict:
    """Build a LangGraph config with a unique thread_id."""
    return {"configurable": {"thread_id": task_id}}


def test_viewer_draft_task_is_denied() -> None:
    graph = build_harness_graph()
    task_id = "task-denied-1"

    result = graph.invoke(
        {
            "task_id": task_id,
            "user_query": "draft issue comment",
            "identity": resolve_identity_from_api_key(VIEWER_API_KEY),
            "audit_trail": [],
        },
        config=_config(task_id),
    )

    assert result["selected_tool_name"] == "draft_issue_comment"
    assert result["policy_decision"].decision == PolicyDecisionType.DENY
    assert result.get("tool_result") is None
    assert result["status"] == TaskStatus.DENIED
    assert result["final_report"].startswith("Task denied:")


def test_viewer_draft_task_audit_excludes_tool_executed() -> None:
    graph = build_harness_graph()
    task_id = "task-denied-2"

    result = graph.invoke(
        {
            "task_id": task_id,
            "user_query": "draft issue comment",
            "identity": resolve_identity_from_api_key(VIEWER_API_KEY),
            "audit_trail": [],
        },
        config=_config(task_id),
    )

    event_types = [event.event_type for event in result["audit_trail"]]

    assert AuditEventType.TASK_CREATED in event_types
    assert AuditEventType.TOOL_SELECTED in event_types
    assert AuditEventType.PERMISSION_CHECKED in event_types
    assert AuditEventType.TOOL_EXECUTED not in event_types
    assert AuditEventType.TASK_COMPLETED not in event_types


def test_unknown_query_fails_without_tool_execution() -> None:
    graph = build_harness_graph()
    task_id = "task-unknown-1"

    result = graph.invoke(
        {
            "task_id": task_id,
            "user_query": "do something random",
            "identity": resolve_identity_from_api_key(VIEWER_API_KEY),
            "audit_trail": [],
        },
        config=_config(task_id),
    )

    assert result["status"] == TaskStatus.FAILED
    assert result["selected_tool_name"] is None
    assert result.get("tool_result") is None
    assert result["error_message"] == "Unable to select a supported tool."
    assert result["final_report"] == "Task failed: Unable to select a supported tool."


def test_unknown_query_audit_does_not_include_tool_or_permission_events() -> None:
    graph = build_harness_graph()
    task_id = "task-unknown-2"

    result = graph.invoke(
        {
            "task_id": task_id,
            "user_query": "do something random",
            "identity": resolve_identity_from_api_key(VIEWER_API_KEY),
            "audit_trail": [],
        },
        config=_config(task_id),
    )

    event_types = [event.event_type for event in result["audit_trail"]]

    assert AuditEventType.TASK_CREATED in event_types
    assert AuditEventType.TOOL_SELECTED not in event_types
    assert AuditEventType.PERMISSION_CHECKED not in event_types
    assert AuditEventType.TOOL_EXECUTED not in event_types