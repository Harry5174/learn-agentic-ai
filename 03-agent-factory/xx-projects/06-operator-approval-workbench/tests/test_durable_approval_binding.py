"""Tests for A4.2 durable approval binding.

Proves the core A4.2 invariant:
    An approval authorizes exactly one validated side-effect action,
    identified by the same side_effect_id and validated_arguments_hash.

Test sections:
    15.1 — Schema / Init Tests
    15.2 — Create / Read Tests
    15.3 — Side-Effect Matching Tests
    15.4 — Duplicate Tests
    15.5 — Approval Transition Tests
    15.6 — Side-Effect Status Interaction Tests
    15.7 — Exact Authorization Assertion Tests
    15.8 — Persistence Tests
    15.9 — Safety / No-Network Tests
"""

from datetime import datetime, timezone

import pytest

from app.persistence.sqlite import SQLiteConnectionManager
from app.side_effects.approval_binding import DurableApprovalBindingStore
from app.side_effects.approval_schemas import (
    ApprovalBindingNotFoundError,
    ApprovalBindingRecord,
    ApprovalBindingStatus,
    ApprovalNotAuthorizedError,
    ApprovalSideEffectMismatchError,
    DuplicateApprovalBindingError,
    SideEffectForApprovalNotFoundError,
    SideEffectNotApprovableError,
    TerminalApprovalStateError,
)
from app.side_effects.durable_ledger import DurableSideEffectLedger
from app.side_effects.durable_schemas import (
    DurableSideEffectRecord,
    DurableSideEffectStatus,
)


# --- Fixtures ---


@pytest.fixture
def temp_db_path(tmp_path):
    return tmp_path / "test_approval.sqlite"


@pytest.fixture
def db_manager(temp_db_path):
    manager = SQLiteConnectionManager(temp_db_path)
    manager.initialize_schema()
    return manager


@pytest.fixture
def ledger(db_manager):
    return DurableSideEffectLedger(db_manager)


@pytest.fixture
def store(db_manager, ledger):
    return DurableApprovalBindingStore(db_manager, ledger)


# --- Helpers ---


def make_planned_se(
    side_effect_id: str = "se_1",
    run_id: str = "run_1",
    skill_id: str = "skill_1",
    step_id: str = "step_1",
    tool_name: str = "test_tool",
    validated_arguments_hash: str = "hash_abc",
) -> DurableSideEffectRecord:
    now = datetime.now(timezone.utc).isoformat()
    return DurableSideEffectRecord(
        side_effect_id=side_effect_id,
        run_id=run_id,
        skill_id=skill_id,
        step_id=step_id,
        tool_name=tool_name,
        validated_arguments_hash=validated_arguments_hash,
        status=DurableSideEffectStatus.PLANNED,
        created_at=now,
        updated_at=now,
    )


def make_pending_binding(
    approval_id: str = "appr_1",
    side_effect_id: str = "se_1",
    run_id: str = "run_1",
    skill_id: str = "skill_1",
    step_id: str = "step_1",
    tool_name: str = "test_tool",
    validated_arguments_hash: str = "hash_abc",
    requested_by: str | None = "operator_1",
) -> ApprovalBindingRecord:
    now = datetime.now(timezone.utc).isoformat()
    return ApprovalBindingRecord(
        approval_id=approval_id,
        run_id=run_id,
        skill_id=skill_id,
        step_id=step_id,
        tool_name=tool_name,
        side_effect_id=side_effect_id,
        validated_arguments_hash=validated_arguments_hash,
        approval_status=ApprovalBindingStatus.PENDING,
        requested_by=requested_by,
        created_at=now,
    )


def create_planned_and_pending(ledger, store, se_id="se_1", appr_id="appr_1"):
    """Helper: create a planned side effect and a pending approval binding."""
    se = make_planned_se(side_effect_id=se_id)
    ledger.create_planned(se)
    binding = make_pending_binding(approval_id=appr_id, side_effect_id=se_id)
    store.create_pending(binding)
    return se, binding


