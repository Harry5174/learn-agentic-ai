"""Deterministic local dry-run results for ledgered operator decisions."""

from __future__ import annotations

from github_repo_steward.models import (
    ApprovalInboxItem,
    DryRunExecutionError,
    DryRunExecutionResult,
    LedgerAuditRecord,
)

DRY_RUN_COMPLETED = "dry_run_completed"
DRY_RUN_SKIPPED = "dry_run_skipped"
NOT_EXECUTED = "not_executed"
NOT_CALLED = "not_called"
NO_EXTERNAL_SIDE_EFFECT = "none"
VERIFIED_LOCAL_AUDIT_RECORD = "verified_local_audit_record"
NO_OP_REJECTED_BY_OPERATOR = "no_op_rejected_by_operator"

APPROVED_PLANNED_ACTIONS = {
    "draft_issue_comment": "would_prepare_issue_comment",
    "draft_pull_request_comment": "would_prepare_pull_request_comment",
}


def dry_run_ledger_record(
    ledger_record: LedgerAuditRecord,
    inbox_item: ApprovalInboxItem,
) -> DryRunExecutionResult:
    """Create one local dry-run result without executing the proposal."""

    _require_ledger_record(ledger_record)
    _require_inbox_item(inbox_item)
    _require_matching_pair(ledger_record, inbox_item)

    dry_run_status = (
        DRY_RUN_SKIPPED
        if ledger_record.decision == "rejected_by_operator"
        else DRY_RUN_COMPLETED
    )
    planned_action = _planned_action_for(ledger_record, inbox_item)

    return DryRunExecutionResult(
        dry_run_id=(
            f"a7x:{ledger_record.ledger_record_id}:"
            f"{ledger_record.proposal_id}"
        ),
        ledger_record_id=ledger_record.ledger_record_id,
        decision_id=ledger_record.decision_id,
        inbox_item_id=ledger_record.inbox_item_id,
        proposal_id=ledger_record.proposal_id,
        proposal_type=inbox_item.proposal_type,
        target_type=inbox_item.target_type,
        target_number=inbox_item.target_number,
        decision=ledger_record.decision,
        planned_action=planned_action,
        dry_run_status=dry_run_status,
        execution_status=NOT_EXECUTED,
        github_status=NOT_CALLED,
        external_side_effect_status=NO_EXTERNAL_SIDE_EFFECT,
        ledger_record_status=VERIFIED_LOCAL_AUDIT_RECORD,
        evidence_refs=ledger_record.evidence_refs,
        summary=_summary_for(dry_run_status, planned_action, inbox_item),
    )


def dry_run_ledger_records(
    ledger_records: list[LedgerAuditRecord],
    inbox_items: list[ApprovalInboxItem],
) -> list[DryRunExecutionResult]:
    """Create deterministic local dry-run results for supplied ledger records."""

    if not ledger_records and not inbox_items:
        return []

    inbox_by_id = _inbox_items_by_id(inbox_items)
    ledger_by_id = _ledger_records_by_id(ledger_records)

    results: list[DryRunExecutionResult] = []
    for ledger_record in sorted(
        ledger_by_id.values(),
        key=lambda record: _ledger_sort_key(record, inbox_by_id),
    ):
        inbox_item = inbox_by_id.get(ledger_record.inbox_item_id)
        if inbox_item is None:
            raise DryRunExecutionError(
                "Dry-run ledger records must reference supplied inbox items."
            )
        results.append(dry_run_ledger_record(ledger_record, inbox_item))

    return results


def _inbox_items_by_id(
    inbox_items: list[ApprovalInboxItem],
) -> dict[str, ApprovalInboxItem]:
    by_id: dict[str, ApprovalInboxItem] = {}
    for inbox_item in inbox_items:
        _require_inbox_item(inbox_item)
        if inbox_item.inbox_item_id in by_id:
            raise DryRunExecutionError(
                f"Duplicate inbox item: {inbox_item.inbox_item_id}"
            )
        by_id[inbox_item.inbox_item_id] = inbox_item
    return by_id


def _ledger_records_by_id(
    ledger_records: list[LedgerAuditRecord],
) -> dict[str, LedgerAuditRecord]:
    by_id: dict[str, LedgerAuditRecord] = {}
    for ledger_record in ledger_records:
        _require_ledger_record(ledger_record)
        if ledger_record.ledger_record_id in by_id:
            raise DryRunExecutionError(
                f"Duplicate ledger record: {ledger_record.ledger_record_id}"
            )
        by_id[ledger_record.ledger_record_id] = ledger_record
    return by_id


def _ledger_sort_key(
    ledger_record: LedgerAuditRecord,
    inbox_by_id: dict[str, ApprovalInboxItem],
) -> tuple[str, int, str, str]:
    inbox_item = inbox_by_id.get(ledger_record.inbox_item_id)
    if inbox_item is None:
        raise DryRunExecutionError(
            "Dry-run ledger records must reference supplied inbox items."
        )
    return (
        inbox_item.target_type,
        inbox_item.target_number,
        inbox_item.proposal_type,
        ledger_record.ledger_record_id,
    )


def _require_matching_pair(
    ledger_record: LedgerAuditRecord,
    inbox_item: ApprovalInboxItem,
) -> None:
    if ledger_record.inbox_item_id != inbox_item.inbox_item_id:
        raise DryRunExecutionError(
            "Ledger record and inbox item IDs must match."
        )
    if ledger_record.proposal_id != inbox_item.proposal_id:
        raise DryRunExecutionError(
            "Ledger record and inbox item proposal IDs must match."
        )
    if ledger_record.execution_status != NOT_EXECUTED:
        raise DryRunExecutionError(
            "Dry-run can only consume unexecuted ledger records."
        )
    if ledger_record.github_status != NOT_CALLED:
        raise DryRunExecutionError(
            "Dry-run can only consume ledger records with GitHub not called."
        )
    if ledger_record.executor_status != "not_triggered":
        raise DryRunExecutionError(
            "Dry-run can only consume ledger records with executor not triggered."
        )
    if ledger_record.record_status != "recorded_locally":
        raise DryRunExecutionError(
            "Dry-run can only consume locally recorded ledger records."
        )


def _planned_action_for(
    ledger_record: LedgerAuditRecord,
    inbox_item: ApprovalInboxItem,
) -> str:
    if ledger_record.decision == "rejected_by_operator":
        return NO_OP_REJECTED_BY_OPERATOR
    planned_action = APPROVED_PLANNED_ACTIONS.get(inbox_item.proposal_type)
    if planned_action is None:
        raise DryRunExecutionError(
            f"Unsupported proposal_type: {inbox_item.proposal_type}"
        )
    return planned_action


def _summary_for(
    dry_run_status: str,
    planned_action: str,
    inbox_item: ApprovalInboxItem,
) -> str:
    return (
        f"{dry_run_status}: {planned_action} for "
        f"{inbox_item.target_type} #{inbox_item.target_number}; "
        "not_executed; github_not_called; no_external_side_effect"
    )


def _require_ledger_record(ledger_record: LedgerAuditRecord) -> None:
    if not isinstance(ledger_record, LedgerAuditRecord):
        raise DryRunExecutionError(
            "Dry-run can only consume LedgerAuditRecord objects."
        )


def _require_inbox_item(inbox_item: ApprovalInboxItem) -> None:
    if not isinstance(inbox_item, ApprovalInboxItem):
        raise DryRunExecutionError(
            "Dry-run requires ApprovalInboxItem context."
        )
