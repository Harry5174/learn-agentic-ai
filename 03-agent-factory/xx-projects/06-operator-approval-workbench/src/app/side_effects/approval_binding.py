"""Durable approval binding store for A4.2.

SQLite-backed store that persists human approval decisions against the exact
validated side-effect action. Enforces the core A4.2 invariant:

    An approval authorizes exactly one validated side-effect action,
    identified by the same side_effect_id and validated_arguments_hash.

Design decisions:
- approve() and reject() update both approval_bindings and side_effect_records
  in a single SQLite transaction to avoid partial state.
- expire() does NOT mutate side_effect_records status. Expired is an
  approval-binding state, not a side-effect execution state.
- assert_approved_for_action() is a pure read check. It does not mutate
  any state, does not execute tools, and does not call any client.
"""

import sqlite3
from datetime import datetime, timezone

from app.persistence.sqlite import SQLiteConnectionManager
from app.side_effects.approval_schemas import (
    ApprovalBindingNotFoundError,
    ApprovalBindingRecord,
    ApprovalBindingStatus,
    ApprovalNotAuthorizedError,
    ApprovalSideEffectMismatchError,
    DuplicateApprovalBindingError,
    InvalidApprovalTransitionError,
    SideEffectForApprovalNotFoundError,
    SideEffectNotApprovableError,
    TerminalApprovalStateError,
)
from app.side_effects.durable_schemas import (
    DurableSideEffectStatus,
    SideEffectRecordNotFoundError,
)
from app.side_effects.durable_ledger import DurableSideEffectLedger


