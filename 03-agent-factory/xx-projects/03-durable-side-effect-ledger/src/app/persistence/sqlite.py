import sqlite3
from pathlib import Path


class SQLiteConnectionManager:
    """Manages SQLite connections and idempotent schema initialization."""

    def __init__(self, db_path: Path | str):
        self.db_path = Path(db_path)

    def get_connection(self) -> sqlite3.Connection:
        """Returns a new connection with row_factory set."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def initialize_schema(self) -> None:
        """Idempotently initializes required A4 schemas."""
        
        # We define the side_effect_records table here.
        create_side_effect_records_sql = """
        CREATE TABLE IF NOT EXISTS side_effect_records (
            side_effect_id TEXT PRIMARY KEY,
            run_id TEXT NOT NULL,
            skill_id TEXT NOT NULL,
            step_id TEXT NOT NULL,
            tool_name TEXT NOT NULL,
            validated_arguments_hash TEXT NOT NULL,
            status TEXT NOT NULL,
            repository TEXT,
            issue_number INTEGER,
            comment_body_hash TEXT,
            comment_body_preview TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            approved_at TEXT,
            started_at TEXT,
            executed_at TEXT,
            skipped_at TEXT,
            failed_at TEXT,
            external_result_json TEXT,
            failure_json TEXT
        );
        """

        # A4.2: approval_bindings table for durable approval binding.
        # side_effect_id is UNIQUE to enforce one binding per side effect in V1.
        # No SQL-level foreign key — domain checks enforce the relationship.
        create_approval_bindings_sql = """
        CREATE TABLE IF NOT EXISTS approval_bindings (
            approval_id TEXT PRIMARY KEY,
            run_id TEXT NOT NULL,
            skill_id TEXT NOT NULL,
            step_id TEXT NOT NULL,
            tool_name TEXT NOT NULL,
            side_effect_id TEXT NOT NULL UNIQUE,
            validated_arguments_hash TEXT NOT NULL,
            approval_status TEXT NOT NULL,
            requested_by TEXT,
            decided_by TEXT,
            reason TEXT,
            created_at TEXT NOT NULL,
            decided_at TEXT,
            expires_at TEXT
        );
        """
        
        with self.get_connection() as conn:
            conn.execute(create_side_effect_records_sql)
            conn.execute(create_approval_bindings_sql)
            conn.commit()
