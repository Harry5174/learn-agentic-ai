from pathlib import Path

from app.audit.schemas import AuditEventType
from app.graph.builder import build_harness_graph
from app.identity.config import OPERATOR_API_KEY, VIEWER_API_KEY
from app.identity.resolver import resolve_identity_from_api_key


def test_allowed_graph_path_audit_event_order() -> None:
    graph = build_harness_graph()

    result = graph.invoke(
        {
            "task_id": "task-audit-allowed-1",
            "user_query": "inspect sandbox issues",
            "identity": resolve_identity_from_api_key(VIEWER_API_KEY),
            "audit_trail": [],
        }
    )

    event_types = [event.event_type for event in result["audit_trail"]]

    assert event_types == [
        AuditEventType.TASK_CREATED,
        AuditEventType.TOOL_SELECTED,
        AuditEventType.PERMISSION_CHECKED,
        AuditEventType.TOOL_EXECUTED,
        AuditEventType.TASK_COMPLETED,
    ]


def test_denied_graph_path_audit_event_order() -> None:
    graph = build_harness_graph()

    result = graph.invoke(
        {
            "task_id": "task-audit-denied-1",
            "user_query": "draft issue comment",
            "identity": resolve_identity_from_api_key(VIEWER_API_KEY),
            "audit_trail": [],
        }
    )

    event_types = [event.event_type for event in result["audit_trail"]]

    assert event_types == [
        AuditEventType.TASK_CREATED,
        AuditEventType.TOOL_SELECTED,
        AuditEventType.PERMISSION_CHECKED,
    ]


def test_approval_pause_graph_path_audit_event_order() -> None:
    graph = build_harness_graph()

    result = graph.invoke(
        {
            "task_id": "task-audit-approval-1",
            "user_query": "trigger workflow",
            "identity": resolve_identity_from_api_key(OPERATOR_API_KEY),
            "audit_trail": [],
        }
    )

    event_types = [event.event_type for event in result["audit_trail"]]

    assert event_types == [
        AuditEventType.TASK_CREATED,
        AuditEventType.TOOL_SELECTED,
        AuditEventType.PERMISSION_CHECKED,
        AuditEventType.APPROVAL_REQUESTED,
    ]


def test_permission_checked_audit_contains_policy_metadata() -> None:
    graph = build_harness_graph()

    result = graph.invoke(
        {
            "task_id": "task-audit-policy-1",
            "user_query": "draft issue comment",
            "identity": resolve_identity_from_api_key(VIEWER_API_KEY),
            "audit_trail": [],
        }
    )

    permission_events = [
        event
        for event in result["audit_trail"]
        if event.event_type == AuditEventType.PERMISSION_CHECKED
    ]

    assert len(permission_events) == 1

    metadata = permission_events[0].metadata

    assert metadata["decision"] == "deny"
    assert metadata["reason"]
    assert metadata["required_scopes"] == ["tools:draft"]
    assert metadata["missing_scopes"] == ["tools:draft"]


def test_graph_source_does_not_import_fastapi_or_openai() -> None:
    graph_source_files = [
        Path("src/app/graph/state.py"),
        Path("src/app/graph/nodes.py"),
        Path("src/app/graph/routing.py"),
        Path("src/app/graph/builder.py"),
    ]

    combined_source = "\n".join(path.read_text() for path in graph_source_files)

    forbidden_imports = [
        "import fastapi",
        "from fastapi",
        "import openai",
        "from openai",
        "import langchain_openai",
        "from langchain_openai",
        "ChatOpenAI",
    ]

    assert not any(term in combined_source for term in forbidden_imports)


def test_graph_source_does_not_perform_external_http_calls() -> None:
    graph_source_files = [
        Path("src/app/graph/state.py"),
        Path("src/app/graph/nodes.py"),
        Path("src/app/graph/routing.py"),
        Path("src/app/graph/builder.py"),
    ]

    combined_source = "\n".join(path.read_text() for path in graph_source_files)

    forbidden_terms = [
        "requests.",
        "httpx.",
        "urllib.request",
        "aiohttp",
    ]

    assert not any(term in combined_source for term in forbidden_terms)