class DurableApprovalBindingStore:
    """SQLite-backed store for durable approval bindings.

    Persists approval decisions against exact side_effect_id and
    validated_arguments_hash. Requires a DurableSideEffectLedger for
    side-effect record validation and status interaction.
    """

    TERMINAL_STATUSES = {
        ApprovalBindingStatus.APPROVED,
        ApprovalBindingStatus.REJECTED,
        ApprovalBindingStatus.EXPIRED,
    }

    VALID_TRANSITIONS = {
        ApprovalBindingStatus.PENDING: {
            ApprovalBindingStatus.APPROVED,
            ApprovalBindingStatus.REJECTED,
            ApprovalBindingStatus.EXPIRED,
        },
    }

    # Side-effect statuses that are NOT approvable.
    # Only PLANNED is approvable in A4.2.
    NON_APPROVABLE_STATUSES = {
        DurableSideEffectStatus.APPROVED,
        DurableSideEffectStatus.EXECUTING,
        DurableSideEffectStatus.SUCCEEDED,
        DurableSideEffectStatus.FAILED,
        DurableSideEffectStatus.SKIPPED_DUPLICATE,
        DurableSideEffectStatus.REJECTED,
        DurableSideEffectStatus.BLOCKED,
    }

    def __init__(
        self,
        db_manager: SQLiteConnectionManager,
        ledger: DurableSideEffectLedger,
    ):
        self.db_manager = db_manager
        self.ledger = ledger

    def initialize(self) -> None:
        """Initialize the approval binding schema."""
        self.db_manager.initialize_schema()

    def create_pending(self, binding: ApprovalBindingRecord) -> None:
        """Create a new pending approval binding for an existing planned side effect.

        Validates:
        - side_effect_id exists in the ledger
        - side_effect record is in PLANNED state
        - run_id, skill_id, step_id, tool_name, validated_arguments_hash all match
        - no existing binding for the same side_effect_id
        - no existing binding with the same approval_id
        """
        if binding.approval_status != ApprovalBindingStatus.PENDING:
            raise ValueError("Initial binding must be in PENDING state")

        # 1. Verify side-effect record exists
        try:
            se_record = self.ledger.get(binding.side_effect_id)
        except SideEffectRecordNotFoundError:
            raise SideEffectForApprovalNotFoundError(
                f"Side-effect record {binding.side_effect_id} does not exist"
            )

        # 2. Verify side-effect is in PLANNED state
        if se_record.status != DurableSideEffectStatus.PLANNED:
            raise SideEffectNotApprovableError(
                f"Side-effect {binding.side_effect_id} is in state "
                f"{se_record.status}, not planned"
            )

        # 3. Verify all matching fields
        mismatches = []
        if binding.run_id != se_record.run_id:
            mismatches.append(f"run_id: {binding.run_id} != {se_record.run_id}")
        if binding.skill_id != se_record.skill_id:
            mismatches.append(f"skill_id: {binding.skill_id} != {se_record.skill_id}")
        if binding.step_id != se_record.step_id:
            mismatches.append(f"step_id: {binding.step_id} != {se_record.step_id}")
        if binding.tool_name != se_record.tool_name:
            mismatches.append(
                f"tool_name: {binding.tool_name} != {se_record.tool_name}"
            )
        if binding.validated_arguments_hash != se_record.validated_arguments_hash:
            mismatches.append(
                f"validated_arguments_hash: {binding.validated_arguments_hash} "
                f"!= {se_record.validated_arguments_hash}"
            )

        if mismatches:
            raise ApprovalSideEffectMismatchError(
                f"Approval binding does not match side-effect record: "
                f"{'; '.join(mismatches)}"
            )

        # 4. Insert the binding
        sql = """
            INSERT INTO approval_bindings (
                approval_id, run_id, skill_id, step_id, tool_name,
                side_effect_id, validated_arguments_hash, approval_status,
                requested_by, decided_by, reason,
                created_at, decided_at, expires_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        try:
            with self.db_manager.get_connection() as conn:
                conn.execute(
                    sql,
                    (
                        binding.approval_id,
                        binding.run_id,
                        binding.skill_id,
                        binding.step_id,
                        binding.tool_name,
                        binding.side_effect_id,
                        binding.validated_arguments_hash,
                        binding.approval_status,
                        binding.requested_by,
                        binding.decided_by,
                        binding.reason,
                        binding.created_at,
                        binding.decided_at,
                        binding.expires_at,
                    ),
                )
                conn.commit()
        except sqlite3.IntegrityError as e:
            error_msg = str(e)
            if "UNIQUE constraint failed: approval_bindings.side_effect_id" in error_msg:
                raise DuplicateApprovalBindingError(
                    f"Approval binding already exists for "
                    f"side_effect_id {binding.side_effect_id}"
                )
            if "UNIQUE constraint failed: approval_bindings.approval_id" in error_msg:
                raise DuplicateApprovalBindingError(
                    f"Approval binding {binding.approval_id} already exists"
                )
            raise DuplicateApprovalBindingError(str(e))  # pragma: no cover

    def get(self, approval_id: str) -> ApprovalBindingRecord:
        """Retrieve an approval binding by approval_id."""
        sql = "SELECT * FROM approval_bindings WHERE approval_id = ?"
        with self.db_manager.get_connection() as conn:
            row = conn.execute(sql, (approval_id,)).fetchone()

        if not row:
            raise ApprovalBindingNotFoundError(
                f"Approval binding {approval_id} not found"
            )

        return ApprovalBindingRecord(**dict(row))

    def get_by_side_effect_id(self, side_effect_id: str) -> ApprovalBindingRecord:
        """Retrieve an approval binding by side_effect_id."""
        sql = "SELECT * FROM approval_bindings WHERE side_effect_id = ?"
        with self.db_manager.get_connection() as conn:
            row = conn.execute(sql, (side_effect_id,)).fetchone()

        if not row:
            raise ApprovalBindingNotFoundError(
                f"Approval binding for side_effect_id {side_effect_id} not found"
            )

        return ApprovalBindingRecord(**dict(row))

    def exists_for_side_effect(self, side_effect_id: str) -> bool:
        """Check if an approval binding exists for the given side_effect_id."""
        sql = "SELECT 1 FROM approval_bindings WHERE side_effect_id = ?"
        with self.db_manager.get_connection() as conn:
            row = conn.execute(sql, (side_effect_id,)).fetchone()
            return bool(row)

    def approve(
        self,
        approval_id: str,
        decided_by: str,
        reason: str | None = None,
    ) -> None:
        """Transition a pending approval binding to approved.

        Also updates the side-effect record from planned to approved.
        Both updates occur in a single SQLite transaction to avoid
        partial state between approval_bindings and side_effect_records.
        """
        self._decide(
            approval_id=approval_id,
            new_status=ApprovalBindingStatus.APPROVED,
            decided_by=decided_by,
            reason=reason,
            update_side_effect=True,
        )

    def reject(
        self,
        approval_id: str,
        decided_by: str,
        reason: str | None = None,
    ) -> None:
        """Transition a pending approval binding to rejected.

        Also updates the side-effect record from planned to rejected.
        Both updates occur in a single SQLite transaction to avoid
        partial state between approval_bindings and side_effect_records.
        """
        self._decide(
            approval_id=approval_id,
            new_status=ApprovalBindingStatus.REJECTED,
            decided_by=decided_by,
            reason=reason,
            update_side_effect=True,
        )

    def expire(
        self,
        approval_id: str,
        reason: str | None = None,
    ) -> None:
        """Transition a pending approval binding to expired.

        Does NOT mutate the side-effect record status. Expired is an
        approval-binding state, not a side-effect execution state.
        The side-effect record remains in planned state.
        """
        self._decide(
            approval_id=approval_id,
            new_status=ApprovalBindingStatus.EXPIRED,
            decided_by=None,
            reason=reason,
            update_side_effect=False,
        )

    def _decide(
        self,
        approval_id: str,
        new_status: ApprovalBindingStatus,
        decided_by: str | None,
        reason: str | None,
        update_side_effect: bool,
    ) -> None:
        """Internal: perform an approval status transition.

        When update_side_effect is True, both approval_bindings and
        side_effect_records are updated in a single SQLite transaction
        to avoid partial state.
        """
        # 1. Retrieve current binding
        binding = self.get(approval_id)

        # 2. Check terminal state
        if binding.approval_status in self.TERMINAL_STATUSES:
            raise TerminalApprovalStateError(
                f"Cannot mutate approval binding {approval_id} "
                f"in terminal state {binding.approval_status}"
            )

        # 3. Check valid transition
        allowed = self.VALID_TRANSITIONS.get(binding.approval_status, set())
        if new_status not in allowed:
            raise InvalidApprovalTransitionError(
                f"Cannot transition from {binding.approval_status} to {new_status}"
            )

        now = datetime.now(timezone.utc).isoformat()

        # 4. Perform updates in a single transaction
        with self.db_manager.get_connection() as conn:
            # Update approval binding
            conn.execute(
                """
                UPDATE approval_bindings
                SET approval_status = ?, decided_by = ?, reason = ?, decided_at = ?
                WHERE approval_id = ?
                """,
                (new_status, decided_by, reason, now, approval_id),
            )

            # Update side-effect record in the same transaction if required
            if update_side_effect:
                if new_status == ApprovalBindingStatus.APPROVED:
                    conn.execute(
                        """
                        UPDATE side_effect_records
                        SET status = ?, approved_at = ?, updated_at = ?
                        WHERE side_effect_id = ?
                        """,
                        (
                            DurableSideEffectStatus.APPROVED,
                            now,
                            now,
                            binding.side_effect_id,
                        ),
                    )
                elif new_status == ApprovalBindingStatus.REJECTED:
                    import json

                    failure_json = (
                        json.dumps({"reason": reason}) if reason else None
                    )
                    conn.execute(
                        """
                        UPDATE side_effect_records
                        SET status = ?, failure_json = ?, updated_at = ?
                        WHERE side_effect_id = ?
                        """,
                        (
                            DurableSideEffectStatus.REJECTED,
                            failure_json,
                            now,
                            binding.side_effect_id,
                        ),
                    )

            conn.commit()

    def assert_approved_for_action(
        self,
        side_effect_id: str,
        validated_arguments_hash: str,
    ) -> None:
        """Assert that an approved binding exists for the exact action.

        This is a pure read check. It does not mutate any state,
        does not execute tools, does not call any client, and does
        not modify side_effect_records.

        Raises ApprovalNotAuthorizedError if:
        - no binding exists for the side_effect_id
        - binding is not in approved state
        - validated_arguments_hash does not match
        """
        try:
            binding = self.get_by_side_effect_id(side_effect_id)
        except ApprovalBindingNotFoundError:
            raise ApprovalNotAuthorizedError(
                f"No approval binding found for side_effect_id {side_effect_id}"
            )

        if binding.approval_status != ApprovalBindingStatus.APPROVED:
            raise ApprovalNotAuthorizedError(
                f"Approval binding for {side_effect_id} is "
                f"{binding.approval_status}, not approved"
            )

        if binding.validated_arguments_hash != validated_arguments_hash:
            raise ApprovalNotAuthorizedError(
                f"Approval binding validated_arguments_hash mismatch for "
                f"{side_effect_id}: expected {validated_arguments_hash}, "
                f"got {binding.validated_arguments_hash}"
            )

        try:
            se_record = self.ledger.get(side_effect_id)
        except SideEffectRecordNotFoundError:
            raise ApprovalNotAuthorizedError(
                f"No side-effect record found for side_effect_id {side_effect_id}"
            )

        mismatches = []
        if binding.run_id != se_record.run_id:
            mismatches.append("run_id")
        if binding.skill_id != se_record.skill_id:
            mismatches.append("skill_id")
        if binding.step_id != se_record.step_id:
            mismatches.append("step_id")
        if binding.tool_name != se_record.tool_name:
            mismatches.append("tool_name")
        if binding.validated_arguments_hash != se_record.validated_arguments_hash:
            mismatches.append("validated_arguments_hash")

        if mismatches:
            raise ApprovalNotAuthorizedError(
                "Approval binding does not match side-effect record: "
                f"{', '.join(mismatches)}"
            )

    def close(self) -> None:
        """Close the store resources if necessary."""
        # SQLite connection manager opens connections on demand.
        # Global or shared connections could be closed here if stored.
        pass
