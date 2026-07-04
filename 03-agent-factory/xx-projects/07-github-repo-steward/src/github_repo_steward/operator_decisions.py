"""Deterministic local operator decision records for pending inbox items."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from github_repo_steward.approval_inbox import PENDING_OPERATOR_REVIEW
from github_repo_steward.models import (
    ApprovalInboxItem,
    OperatorDecisionError,
    OperatorDecisionRecord,
)

APPROVED_BY_OPERATOR = "approved_by_operator"
REJECTED_BY_OPERATOR = "rejected_by_operator"
LOCAL_DECISION_RECORDED = "local_decision_recorded"
NOT_EXECUTED = "not_executed"
NOT_RECORDED = "not_recorded"


def record_operator_decision(
    inbox_item: ApprovalInboxItem,
    decision: str,
    decided_by: str,
    rationale: str = "",
) -> OperatorDecisionRecord:
    """Record one local operator decision without execution or ledger writes."""

    _require_pending_inbox_item(inbox_item)
    _require_decision(decision)
    decided_by = decided_by.strip()
    rationale = rationale.strip()

    return OperatorDecisionRecord(
        decision_id=f"a7d:{inbox_item.inbox_item_id}:{decision}",
        inbox_item_id=inbox_item.inbox_item_id,
        proposal_id=inbox_item.proposal_id,
        decision=decision,
        decided_by=decided_by,
        rationale=rationale,
        status=LOCAL_DECISION_RECORDED,
        execution_status=NOT_EXECUTED,
        ledger_status=NOT_RECORDED,
    )


def record_operator_decisions(
    inbox_items: list[ApprovalInboxItem],
    decisions: list[dict[str, str]],
) -> list[OperatorDecisionRecord]:
    """Record local operator decisions in deterministic inbox-item order."""

    if not inbox_items and not decisions:
        return []
    for inbox_item in inbox_items:
        _require_pending_inbox_item(inbox_item)

    inbox_by_id = _inbox_items_by_id(inbox_items)
    decision_by_inbox_id = _decisions_by_inbox_item_id(decisions)

    unknown_ids = set(decision_by_inbox_id).difference(inbox_by_id)
    if unknown_ids:
        raise OperatorDecisionError(
            "Operator decisions must reference supplied approval inbox items."
        )

    records: list[OperatorDecisionRecord] = []
    for inbox_item in sorted(inbox_items, key=_inbox_sort_key):
        decision_input = decision_by_inbox_id.get(inbox_item.inbox_item_id)
        if decision_input is None:
            continue
        records.append(
            record_operator_decision(
                inbox_item,
                decision=decision_input["decision"],
                decided_by=decision_input["decided_by"],
                rationale=decision_input.get("rationale", ""),
            )
        )

    return records


def _inbox_items_by_id(
    inbox_items: list[ApprovalInboxItem],
) -> dict[str, ApprovalInboxItem]:
    by_id: dict[str, ApprovalInboxItem] = {}
    for inbox_item in inbox_items:
        if inbox_item.inbox_item_id in by_id:
            raise OperatorDecisionError(
                f"Duplicate inbox item: {inbox_item.inbox_item_id}"
            )
        by_id[inbox_item.inbox_item_id] = inbox_item
    return by_id


def _decisions_by_inbox_item_id(
    decisions: list[dict[str, str]],
) -> dict[str, dict[str, str]]:
    by_id: dict[str, dict[str, str]] = {}
    for decision_input in decisions:
        _require_decision_input_mapping(decision_input)
        inbox_item_id = _require_decision_field(decision_input, "inbox_item_id")
        _require_decision(_require_decision_field(decision_input, "decision"))
        _require_decision_field(decision_input, "decided_by")
        if inbox_item_id in by_id:
            raise OperatorDecisionError(
                f"Duplicate operator decision for inbox item: {inbox_item_id}"
            )
        by_id[inbox_item_id] = dict(decision_input)
    return by_id


def _inbox_sort_key(inbox_item: ApprovalInboxItem) -> tuple[str, int, str, str]:
    target_number = (
        inbox_item.target_number
        if isinstance(inbox_item.target_number, int)
        else 0
    )
    return (
        inbox_item.target_type,
        target_number,
        inbox_item.proposal_type,
        inbox_item.inbox_item_id,
    )


def _require_pending_inbox_item(inbox_item: ApprovalInboxItem) -> None:
    if not isinstance(inbox_item, ApprovalInboxItem):
        raise OperatorDecisionError(
            "Operator decisions can only consume ApprovalInboxItem objects."
        )
    if inbox_item.status != PENDING_OPERATOR_REVIEW:
        raise OperatorDecisionError(
            "Operator decisions require pending_operator_review inbox items."
        )
    if inbox_item.requires_operator_approval is not True:
        raise OperatorDecisionError(
            "Operator decisions require items that need operator approval."
        )


def _require_decision(decision: str) -> None:
    if decision not in {APPROVED_BY_OPERATOR, REJECTED_BY_OPERATOR}:
        raise OperatorDecisionError(
            f"Unsupported operator decision: {decision}"
        )


def _require_decision_input_mapping(decision_input: object) -> None:
    if not isinstance(decision_input, Mapping):
        raise OperatorDecisionError(
            "Operator decision batch entries must be mappings."
        )


def _require_decision_field(
    decision_input: Mapping[str, Any],
    field_name: str,
) -> str:
    value = decision_input.get(field_name)
    if not isinstance(value, str) or not value.strip():
        raise OperatorDecisionError(f"{field_name} is required.")
    return value.strip()
