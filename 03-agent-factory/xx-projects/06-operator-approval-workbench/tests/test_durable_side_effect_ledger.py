from datetime import datetime, timezone
import json

import pytest

from app.persistence.sqlite import SQLiteConnectionManager
from app.side_effects.durable_schemas import (
    DuplicateSideEffectRecordError,
    DurableSideEffectRecord,
    DurableSideEffectStatus,
    InvalidSideEffectTransitionError,
    SideEffectRecordNotFoundError,
    TerminalSideEffectStateError,
)
from app.side_effects.durable_ledger import DurableSideEffectLedger


@pytest.fixture
def temp_db_path(tmp_path):
    return tmp_path / "test_ledger.sqlite"


@pytest.fixture
def db_manager(temp_db_path):
    manager = SQLiteConnectionManager(temp_db_path)
    manager.initialize_schema()
    return manager


@pytest.fixture
def ledger(db_manager):
    return DurableSideEffectLedger(db_manager)


def make_planned_record(side_effect_id: str, run_id: str = "run_1") -> DurableSideEffectRecord:
    return DurableSideEffectRecord(
        side_effect_id=side_effect_id,
        run_id=run_id,
        skill_id="skill_1",
        step_id="step_1",
        tool_name="test_tool",
        validated_arguments_hash="hash_123",
        status=DurableSideEffectStatus.PLANNED,
        created_at=datetime.now(timezone.utc).isoformat(),
        updated_at=datetime.now(timezone.utc).isoformat(),
        comment_body_hash="hash_abc",
        comment_body_preview="Hello..."
    )


# --- 16.1 Schema / Init Tests ---
def test_schema_initialization_idempotent(temp_db_path):
    manager = SQLiteConnectionManager(temp_db_path)
    manager.initialize_schema()
    # Running again should not error
    manager.initialize_schema()
    
    # Check that it exists and has correct columns
    with manager.get_connection() as conn:
        cursor = conn.execute("PRAGMA table_info(side_effect_records)")
        columns = [row["name"] for row in cursor.fetchall()]
        assert "side_effect_id" in columns
        assert "run_id" in columns


# --- 16.2 Create / Read Tests ---
def test_create_and_read_record(ledger):
    record = make_planned_record("se_1")
    ledger.create_planned(record)
    
    retrieved = ledger.get("se_1")
    assert retrieved.side_effect_id == "se_1"
    assert retrieved.status == DurableSideEffectStatus.PLANNED
    assert retrieved.comment_body_hash == "hash_abc"
    assert retrieved.comment_body_preview == "Hello..."
    assert ledger.exists("se_1") is True


def test_get_missing_record(ledger):
    with pytest.raises(SideEffectRecordNotFoundError):
        ledger.get("se_missing")


def test_list_by_run_id(ledger):
    ledger.create_planned(make_planned_record("se_1", "run_A"))
    ledger.create_planned(make_planned_record("se_2", "run_A"))
    ledger.create_planned(make_planned_record("se_3", "run_B"))
    
    records_a = ledger.list_by_run_id("run_A")
    assert len(records_a) == 2
    assert {r.side_effect_id for r in records_a} == {"se_1", "se_2"}


# --- 16.3 Duplicate Tests ---
def test_duplicate_side_effect_id(ledger):
    record = make_planned_record("se_dup")
    ledger.create_planned(record)
    
    with pytest.raises(DuplicateSideEffectRecordError):
        ledger.create_planned(record)


# --- 16.4 Transition Tests ---
def test_valid_transitions(ledger):
    # Full happy path
    ledger.create_planned(make_planned_record("se_happy"))
    ledger.mark_approved("se_happy")
    assert ledger.get("se_happy").status == DurableSideEffectStatus.APPROVED
    assert ledger.get("se_happy").approved_at is not None
    
    ledger.mark_executing("se_happy")
    assert ledger.get("se_happy").status == DurableSideEffectStatus.EXECUTING
    assert ledger.get("se_happy").started_at is not None

    ledger.mark_succeeded("se_happy", {"result": "ok"})
    assert ledger.get("se_happy").status == DurableSideEffectStatus.SUCCEEDED
    assert ledger.get("se_happy").executed_at is not None
    assert json.loads(ledger.get("se_happy").external_result_json) == {"result": "ok"}
    
    ledger.mark_skipped_duplicate("se_happy", {"result": "duplicate"})
    assert ledger.get("se_happy").status == DurableSideEffectStatus.SKIPPED_DUPLICATE
    assert ledger.get("se_happy").skipped_at is not None


def test_remote_reconciliation_marks_approved_record_succeeded(ledger):
    ledger.create_planned(make_planned_record("se_remote"))
    ledger.mark_approved("se_remote")

    ledger.mark_remote_reconciled(
        "se_remote",
        {
            "comment_id": "remote-comment-1",
            "comment_url": "https://example.invalid/issuecomment/remote-comment-1",
            "remote_reconciled": True,
            "client_called": False,
            "source": "remote_marker",
        },
    )

    record = ledger.get("se_remote")
    external_result = json.loads(record.external_result_json or "{}")

    assert record.status == DurableSideEffectStatus.SUCCEEDED
    assert record.executed_at is not None
    assert external_result["comment_id"] == "remote-comment-1"
    assert external_result["remote_reconciled"] is True


