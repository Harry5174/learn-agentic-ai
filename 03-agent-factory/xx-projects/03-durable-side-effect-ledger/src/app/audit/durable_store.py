import json
import math
import sqlite3
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from pydantic import ValidationError

from app.audit.durable_schemas import (
    DuplicateDurableAuditEventError,
    DurableAuditEvent,
    DurableAuditEventNotFoundError,
    DurableAuditEventType,
    InvalidDurableAuditEventTypeError,
    InvalidDurableAuditMetadataError,
    UnsafeDurableAuditMetadataError,
)
from app.persistence.sqlite import SQLiteConnectionManager


UNSAFE_METADATA_KEYS = {
    "authorization",
    "github_token",
    "github-token",
    "githubtoken",
    "api_base_url",
    "client_config",
    "transport",
}

UNSAFE_METADATA_VALUE_MARKERS = (
    "authorization",
    "github_token",
    "github-token",
    "githubtoken",
    "github_pat_",
    "ghp_",
    "gho_",
    "ghu_",
    "ghs_",
    "ghr_",
    "bearer ",
    "api_base_url",
    "client_config",
    "transport",
)


class DurableAuditStore:
    """SQLite-backed durable audit store for local/demo side-effect evidence."""

    def __init__(self, db_manager: SQLiteConnectionManager):
        self.db_manager = db_manager

    def initialize(self) -> None:
        self.db_manager.initialize_schema()

    def append(self, event: DurableAuditEvent) -> None:
        metadata_json = _metadata_to_safe_json(event.metadata)
        event_type = _event_type_value(event.event_type)

        sql = """
            INSERT INTO durable_audit_events (
                event_id, run_id, side_effect_id, event_type, actor_id,
                message, metadata_json, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        try:
            with self.db_manager.get_connection() as conn:
                conn.execute(
                    sql,
                    (
                        event.event_id,
                        event.run_id,
                        event.side_effect_id,
                        event_type,
                        event.actor_id,
                        event.message,
                        metadata_json,
                        event.created_at,
                    ),
                )
                conn.commit()
        except sqlite3.IntegrityError as exc:
            if "UNIQUE constraint failed" in str(exc):
                raise DuplicateDurableAuditEventError(
                    f"Durable audit event {event.event_id} already exists"
                )
            raise DuplicateDurableAuditEventError(str(exc))  # pragma: no cover

    def append_event(
        self,
        *,
        run_id: str,
        event_type: DurableAuditEventType | str,
        message: str,
        side_effect_id: str | None = None,
        actor_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> DurableAuditEvent:
        try:
            event = DurableAuditEvent(
                event_id=str(uuid4()),
                run_id=run_id,
                side_effect_id=side_effect_id,
                event_type=event_type,
                actor_id=actor_id,
                message=message,
                metadata=dict(metadata or {}),
                created_at=datetime.now(timezone.utc).isoformat(),
            )
        except ValidationError as exc:
            raise InvalidDurableAuditEventTypeError(str(exc))

        self.append(event)
        return event

    def get(self, event_id: str) -> DurableAuditEvent:
        sql = "SELECT * FROM durable_audit_events WHERE event_id = ?"
        with self.db_manager.get_connection() as conn:
            row = conn.execute(sql, (event_id,)).fetchone()

        if not row:
            raise DurableAuditEventNotFoundError(
                f"Durable audit event {event_id} not found"
            )

        return _event_from_row(row)

    def list_by_run_id(self, run_id: str) -> list[DurableAuditEvent]:
        sql = """
            SELECT * FROM durable_audit_events
            WHERE run_id = ?
            ORDER BY created_at, event_id
        """
        with self.db_manager.get_connection() as conn:
            rows = conn.execute(sql, (run_id,)).fetchall()
        return [_event_from_row(row) for row in rows]

    def list_by_side_effect_id(self, side_effect_id: str) -> list[DurableAuditEvent]:
        sql = """
            SELECT * FROM durable_audit_events
            WHERE side_effect_id = ?
            ORDER BY created_at, event_id
        """
        with self.db_manager.get_connection() as conn:
            rows = conn.execute(sql, (side_effect_id,)).fetchall()
        return [_event_from_row(row) for row in rows]

    def close(self) -> None:
        pass


def _event_type_value(event_type: DurableAuditEventType | str) -> str:
    try:
        return DurableAuditEventType(event_type).value
    except ValueError:
        raise InvalidDurableAuditEventTypeError(
            f"Unsupported durable audit event type: {event_type}"
        )


def _metadata_to_safe_json(metadata: dict[str, Any]) -> str:
    _validate_safe_json_value(metadata)
    try:
        return json.dumps(
            metadata,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
    except (TypeError, ValueError) as exc:
        raise InvalidDurableAuditMetadataError(str(exc))


def _event_from_row(row: sqlite3.Row) -> DurableAuditEvent:
    metadata_json = row["metadata_json"]
    if metadata_json is None:
        metadata: dict[str, Any] = {}
    else:
        try:
            parsed = json.loads(metadata_json)
        except json.JSONDecodeError as exc:
            raise InvalidDurableAuditMetadataError(str(exc))
        if not isinstance(parsed, dict):
            raise InvalidDurableAuditMetadataError(
                "Durable audit metadata_json must decode to an object"
            )
        metadata = parsed

    try:
        return DurableAuditEvent(
            event_id=row["event_id"],
            run_id=row["run_id"],
            side_effect_id=row["side_effect_id"],
            event_type=row["event_type"],
            actor_id=row["actor_id"],
            message=row["message"],
            metadata=metadata,
            created_at=row["created_at"],
        )
    except ValidationError as exc:
        raise InvalidDurableAuditEventTypeError(str(exc))


def _validate_safe_json_value(value: Any) -> None:
    if isinstance(value, dict):
        for key, nested in value.items():
            if not isinstance(key, str):
                raise InvalidDurableAuditMetadataError(
                    "Durable audit metadata keys must be strings"
                )
            _reject_unsafe_text(key)
            _validate_safe_json_value(nested)
        return

    if isinstance(value, list):
        for nested in value:
            _validate_safe_json_value(nested)
        return

    if isinstance(value, str):
        _reject_unsafe_text(value)
        return

    if isinstance(value, bool) or value is None or isinstance(value, int):
        return

    if isinstance(value, float):
        if not math.isfinite(value):
            raise InvalidDurableAuditMetadataError(
                "Durable audit metadata floats must be finite"
            )
        return

    raise InvalidDurableAuditMetadataError(
        f"Unsupported durable audit metadata value type: {type(value).__name__}"
    )


def _reject_unsafe_text(value: str) -> None:
    normalized = value.lower()
    if normalized in UNSAFE_METADATA_KEYS:
        raise UnsafeDurableAuditMetadataError(
            f"Unsafe durable audit metadata key or value: {value}"
        )

    for marker in UNSAFE_METADATA_VALUE_MARKERS:
        if marker in normalized:
            raise UnsafeDurableAuditMetadataError(
                f"Unsafe durable audit metadata key or value: {value}"
            )