# ============================================================
# 15.1 — Schema / Init Tests
# ============================================================


class TestSchemaInit:
    """Prove schema initialization works correctly."""

    def test_approval_bindings_schema_initializes(self, temp_db_path):
        manager = SQLiteConnectionManager(temp_db_path)
        manager.initialize_schema()

        with manager.get_connection() as conn:
            cursor = conn.execute("PRAGMA table_info(approval_bindings)")
            columns = [row["name"] for row in cursor.fetchall()]

        assert "approval_id" in columns
        assert "side_effect_id" in columns
        assert "validated_arguments_hash" in columns
        assert "approval_status" in columns
        assert "run_id" in columns
        assert "decided_by" in columns
        assert "created_at" in columns

    def test_schema_initialization_is_idempotent(self, temp_db_path):
        manager = SQLiteConnectionManager(temp_db_path)
        manager.initialize_schema()
        # Running again should not error
        manager.initialize_schema()

        with manager.get_connection() as conn:
            cursor = conn.execute("PRAGMA table_info(approval_bindings)")
            columns = [row["name"] for row in cursor.fetchall()]
            assert "approval_id" in columns

    def test_store_can_use_temp_sqlite(self, temp_db_path):
        manager = SQLiteConnectionManager(temp_db_path)
        manager.initialize_schema()
        ledger = DurableSideEffectLedger(manager)
        store = DurableApprovalBindingStore(manager, ledger)
        # Should not raise
        assert store is not None

    def test_side_effect_records_still_initializes(self, temp_db_path):
        manager = SQLiteConnectionManager(temp_db_path)
        manager.initialize_schema()

        with manager.get_connection() as conn:
            cursor = conn.execute("PRAGMA table_info(side_effect_records)")
            columns = [row["name"] for row in cursor.fetchall()]

        assert "side_effect_id" in columns
        assert "run_id" in columns


# ============================================================
# 15.2 — Create / Read Tests
# ============================================================


class TestCreateRead:
    """Prove basic create and read operations."""

    def test_create_pending_for_planned_side_effect(self, ledger, store):
        se = make_planned_se()
        ledger.create_planned(se)

        binding = make_pending_binding()
        store.create_pending(binding)

        retrieved = store.get("appr_1")
        assert retrieved.approval_id == "appr_1"
        assert retrieved.approval_status == ApprovalBindingStatus.PENDING

    def test_retrieve_by_approval_id(self, ledger, store):
        create_planned_and_pending(ledger, store)
        retrieved = store.get("appr_1")
        assert retrieved.approval_id == "appr_1"
        assert retrieved.side_effect_id == "se_1"

    def test_retrieve_by_side_effect_id(self, ledger, store):
        create_planned_and_pending(ledger, store)
        retrieved = store.get_by_side_effect_id("se_1")
        assert retrieved.approval_id == "appr_1"
        assert retrieved.side_effect_id == "se_1"

    def test_missing_approval_raises_not_found(self, store):
        with pytest.raises(ApprovalBindingNotFoundError):
            store.get("appr_nonexistent")

    def test_missing_side_effect_id_raises_not_found(self, store):
        with pytest.raises(ApprovalBindingNotFoundError):
            store.get_by_side_effect_id("se_nonexistent")

    def test_created_at_is_persisted(self, ledger, store):
        create_planned_and_pending(ledger, store)
        retrieved = store.get("appr_1")
        assert retrieved.created_at is not None
        assert len(retrieved.created_at) > 0

    def test_approval_status_starts_pending(self, ledger, store):
        create_planned_and_pending(ledger, store)
        retrieved = store.get("appr_1")
        assert retrieved.approval_status == ApprovalBindingStatus.PENDING

    def test_exists_for_side_effect(self, ledger, store):
        assert store.exists_for_side_effect("se_1") is False
        create_planned_and_pending(ledger, store)
        assert store.exists_for_side_effect("se_1") is True


# ============================================================
# 15.3 — Side-Effect Matching Tests
# ============================================================


