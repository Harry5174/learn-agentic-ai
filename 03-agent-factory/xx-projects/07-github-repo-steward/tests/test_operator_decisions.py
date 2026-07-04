from __future__ import annotations

from dataclasses import fields, replace

import pytest

from github_repo_steward import (
    ApprovalInboxItem,
    FakeProposalProvider,
    OperatorDecisionError,
    OperatorDecisionRecord,
    ProposalPolicyEvaluation,
    RepoProposal,
    analyze_repo_snapshot,
    build_approval_inbox,
    evaluate_repo_proposals,
    load_default_fixture_snapshot,
    normalize_repo_snapshot,
    record_operator_decision,
    record_operator_decisions,
)


def test_operator_decision_model_contains_local_record_fields_only() -> None:
    assert [field.name for field in fields(OperatorDecisionRecord)] == [
        "decision_id",
        "inbox_item_id",
        "proposal_id",
        "decision",
        "decided_by",
        "rationale",
        "status",
        "execution_status",
        "ledger_status",
    ]
    assert "executed_at" not in {field.name for field in fields(OperatorDecisionRecord)}
    assert "github_response" not in {
        field.name for field in fields(OperatorDecisionRecord)
    }
    assert "ledger_entry_id" not in {
        field.name for field in fields(OperatorDecisionRecord)
    }


def test_operator_can_approve_pending_inbox_item_locally() -> None:
    inbox = _default_inbox()

    decision = record_operator_decision(
        inbox[0],
        decision="approved_by_operator",
        decided_by="local-operator",
        rationale="Approved for local decision-record test only.",
    )

    assert decision == OperatorDecisionRecord(
        decision_id=f"a7d:{inbox[0].inbox_item_id}:approved_by_operator",
        inbox_item_id=inbox[0].inbox_item_id,
        proposal_id=inbox[0].proposal_id,
        decision="approved_by_operator",
        decided_by="local-operator",
        rationale="Approved for local decision-record test only.",
        status="local_decision_recorded",
        execution_status="not_executed",
        ledger_status="not_recorded",
    )


def test_operator_can_reject_pending_inbox_item_locally() -> None:
    inbox = _default_inbox()

    decision = record_operator_decision(
        inbox[0],
        decision="rejected_by_operator",
        decided_by="local-operator",
        rationale="Needs maintainer review before any future action.",
    )

    assert decision.decision == "rejected_by_operator"
    assert decision.status == "local_decision_recorded"
    assert decision.execution_status == "not_executed"
    assert decision.ledger_status == "not_recorded"
    assert decision.rationale == "Needs maintainer review before any future action."


def test_rejected_decision_without_rationale_fails_safely() -> None:
    inbox = _default_inbox()

    with pytest.raises(OperatorDecisionError, match="rationale"):
        record_operator_decision(
            inbox[0],
            decision="rejected_by_operator",
            decided_by="local-operator",
        )


def test_invalid_decision_value_fails_safely() -> None:
    inbox = _default_inbox()

    with pytest.raises(OperatorDecisionError, match="Unsupported"):
        record_operator_decision(
            inbox[0],
            decision="execute_now",
            decided_by="local-operator",
        )


def test_missing_decided_by_fails_safely() -> None:
    inbox = _default_inbox()

    with pytest.raises(OperatorDecisionError, match="decided_by"):
        record_operator_decision(
            inbox[0],
            decision="approved_by_operator",
            decided_by=" ",
        )


def test_duplicate_decisions_for_same_inbox_item_fail_safely() -> None:
    inbox = _default_inbox()
    decision_input = {
        "inbox_item_id": inbox[0].inbox_item_id,
        "decision": "approved_by_operator",
        "decided_by": "local-operator",
        "rationale": "Approved locally.",
    }

    with pytest.raises(OperatorDecisionError, match="Duplicate"):
        record_operator_decisions(inbox, [decision_input, decision_input])


def test_decision_for_unknown_inbox_item_fails_safely() -> None:
    inbox = _default_inbox()

    with pytest.raises(OperatorDecisionError, match="supplied approval inbox"):
        record_operator_decisions(
            inbox,
            [
                {
                    "inbox_item_id": "a7i:unknown",
                    "decision": "approved_by_operator",
                    "decided_by": "local-operator",
                    "rationale": "Approved locally.",
                }
            ],
        )


def test_empty_inbox_and_decision_lists_return_empty_decision_list() -> None:
    assert record_operator_decisions([], []) == []


def test_decision_record_invariants_reject_execution_or_ledger_claims() -> None:
    decision = record_operator_decision(
        _default_inbox()[0],
        decision="approved_by_operator",
        decided_by="local-operator",
    )

    with pytest.raises(OperatorDecisionError, match="local_decision_recorded"):
        replace(decision, status="executed")
    with pytest.raises(OperatorDecisionError, match="executed"):
        replace(decision, execution_status="executed")
    with pytest.raises(OperatorDecisionError, match="ledger"):
        replace(decision, ledger_status="recorded")


def test_operator_decision_rejects_non_inbox_input() -> None:
    with pytest.raises(OperatorDecisionError, match="ApprovalInboxItem"):
        record_operator_decision(  # type: ignore[arg-type]
            "not-an-inbox-item",
            decision="approved_by_operator",
            decided_by="local-operator",
        )


def test_operator_decision_rejects_non_pending_inbox_items() -> None:
    inbox_item = _unchecked_inbox_item_with_status(
        _default_inbox()[0],
        "already_decided",
    )

    with pytest.raises(OperatorDecisionError, match="pending_operator_review"):
        record_operator_decision(
            inbox_item,
            decision="approved_by_operator",
            decided_by="local-operator",
        )


def _unchecked_inbox_item_with_status(
    inbox_item: ApprovalInboxItem,
    status: str,
) -> ApprovalInboxItem:
    unchecked = object.__new__(ApprovalInboxItem)
    for field in fields(ApprovalInboxItem):
        value = status if field.name == "status" else getattr(inbox_item, field.name)
        object.__setattr__(unchecked, field.name, value)
    return unchecked


def _default_inbox() -> list[ApprovalInboxItem]:
    proposals, evaluations = _default_proposals_and_evaluations()
    return build_approval_inbox(proposals, evaluations)


def _default_proposals_and_evaluations() -> tuple[
    list[RepoProposal],
    list[ProposalPolicyEvaluation],
]:
    raw = load_default_fixture_snapshot()
    snapshot = normalize_repo_snapshot(raw)
    findings = analyze_repo_snapshot(snapshot)
    proposals = FakeProposalProvider().propose(snapshot, findings)
    evaluations = evaluate_repo_proposals(proposals)
    return proposals, evaluations
