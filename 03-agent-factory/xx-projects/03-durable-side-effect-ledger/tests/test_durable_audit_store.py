import json
import sqlite3
from pathlib import Path

import pytest

from app.audit.durable_schemas import (
    DuplicateDurableAuditEventError,
    DurableAuditEvent,
    DurableAuditEventNotFoundError,
    DurableAuditEventType,
    InvalidDurableAuditEventTypeError,
    InvalidDurableAuditMetadataError,
    UnsafeDurableAuditMetadataError,
)
from app.audit.durable_store import DurableAuditStore
from app.persistence.sqlite import SQLiteConnectionManager


def store_for(db_path: Path) -> DurableAuditStore:
    manager = SQLiteConnectionManager(db_path)
    store = DurableAuditStore(manager)
    store.initialize()
    return store


def test_schema_initializes_idempotently(tmp_path: Path) -> None:
    db_path = tmp_path / "durable.sqlite"
    store = store_for(db_path)
    store.initialize()

    event = store.append_event(
        run_id="run-audit-1",
        side_effect_id="side-effect-1",
        event_type=DurableAuditEventType.EXECUTION_REQUESTED,
        message="Execution requested.",
    )

    assert store.get(event.event_id).event_type == (
        DurableAuditEventType.EXECUTION_REQUESTED
    )


def test_append_get_and_list_events(tmp_path: Path) -> None:
    db_path = tmp_path / "durable.sqlite"
    store = store_for(db_path)
    first = store.append_event(
        run_id="run-audit-1",
        side_effect_id="side-effect-1",
        event_type=DurableAuditEventType.EXECUTION_REQUESTED,
        message="Execution requested.",
        metadata={"repository": "Harry5174/learn-agentic-ai", "issue_number": 1},
    )
    second = store.append_event(
        run_id="run-audit-1",
        side_effect_id="side-effect-1",
        event_type=DurableAuditEventType.EXECUTION_BLOCKED,
        message="Execution blocked.",
        metadata={"replay_outcome": "approval_blocked"},
    )

    assert store.get(first.event_id).metadata["issue_number"] == 1
    assert [event.event_id for event in store.list_by_run_id("run-audit-1")] == [
        first.event_id,
        second.event_id,
    ]
    assert [
        event.event_type for event in store.list_by_side_effect_id("side-effect-1")
    ] == [
        DurableAuditEventType.EXECUTION_REQUESTED,
        DurableAuditEventType.EXECUTION_BLOCKED,
    ]


def test_events_survive_store_reinstantiation(tmp_path: Path) -> None:
    db_path = tmp_path / "durable.sqlite"
    store_1 = store_for(db_path)
    event = store_1.append_event(
        run_id="run-audit-1",
        side_effect_id="side-effect-1",
        event_type=DurableAuditEventType.EXECUTION_SUCCEEDED,
        message="Execution succeeded.",
        metadata={"comment_id": "fake-comment-1"},
    )

    store_2 = store_for(db_path)

    assert store_2.get(event.event_id).metadata == {
        "comment_id": "fake-comment-1"
    }


def test_duplicate_event_id_fails_safely(tmp_path: Path) -> None:
    db_path = tmp_path / "durable.sqlite"
    store = store_for(db_path)
    event = DurableAuditEvent(
        event_id="event-1",
        run_id="run-audit-1",
        side_effect_id="side-effect-1",
        event_type=DurableAuditEventType.EXECUTION_REQUESTED,
        message="Execution requested.",
    )
    store.append(event)

    with pytest.raises(DuplicateDurableAuditEventError):
        store.append(event)


def test_get_missing_event_fails_safely(tmp_path: Path) -> None:
    store = store_for(tmp_path / "durable.sqlite")

    with pytest.raises(DurableAuditEventNotFoundError):
        store.get("missing-event")


def test_invalid_event_type_fails_safely(tmp_path: Path) -> None:
    store = store_for(tmp_path / "durable.sqlite")

    with pytest.raises(InvalidDurableAuditEventTypeError):
        store.append_event(
            run_id="run-audit-1",
            event_type="not_a_real_event_type",
            message="Invalid event.",
        )


def test_metadata_is_serialized_and_deserialized_as_json(tmp_path: Path) -> None:
    db_path = tmp_path / "durable.sqlite"
    store = store_for(db_path)
    event = store.append_event(
        run_id="run-audit-1",
        side_effect_id="side-effect-1",
        event_type=DurableAuditEventType.EXECUTION_SUCCEEDED,
        message="Execution succeeded.",
        metadata={"nested": {"ok": True}, "items": [1, "two", None]},
    )

    with sqlite3.connect(db_path) as conn:
        raw = conn.execute(
            "SELECT metadata_json FROM durable_audit_events WHERE event_id = ?",
            (event.event_id,),
        ).fetchone()[0]

    assert json.loads(raw) == {"items": [1, "two", None], "nested": {"ok": True}}
    assert store.get(event.event_id).metadata["nested"] == {"ok": True}


@pytest.mark.parametrize(
    "metadata",
    [
        {"github_token": "ghp_secret"},
        {"GITHUB_TOKEN": "secret"},
        {"headers": {"authorization": "Bearer secret"}},
        {"api_base_url": "https://api.github.com"},
        {"client_config": {"timeout": 1}},
        {"transport": "network"},
        {"payload": {"nested": "raw malicious github_token value"}},
    ],
)
def test_unsafe_metadata_is_rejected_and_not_persisted_raw(
    tmp_path: Path,
    metadata: dict,
) -> None:
    db_path = tmp_path / "durable.sqlite"
    store = store_for(db_path)

    with pytest.raises(UnsafeDurableAuditMetadataError):
        store.append_event(
            run_id="run-audit-1",
            side_effect_id="side-effect-1",
            event_type=DurableAuditEventType.EXECUTION_REQUESTED,
            message="Execution requested.",
            metadata=metadata,
        )

    with sqlite3.connect(db_path) as conn:
        rows = conn.execute(
            "SELECT metadata_json FROM durable_audit_events"
        ).fetchall()

    raw_values = "\n".join(row[0] or "" for row in rows).lower()
    for forbidden in (
        "github_token",
        "authorization",
        "api_base_url",
        "client_config",
        "transport",
    ):
        assert forbidden.lower() not in raw_values


def test_non_json_metadata_is_rejected(tmp_path: Path) -> None:
    store = store_for(tmp_path / "durable.sqlite")

    with pytest.raises(InvalidDurableAuditMetadataError):
        store.append_event(
            run_id="run-audit-1",
            side_effect_id="side-effect-1",
            event_type=DurableAuditEventType.EXECUTION_REQUESTED,
            message="Execution requested.",
            metadata={"bad": object()},
        )
