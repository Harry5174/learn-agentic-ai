"""Deterministic local ledger/audit records for operator decisions."""

from __future__ import annotations

from github_repo_steward.models import (
    ApprovalInboxItem,
    LedgerAuditError,
    LedgerAuditRecord,
    OperatorDecisionRecord,
)

OPERATOR_DECISION_AUDIT = "operator_decision_audit"
RECORDED_LOCALLY = "recorded_locally"
NOT_EXECUTED = "not_executed"
NOT_CALLED = "not_called"
NOT_TRIGGERED = "not_triggered"


def record_decision_to_ledger(
    decision_record: OperatorDecisionRecord,
    inbox_item: ApprovalInboxItem,
    evidence_refs: tuple[str, ...] = (),
    source_snapshot_id: str = "",
) -> LedgerAuditRecord:
    """Create one local audit record without execution or persistence."""

    _require_operator_decision(decision_record)
    _require_inbox_item(inbox_item)
    _require_matching_pair(decision_record, inbox_item)
    _require_evidence_refs(evidence_refs)
    if not isinstance(source_snapshot_id, str):
        raise LedgerAuditError("source_snapshot_id must be a string.")

    return LedgerAuditRecord(
        ledger_record_id=(
            f"a7l:{decision_record.decision_id}:{inbox_item.inbox_item_id}"
        ),
        decision_id=decision_record.decision_id,
        inbox_item_id=inbox_item.inbox_item_id,
        proposal_id=decision_record.proposal_id,
        decision=decision_record.decision,
        decided_by=decision_record.decided_by,
        decision_rationale=decision_record.rationale,
        record_type=OPERATOR_DECISION_AUDIT,
        record_status=RECORDED_LOCALLY,
        execution_status=NOT_EXECUTED,
        github_status=NOT_CALLED,
        executor_status=NOT_TRIGGERED,
        source_snapshot_id=source_snapshot_id,
        evidence_refs=evidence_refs,
    )


def record_decisions_to_ledger(
    decision_records: list[OperatorDecisionRecord],
    inbox_items: list[ApprovalInboxItem],
    evidence_refs_by_decision_id: dict[str, tuple[str, ...]] | None = None,
    source_snapshot_id: str = "",
) -> list[LedgerAuditRecord]:
    """Create deterministic local audit records for supplied decisions."""

    if not decision_records and not inbox_items:
        if evidence_refs_by_decision_id:
            raise LedgerAuditError(
                "Evidence refs must correspond to supplied decisions."
            )
        return []
    if evidence_refs_by_decision_id is None:
        evidence_refs_by_decision_id = {}
    if not isinstance(evidence_refs_by_decision_id, dict):
        raise LedgerAuditError("evidence_refs_by_decision_id must be a dict.")
    if not isinstance(source_snapshot_id, str):
        raise LedgerAuditError("source_snapshot_id must be a string.")

    inbox_by_id = _inbox_items_by_id(inbox_items)
    decisions_by_id = _decision_records_by_id(decision_records)

    decision_ids = set(decisions_by_id)
    extra_evidence_ids = set(evidence_refs_by_decision_id) - decision_ids
    if extra_evidence_ids:
        raise LedgerAuditError(
            "Evidence refs must correspond to supplied decisions."
        )

    records: list[LedgerAuditRecord] = []
    for decision_record in sorted(
        decision_records,
        key=lambda record: _decision_sort_key(record, inbox_by_id),
    ):
        inbox_item = inbox_by_id.get(decision_record.inbox_item_id)
        if inbox_item is None:
            raise LedgerAuditError(
                "Ledger decisions must reference supplied approval inbox items."
            )
        evidence_refs = evidence_refs_by_decision_id.get(
            decision_record.decision_id,
            (),
        )
        records.append(
            record_decision_to_ledger(
                decision_record,
                inbox_item,
                evidence_refs=evidence_refs,
                source_snapshot_id=source_snapshot_id,
            )
        )

    return records


def _inbox_items_by_id(
    inbox_items: list[ApprovalInboxItem],
) -> dict[str, ApprovalInboxItem]:
    by_id: dict[str, ApprovalInboxItem] = {}
    for inbox_item in inbox_items:
        _require_inbox_item(inbox_item)
        if inbox_item.inbox_item_id in by_id:
            raise LedgerAuditError(
                f"Duplicate inbox item: {inbox_item.inbox_item_id}"
            )
        by_id[inbox_item.inbox_item_id] = inbox_item
    return by_id


def _decision_records_by_id(
    decision_records: list[OperatorDecisionRecord],
) -> dict[str, OperatorDecisionRecord]:
    by_id: dict[str, OperatorDecisionRecord] = {}
    for decision_record in decision_records:
        _require_operator_decision(decision_record)
        if decision_record.decision_id in by_id:
            raise LedgerAuditError(
                f"Duplicate operator decision: {decision_record.decision_id}"
            )
        by_id[decision_record.decision_id] = decision_record
    return by_id


def _decision_sort_key(
    decision_record: OperatorDecisionRecord,
    inbox_by_id: dict[str, ApprovalInboxItem],
) -> tuple[str, int, str, str]:
    inbox_item = inbox_by_id.get(decision_record.inbox_item_id)
    if inbox_item is None:
        raise LedgerAuditError(
            "Ledger decisions must reference supplied approval inbox items."
        )
    target_number = (
        inbox_item.target_number
        if isinstance(inbox_item.target_number, int)
        else 0
    )
    return (
        inbox_item.target_type,
        target_number,
        inbox_item.proposal_type,
        decision_record.decision_id,
    )


def _require_matching_pair(
    decision_record: OperatorDecisionRecord,
    inbox_item: ApprovalInboxItem,
) -> None:
    if decision_record.inbox_item_id != inbox_item.inbox_item_id:
        raise LedgerAuditError(
            "Operator decision and inbox item IDs must match."
        )
    if decision_record.proposal_id != inbox_item.proposal_id:
        raise LedgerAuditError(
            "Operator decision and inbox item proposal IDs must match."
        )
    if decision_record.execution_status != NOT_EXECUTED:
        raise LedgerAuditError(
            "Ledger audit records can only consume unexecuted decisions."
        )
    if decision_record.ledger_status != "not_recorded":
        raise LedgerAuditError(
            "Ledger audit records can only consume unrecorded decisions."
        )


def _require_operator_decision(
    decision_record: OperatorDecisionRecord,
) -> None:
    if not isinstance(decision_record, OperatorDecisionRecord):
        raise LedgerAuditError(
            "Ledger audit records can only consume OperatorDecisionRecord."
        )


def _require_inbox_item(inbox_item: ApprovalInboxItem) -> None:
    if not isinstance(inbox_item, ApprovalInboxItem):
        raise LedgerAuditError(
            "Ledger audit records require ApprovalInboxItem context."
        )


def _require_evidence_refs(evidence_refs: tuple[str, ...]) -> None:
    if not isinstance(evidence_refs, tuple) or not all(
        isinstance(ref, str) for ref in evidence_refs
    ):
        raise LedgerAuditError("evidence_refs must be a tuple of strings.")