class TestSideEffectMatching:
    """Prove approval binding fails safely on mismatch."""

    def test_fails_when_side_effect_does_not_exist(self, store):
        binding = make_pending_binding(side_effect_id="se_nonexistent")
        with pytest.raises(SideEffectForApprovalNotFoundError):
            store.create_pending(binding)

    def test_fails_when_side_effect_not_planned(self, ledger, store):
        se = make_planned_se()
        ledger.create_planned(se)
        ledger.mark_approved("se_1")

        binding = make_pending_binding()
        with pytest.raises(SideEffectNotApprovableError):
            store.create_pending(binding)

    def test_fails_when_run_id_mismatches(self, ledger, store):
        se = make_planned_se()
        ledger.create_planned(se)

        binding = make_pending_binding(run_id="wrong_run")
        with pytest.raises(ApprovalSideEffectMismatchError, match="run_id"):
            store.create_pending(binding)

    def test_fails_when_skill_id_mismatches(self, ledger, store):
        se = make_planned_se()
        ledger.create_planned(se)

        binding = make_pending_binding(skill_id="wrong_skill")
        with pytest.raises(ApprovalSideEffectMismatchError, match="skill_id"):
            store.create_pending(binding)

    def test_fails_when_step_id_mismatches(self, ledger, store):
        se = make_planned_se()
        ledger.create_planned(se)

        binding = make_pending_binding(step_id="wrong_step")
        with pytest.raises(ApprovalSideEffectMismatchError, match="step_id"):
            store.create_pending(binding)

    def test_fails_when_tool_name_mismatches(self, ledger, store):
        se = make_planned_se()
        ledger.create_planned(se)

        binding = make_pending_binding(tool_name="wrong_tool")
        with pytest.raises(ApprovalSideEffectMismatchError, match="tool_name"):
            store.create_pending(binding)

    def test_fails_when_validated_arguments_hash_mismatches(self, ledger, store):
        se = make_planned_se()
        ledger.create_planned(se)

        binding = make_pending_binding(validated_arguments_hash="wrong_hash")
        with pytest.raises(
            ApprovalSideEffectMismatchError, match="validated_arguments_hash"
        ):
            store.create_pending(binding)


# ============================================================
# 15.4 — Duplicate Tests
# ============================================================


class TestDuplicates:
    """Prove duplicate protection works."""

    def test_cannot_create_duplicate_approval_id(self, ledger, store):
        # Create two different side effects
        ledger.create_planned(make_planned_se(side_effect_id="se_1"))
        ledger.create_planned(make_planned_se(side_effect_id="se_2"))

        store.create_pending(
            make_pending_binding(approval_id="appr_dup", side_effect_id="se_1")
        )
        with pytest.raises(DuplicateApprovalBindingError):
            store.create_pending(
                make_pending_binding(approval_id="appr_dup", side_effect_id="se_2")
            )

    def test_cannot_create_multiple_bindings_for_same_side_effect(
        self, ledger, store
    ):
        ledger.create_planned(make_planned_se(side_effect_id="se_1"))
        store.create_pending(
            make_pending_binding(approval_id="appr_1", side_effect_id="se_1")
        )
        with pytest.raises(DuplicateApprovalBindingError):
            store.create_pending(
                make_pending_binding(approval_id="appr_2", side_effect_id="se_1")
            )

    def test_original_binding_not_overwritten_on_duplicate(self, ledger, store):
        ledger.create_planned(make_planned_se(side_effect_id="se_1"))
        store.create_pending(
            make_pending_binding(
                approval_id="appr_orig",
                side_effect_id="se_1",
                requested_by="original_operator",
            )
        )

        with pytest.raises(DuplicateApprovalBindingError):
            store.create_pending(
                make_pending_binding(
                    approval_id="appr_dup",
                    side_effect_id="se_1",
                    requested_by="different_operator",
                )
            )

        # Original is still intact
        retrieved = store.get("appr_orig")
        assert retrieved.requested_by == "original_operator"

    def test_duplicate_raises_controlled_error(self, ledger, store):
        ledger.create_planned(make_planned_se())
        store.create_pending(make_pending_binding())

        with pytest.raises(DuplicateApprovalBindingError):
            store.create_pending(make_pending_binding())