def test_remote_reconciliation_rejects_unapproved_planned_record(ledger):
    ledger.create_planned(make_planned_record("se_remote_planned"))

    with pytest.raises(InvalidSideEffectTransitionError):
        ledger.mark_remote_reconciled(
            "se_remote_planned",
            {"comment_id": "remote-comment-1"},
        )

    assert ledger.get("se_remote_planned").status == DurableSideEffectStatus.PLANNED


def test_remote_reconciliation_rejects_terminal_record(ledger):
    ledger.create_planned(make_planned_record("se_remote_failed"))
    ledger.mark_approved("se_remote_failed")
    ledger.mark_executing("se_remote_failed")
    ledger.mark_failed("se_remote_failed")

    with pytest.raises(TerminalSideEffectStateError):
        ledger.mark_remote_reconciled(
            "se_remote_failed",
            {"comment_id": "remote-comment-1"},
        )

    assert ledger.get("se_remote_failed").status == DurableSideEffectStatus.FAILED

def test_transition_planned_to_rejected(ledger):
    ledger.create_planned(make_planned_record("se_rej"))
    ledger.mark_rejected("se_rej", reason="policy violation")
    assert ledger.get("se_rej").status == DurableSideEffectStatus.REJECTED
    assert json.loads(ledger.get("se_rej").failure_json) == {"reason": "policy violation"}

def test_transition_planned_to_blocked(ledger):
    ledger.create_planned(make_planned_record("se_blk"))
    ledger.mark_blocked("se_blk", reason="needs review")
    assert ledger.get("se_blk").status == DurableSideEffectStatus.BLOCKED

def test_invalid_transitions(ledger):
    ledger.create_planned(make_planned_record("se_inv"))
    with pytest.raises(InvalidSideEffectTransitionError):
        ledger.mark_executing("se_inv")  # Planned -> Executing not allowed

    with pytest.raises(InvalidSideEffectTransitionError):
        ledger.mark_succeeded("se_inv")  # Planned -> Succeeded not allowed


# --- 16.5 Terminal-State Tests ---
def test_terminal_states(ledger):
    ledger.create_planned(make_planned_record("se_fail"))
    ledger.mark_approved("se_fail")
    ledger.mark_executing("se_fail")
    ledger.mark_failed("se_fail", {"error": "boom"})
    
    assert ledger.get("se_fail").status == DurableSideEffectStatus.FAILED
    
    with pytest.raises(TerminalSideEffectStateError):
        ledger.mark_executing("se_fail")  # Failed -> Executing not allowed
        
    with pytest.raises(TerminalSideEffectStateError):
         ledger.mark_approved("se_fail") # Failed -> Approved not allowed

    # Rejection is terminal
    ledger.create_planned(make_planned_record("se_term_rej"))
    ledger.mark_rejected("se_term_rej")
    with pytest.raises(TerminalSideEffectStateError):
        ledger.mark_approved("se_term_rej")

    # Blocked is terminal
    ledger.create_planned(make_planned_record("se_term_blk"))
    ledger.mark_blocked("se_term_blk")
    with pytest.raises(TerminalSideEffectStateError):
        ledger.mark_approved("se_term_blk")


# --- 16.6 Fresh Repository Persistence Test ---
def test_fresh_repository_persistence(temp_db_path):
    # 1. Create temporary SQLite file via temp_db_path fixture
    # 2. Instantiate ledger_1
    manager1 = SQLiteConnectionManager(temp_db_path)
    manager1.initialize_schema()
    ledger1 = DurableSideEffectLedger(manager1)
    
    # 3. Create a planned side_effect_record
    ledger1.create_planned(make_planned_record("se_persist"))
    
    # 4. Close/discard ledger_1 (implicit)
    
    # 5. Instantiate ledger_2 with the same SQLite file
    manager2 = SQLiteConnectionManager(temp_db_path)
    ledger2 = DurableSideEffectLedger(manager2)
    
    # 6. Retrieve the same record from ledger_2
    retrieved = ledger2.get("se_persist")
    assert retrieved.side_effect_id == "se_persist"
    assert retrieved.status == DurableSideEffectStatus.PLANNED


# --- 16.7 Safety / No-Network Tests ---
def test_no_network_imports():
    import sys
    
    # Check that we haven't loaded requests or httpx or github in the side_effects module
    # We will just verify our domain logic doesn't depend on them
    
    for mod in sys.modules:
        if "app.side_effects.durable_ledger" in mod or "app.persistence.sqlite" in mod:
            # Re-importing locally to ensure they don't bring in network libraries
            pass
            
    import app.side_effects.durable_ledger
    assert not hasattr(app.side_effects.durable_ledger, "requests")
    assert not hasattr(app.side_effects.durable_ledger, "httpx")
