import json
import sqlite3
from datetime import datetime, timezone

from app.persistence.sqlite import SQLiteConnectionManager
from app.side_effects.durable_schemas import (
    DuplicateSideEffectRecordError,
    DurableSideEffectRecord,
    DurableSideEffectStatus,
    InvalidSideEffectTransitionError,
    SideEffectRecordNotFoundError,
    TerminalSideEffectStateError,
)


class DurableSideEffectLedger:
    """SQLite-backed ledger for storing and managing side-effect records."""

    TERMINAL_STATES = {
        DurableSideEffectStatus.SUCCEEDED,
        DurableSideEffectStatus.FAILED,
        DurableSideEffectStatus.SKIPPED_DUPLICATE,
        DurableSideEffectStatus.REJECTED,
        DurableSideEffectStatus.BLOCKED,
    }

    VALID_TRANSITIONS = {
        DurableSideEffectStatus.PLANNED: {
            DurableSideEffectStatus.APPROVED,
            DurableSideEffectStatus.REJECTED,
            DurableSideEffectStatus.BLOCKED,
        },
        DurableSideEffectStatus.APPROVED: {
            DurableSideEffectStatus.EXECUTING,
        },
        DurableSideEffectStatus.EXECUTING: {
            DurableSideEffectStatus.SUCCEEDED,
            DurableSideEffectStatus.FAILED,
        },
        DurableSideEffectStatus.SUCCEEDED: {
            DurableSideEffectStatus.SKIPPED_DUPLICATE,
        },
    }

    def __init__(self, db_manager: SQLiteConnectionManager):
        self.db_manager = db_manager

    def initialize(self) -> None:
        """Initialize the ledger schema."""
        self.db_manager.initialize_schema()

    def create_planned(self, record: DurableSideEffectRecord) -> None:
        """Create a new side-effect record in PLANNED state."""
        if record.status != DurableSideEffectStatus.PLANNED:
            raise ValueError("Initial record must be in PLANNED state")

        sql = """
            INSERT INTO side_effect_records (
                side_effect_id, run_id, skill_id, step_id, tool_name,
                validated_arguments_hash, status, repository, issue_number,
                comment_body_hash, comment_body_preview, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        try:
            with self.db_manager.get_connection() as conn:
                conn.execute(sql, (
                    record.side_effect_id, record.run_id, record.skill_id, record.step_id, record.tool_name,
                    record.validated_arguments_hash, record.status, record.repository, record.issue_number,
                    record.comment_body_hash, record.comment_body_preview, record.created_at, record.updated_at
                ))
                conn.commit()
        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed" in str(e):
                raise DuplicateSideEffectRecordError(f"Record {record.side_effect_id} already exists")
            raise  # pragma: no cover

    def get(self, side_effect_id: str) -> DurableSideEffectRecord:
        """Retrieve a side-effect record by ID."""
        sql = "SELECT * FROM side_effect_records WHERE side_effect_id = ?"
        with self.db_manager.get_connection() as conn:
            row = conn.execute(sql, (side_effect_id,)).fetchone()
            
        if not row:
            raise SideEffectRecordNotFoundError(f"Record {side_effect_id} not found")
            
        return DurableSideEffectRecord(**dict(row))

    def exists(self, side_effect_id: str) -> bool:
        """Check if a side-effect record exists."""
        sql = "SELECT 1 FROM side_effect_records WHERE side_effect_id = ?"
        with self.db_manager.get_connection() as conn:
            row = conn.execute(sql, (side_effect_id,)).fetchone()
            return bool(row)

    def list_by_run_id(self, run_id: str) -> list[DurableSideEffectRecord]:
        """List all side-effect records for a given run ID."""
        sql = "SELECT * FROM side_effect_records WHERE run_id = ?"
        with self.db_manager.get_connection() as conn:
            rows = conn.execute(sql, (run_id,)).fetchall()
            return [DurableSideEffectRecord(**dict(row)) for row in rows]

    def _transition_status(
        self,
        side_effect_id: str,
        new_status: DurableSideEffectStatus,
        updates: dict[str, str | None],
    ) -> None:
        """Perform a status transition with checks."""
        record = self.get(side_effect_id)

        if record.status in self.TERMINAL_STATES and new_status not in self.VALID_TRANSITIONS.get(record.status, set()):
             raise TerminalSideEffectStateError(f"Cannot mutate record in terminal state {record.status}")
             
        if new_status not in self.VALID_TRANSITIONS.get(record.status, set()):
             raise InvalidSideEffectTransitionError(f"Cannot transition from {record.status} to {new_status}")

        now = datetime.now(timezone.utc).isoformat()
        
        set_clauses = ["status = ?", "updated_at = ?"]
        values = [new_status, now]
        
        for k, v in updates.items():
            set_clauses.append(f"{k} = ?")
            values.append(v)
            
        set_clauses_str = ", ".join(set_clauses)
        values.append(side_effect_id)
        
        sql = f"UPDATE side_effect_records SET {set_clauses_str} WHERE side_effect_id = ?"
        
        with self.db_manager.get_connection() as conn:
            conn.execute(sql, tuple(values))
            conn.commit()

    def mark_approved(self, side_effect_id: str) -> None:
        """Mark a record as approved."""
        self._transition_status(
            side_effect_id,
            DurableSideEffectStatus.APPROVED,
            {"approved_at": datetime.now(timezone.utc).isoformat()}
        )

    def mark_rejected(self, side_effect_id: str, reason: str | None = None) -> None:
        """Mark a record as rejected."""
        failure_json = json.dumps({"reason": reason}) if reason else None
        self._transition_status(
            side_effect_id,
            DurableSideEffectStatus.REJECTED,
            {"failure_json": failure_json}
        )

    def mark_blocked(self, side_effect_id: str, reason: str | None = None) -> None:
        """Mark a record as blocked."""
        failure_json = json.dumps({"reason": reason}) if reason else None
        self._transition_status(
            side_effect_id,
            DurableSideEffectStatus.BLOCKED,
            {"failure_json": failure_json}
        )

    def mark_executing(self, side_effect_id: str) -> None:
        """Mark a record as executing."""
        self._transition_status(
            side_effect_id,
            DurableSideEffectStatus.EXECUTING,
            {"started_at": datetime.now(timezone.utc).isoformat()}
        )

    def mark_succeeded(self, side_effect_id: str, external_result: dict | None = None) -> None:
        """Mark a record as succeeded."""
        result_json = json.dumps(external_result) if external_result else None
        self._transition_status(
            side_effect_id,
            DurableSideEffectStatus.SUCCEEDED,
            {
                "executed_at": datetime.now(timezone.utc).isoformat(),
                "external_result_json": result_json
            }
        )

    def mark_failed(self, side_effect_id: str, failure: dict | None = None) -> None:
        """Mark a record as failed."""
        failure_json = json.dumps(failure) if failure else None
        self._transition_status(
            side_effect_id,
            DurableSideEffectStatus.FAILED,
            {
                "failed_at": datetime.now(timezone.utc).isoformat(),
                "failure_json": failure_json
            }
        )

    def mark_skipped_duplicate(self, side_effect_id: str, external_result: dict | None = None) -> None:
        """Mark a record as skipped due to duplication (replay)."""
        result_json = json.dumps(external_result) if external_result else None
        self._transition_status(
            side_effect_id,
            DurableSideEffectStatus.SKIPPED_DUPLICATE,
            {
                "skipped_at": datetime.now(timezone.utc).isoformat(),
                "external_result_json": result_json
            }
        )

    def mark_remote_reconciled(
        self,
        side_effect_id: str,
        external_result: dict | None = None,
    ) -> None:
        """Recover an approved/executing record after finding its remote marker."""

        record = self.get(side_effect_id)
        if record.status not in {
            DurableSideEffectStatus.APPROVED,
            DurableSideEffectStatus.EXECUTING,
        }:
            if record.status in self.TERMINAL_STATES:
                raise TerminalSideEffectStateError(
                    f"Cannot remote-reconcile terminal state {record.status}"
                )
            raise InvalidSideEffectTransitionError(
                f"Cannot remote-reconcile from {record.status}"
            )

        result_json = json.dumps(external_result) if external_result else None
        now = datetime.now(timezone.utc).isoformat()
        sql = """
            UPDATE side_effect_records
            SET status = ?, updated_at = ?, executed_at = ?,
                external_result_json = ?
            WHERE side_effect_id = ?
        """
        with self.db_manager.get_connection() as conn:
            conn.execute(
                sql,
                (
                    DurableSideEffectStatus.SUCCEEDED,
                    now,
                    now,
                    result_json,
                    side_effect_id,
                ),
            )
            conn.commit()
        
    def close(self) -> None:
        """Close the ledger resources if necessary."""
        # SQLite connection manager opens connections on demand
        # Global or shared connections could be closed here if stored
        pass