# ============================================================
# 15.5 — Approval Transition Tests
# ============================================================


class TestApprovalTransitions:
    """Prove allowed and forbidden transitions."""

    # Allowed transitions

    def test_pending_to_approved(self, ledger, store):
        create_planned_and_pending(ledger, store)
        store.approve("appr_1", decided_by="admin_1", reason="looks good")

        binding = store.get("appr_1")
        assert binding.approval_status == ApprovalBindingStatus.APPROVED
        assert binding.decided_by == "admin_1"
        assert binding.reason == "looks good"
        assert binding.decided_at is not None

    def test_pending_to_rejected(self, ledger, store):
        create_planned_and_pending(ledger, store)
        store.reject("appr_1", decided_by="admin_1", reason="not allowed")

        binding = store.get("appr_1")
        assert binding.approval_status == ApprovalBindingStatus.REJECTED
        assert binding.decided_by == "admin_1"

    def test_pending_to_expired(self, ledger, store):
        create_planned_and_pending(ledger, store)
        store.expire("appr_1", reason="timed out")

        binding = store.get("appr_1")
        assert binding.approval_status == ApprovalBindingStatus.EXPIRED
        assert binding.reason == "timed out"

    # Forbidden transitions

    def test_approved_to_rejected_forbidden(self, ledger, store):
        create_planned_and_pending(ledger, store)
        store.approve("appr_1", decided_by="admin_1")

        with pytest.raises(TerminalApprovalStateError):
            store.reject("appr_1", decided_by="admin_1")

    def test_approved_to_expired_forbidden(self, ledger, store):
        create_planned_and_pending(ledger, store)
        store.approve("appr_1", decided_by="admin_1")

        with pytest.raises(TerminalApprovalStateError):
            store.expire("appr_1")

    def test_rejected_to_approved_forbidden(self, ledger, store):
        create_planned_and_pending(ledger, store)
        store.reject("appr_1", decided_by="admin_1")

        with pytest.raises(TerminalApprovalStateError):
            store.approve("appr_1", decided_by="admin_1")

    def test_expired_to_approved_forbidden(self, ledger, store):
        create_planned_and_pending(ledger, store)
        store.expire("appr_1")

        with pytest.raises(TerminalApprovalStateError):
            store.approve("appr_1", decided_by="admin_1")

    def test_expired_to_rejected_forbidden(self, ledger, store):
        create_planned_and_pending(ledger, store)
        store.expire("appr_1")

        with pytest.raises(TerminalApprovalStateError):
            store.reject("appr_1", decided_by="admin_1")


# ============================================================
# 15.6 — Side-Effect Status Interaction Tests
# ============================================================


class TestSideEffectStatusInteraction:
    """Prove correct interaction between approval decisions and side-effect status."""

    def test_approving_updates_side_effect_to_approved(self, ledger, store):
        create_planned_and_pending(ledger, store)
        store.approve("appr_1", decided_by="admin_1")

        se = ledger.get("se_1")
        assert se.status == DurableSideEffectStatus.APPROVED

    def test_rejecting_updates_side_effect_to_rejected(self, ledger, store):
        create_planned_and_pending(ledger, store)
        store.reject("appr_1", decided_by="admin_1", reason="denied")

        se = ledger.get("se_1")
        assert se.status == DurableSideEffectStatus.REJECTED

    def test_expiring_does_not_move_side_effect_to_executing(self, ledger, store):
        create_planned_and_pending(ledger, store)
        store.expire("appr_1")

        se = ledger.get("se_1")
        assert se.status != DurableSideEffectStatus.EXECUTING

    def test_expiring_leaves_side_effect_planned(self, ledger, store):
        create_planned_and_pending(ledger, store)
        store.expire("appr_1")

        se = ledger.get("se_1")
        assert se.status == DurableSideEffectStatus.PLANNED

    def test_cannot_approve_side_effect_already_blocked(self, ledger, store):
        se = make_planned_se(side_effect_id="se_blocked")
        ledger.create_planned(se)
        ledger.mark_blocked("se_blocked", reason="policy")

        binding = make_pending_binding(
            approval_id="appr_blocked", side_effect_id="se_blocked"
        )
        with pytest.raises(SideEffectNotApprovableError):
            store.create_pending(binding)

    def test_cannot_approve_side_effect_already_failed(self, ledger, store):
        se = make_planned_se(side_effect_id="se_fail")
        ledger.create_planned(se)
        ledger.mark_approved("se_fail")
        ledger.mark_executing("se_fail")
        ledger.mark_failed("se_fail", {"error": "boom"})

        binding = make_pending_binding(
            approval_id="appr_fail", side_effect_id="se_fail"
        )
        with pytest.raises(SideEffectNotApprovableError):
            store.create_pending(binding)

    def test_cannot_approve_side_effect_already_succeeded(self, ledger, store):
        se = make_planned_se(side_effect_id="se_succ")
        ledger.create_planned(se)
        ledger.mark_approved("se_succ")
        ledger.mark_executing("se_succ")
        ledger.mark_succeeded("se_succ")

        binding = make_pending_binding(
            approval_id="appr_succ", side_effect_id="se_succ"
        )
        with pytest.raises(SideEffectNotApprovableError):
            store.create_pending(binding)

    def test_cannot_approve_side_effect_already_rejected(self, ledger, store):
        se = make_planned_se(side_effect_id="se_rej")
        ledger.create_planned(se)
        ledger.mark_rejected("se_rej")

        binding = make_pending_binding(
            approval_id="appr_rej", side_effect_id="se_rej"
        )
        with pytest.raises(SideEffectNotApprovableError):
            store.create_pending(binding)

    def test_cannot_approve_side_effect_already_executing(self, ledger, store):
        se = make_planned_se(side_effect_id="se_exec")
        ledger.create_planned(se)
        ledger.mark_approved("se_exec")
        ledger.mark_executing("se_exec")

        binding = make_pending_binding(
            approval_id="appr_exec", side_effect_id="se_exec"
        )
        with pytest.raises(SideEffectNotApprovableError):
            store.create_pending(binding)


# ============================================================
# 15.7 — Exact Authorization Assertion Tests
# ============================================================


class TestAssertApprovedForAction:
    """Prove assert_approved_for_action behavior."""

    def test_passes_for_exact_match(self, ledger, store):
        create_planned_and_pending(ledger, store)
        store.approve("appr_1", decided_by="admin_1")

        # Should not raise
        store.assert_approved_for_action("se_1", "hash_abc")

    def test_fails_for_wrong_side_effect_id(self, ledger, store):
        create_planned_and_pending(ledger, store)
        store.approve("appr_1", decided_by="admin_1")

        with pytest.raises(ApprovalNotAuthorizedError):
            store.assert_approved_for_action("se_wrong", "hash_abc")

    def test_fails_for_wrong_validated_arguments_hash(self, ledger, store):
        create_planned_and_pending(ledger, store)
        store.approve("appr_1", decided_by="admin_1")

        with pytest.raises(ApprovalNotAuthorizedError):
            store.assert_approved_for_action("se_1", "wrong_hash")

    def test_fails_for_pending_approval(self, ledger, store):
        create_planned_and_pending(ledger, store)

        with pytest.raises(ApprovalNotAuthorizedError):
            store.assert_approved_for_action("se_1", "hash_abc")

    def test_fails_for_rejected_approval(self, ledger, store):
        create_planned_and_pending(ledger, store)
        store.reject("appr_1", decided_by="admin_1")

        with pytest.raises(ApprovalNotAuthorizedError):
            store.assert_approved_for_action("se_1", "hash_abc")

    def test_fails_for_expired_approval(self, ledger, store):
        create_planned_and_pending(ledger, store)
        store.expire("appr_1")

        with pytest.raises(ApprovalNotAuthorizedError):
            store.assert_approved_for_action("se_1", "hash_abc")


# ============================================================
# 15.8 — Persistence Tests
# ============================================================


class TestPersistence:
    """Prove approval bindings survive store re-instantiation."""

    def test_approved_binding_survives_reinstantiation(self, temp_db_path):
        # 1. Create temp SQLite file
        # 2. Instantiate ledger_1 + store_1
        manager_1 = SQLiteConnectionManager(temp_db_path)
        manager_1.initialize_schema()
        ledger_1 = DurableSideEffectLedger(manager_1)
        store_1 = DurableApprovalBindingStore(manager_1, ledger_1)

        # 3. Create planned side-effect record
        se = make_planned_se()
        ledger_1.create_planned(se)

        # 4. Create pending approval binding
        binding = make_pending_binding()
        store_1.create_pending(binding)

        # 5. Approve it
        store_1.approve("appr_1", decided_by="admin_1")

        # 6. Discard store objects (implicit)

        # 7. Instantiate ledger_2 + store_2 with same SQLite file
        manager_2 = SQLiteConnectionManager(temp_db_path)
        ledger_2 = DurableSideEffectLedger(manager_2)
        store_2 = DurableApprovalBindingStore(manager_2, ledger_2)

        # 8. Retrieve approved binding
        retrieved = store_2.get("appr_1")
        assert retrieved.approval_id == "appr_1"
        assert retrieved.approval_status == ApprovalBindingStatus.APPROVED
        assert retrieved.decided_by == "admin_1"

        # 9. Assert approval still authorizes exact action
        store_2.assert_approved_for_action("se_1", "hash_abc")

        # 10. Also verify the side-effect record persisted as approved
        se_retrieved = ledger_2.get("se_1")
        assert se_retrieved.status == DurableSideEffectStatus.APPROVED


# ============================================================
# 15.9 — Safety / No-Network Tests
# ============================================================


class TestSafetyNoNetwork:
    """Prove A4.2 does not use network or GitHub client."""

    def test_no_github_token_required(self):
        import os

        # A4.2 modules should not require GITHUB_TOKEN
        assert "GITHUB_TOKEN" not in os.environ or True  # test always passes
        # The real check: our modules don't read it
        import app.side_effects.approval_binding
        import app.side_effects.approval_schemas

        source_binding = open(
            app.side_effects.approval_binding.__file__
        ).read()
        source_schemas = open(
            app.side_effects.approval_schemas.__file__
        ).read()
        assert "GITHUB_TOKEN" not in source_binding
        assert "GITHUB_TOKEN" not in source_schemas

    def test_no_fake_github_client_import(self):
        import app.side_effects.approval_binding
        import app.side_effects.approval_schemas

        source_binding = open(
            app.side_effects.approval_binding.__file__
        ).read()
        source_schemas = open(
            app.side_effects.approval_schemas.__file__
        ).read()
        assert "FakeGitHub" not in source_binding
        assert "FakeGitHub" not in source_schemas

    def test_no_network_library_import(self):
        import app.side_effects.approval_binding
        import app.side_effects.approval_schemas

        source_binding = open(
            app.side_effects.approval_binding.__file__
        ).read()
        source_schemas = open(
            app.side_effects.approval_schemas.__file__
        ).read()

        for lib in ["requests", "httpx", "PyGithub", "github.Github"]:
            assert lib not in source_binding, f"Found {lib} in approval_binding.py"
            assert lib not in source_schemas, f"Found {lib} in approval_schemas.py"

    def test_no_network_in_persistence_module(self):
        import app.persistence.sqlite

        source = open(app.persistence.sqlite.__file__).read()
        for lib in ["requests", "httpx", "PyGithub", "github.Github", "GITHUB_TOKEN"]:
            assert lib not in source, f"Found {lib} in sqlite.py"
