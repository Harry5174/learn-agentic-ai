from __future__ import annotations

from dataclasses import fields, replace

import pytest

from github_repo_steward import (
    ApprovalInboxItem,
    FakeProposalProvider,
    LedgerAuditError,
    LedgerAuditRecord,
    OperatorDecisionRecord,
    ProposalPolicyEvaluation,
    RepoProposal,
    analyze_repo_snapshot,
    build_approval_inbox,
    evaluate_repo_proposals,
    load_default_fixture_snapshot,
    normalize_repo_snapshot,
    record_decision_to_ledger,
    record_decisions_to_ledger,
    record_operator_decision,
)


def test_ledger_audit_model_contains_local_record_fields_only() -> None:
    assert [field.name for field in fields(LedgerAuditRecord)] == [
        "ledger_record_id",
        "decision_id",
        "inbox_item_id",
        "proposal_id",
        "decision",
        "decided_by",
        "decision_rationale",
        "record_type",
        "record_status",
        "execution_status",
        "github_status",
        "executor_status",
        "source_snapshot_id",
        "evidence_refs",
    ]
    forbidden_fields = {field.name for field in fields(LedgerAuditRecord)}
    assert "executed_at" not in forbidden_fields
    assert "github_response" not in forbidden_fields
    assert "external_url" not in forbidden_fields
    assert "github_comment_id" not in forbidden_fields
    assert "executor_run_id" not in forbidden_fields
    assert "real_github_request_id" not in forbidden_fields


def test_approved_operator_decision_can_be_ledgered_locally() -> None:
    inbox = _default_inbox()
    decision = record_operator_decision(
        inbox[0],
        decision="approved_by_operator",
        decided_by="local-operator",
        rationale="Approved for local ledger-record test only.",
    )

    ledger_record = record_decision_to_ledger(
        decision,
        inbox[0],
        evidence_refs=("artifact-7.7-unit-test",),
        source_snapshot_id="fake-repo",
    )

    assert ledger_record == LedgerAuditRecord(
        ledger_record_id=f"a7l:{decision.decision_id}:{inbox[0].inbox_item_id}",
        decision_id=decision.decision_id,
        inbox_item_id=inbox[0].inbox_item_id,
        proposal_id=inbox[0].proposal_id,
        decision="approved_by_operator",
        decided_by="local-operator",
        decision_rationale="Approved for local ledger-record test only.",
        record_type="operator_decision_audit",
        record_status="recorded_locally",
        execution_status="not_executed",
        github_status="not_called",
        executor_status="not_triggered",
        source_snapshot_id="fake-repo",
        evidence_refs=("artifact-7.7-unit-test",),
    )


def test_rejected_operator_decision_can_be_ledgered_locally() -> None:
    inbox = _default_inbox()
    decision = record_operator_decision(
        inbox[0],
        decision="rejected_by_operator",
        decided_by="local-operator",
        rationale="Needs maintainer review before any future action.",
    )

    ledger_record = record_decision_to_ledger(decision, inbox[0])

    assert ledger_record.decision == "rejected_by_operator"
    assert ledger_record.decision_id == decision.decision_id
    assert ledger_record.proposal_id == decision.proposal_id
    assert ledger_record.inbox_item_id == decision.inbox_item_id
    assert ledger_record.decided_by == decision.decided_by
    assert ledger_record.decision_rationale == decision.rationale
    assert ledger_record.execution_status == "not_executed"
    assert ledger_record.github_status == "not_called"
    assert ledger_record.executor_status == "not_triggered"


def test_ledger_record_invariants_reject_execution_or_external_claims() -> None:
    ledger_record = _default_ledger_records()[0]

    with pytest.raises(LedgerAuditError, match="operator_decision_audit"):
        replace(ledger_record, record_type="github_comment")
    with pytest.raises(LedgerAuditError, match="recorded_locally"):
        replace(ledger_record, record_status="persisted")
    with pytest.raises(LedgerAuditError, match="execution"):
        replace(ledger_record, execution_status="executed")
    with pytest.raises(LedgerAuditError, match="GitHub"):
        replace(ledger_record, github_status="called")
    with pytest.raises(LedgerAuditError, match="executor"):
        replace(ledger_record, executor_status="triggered")


def test_mismatched_decision_and_inbox_data_fails_safely() -> None:
    inbox = _default_inbox()
    decision = record_operator_decision(
        inbox[0],
        decision="approved_by_operator",
        decided_by="local-operator",
    )

    with pytest.raises(LedgerAuditError, match="IDs must match"):
        record_decision_to_ledger(decision, inbox[1])


def test_mismatched_decision_and_inbox_proposal_id_fails_safely() -> None:
    inbox = _default_inbox()
    decision = _unchecked_decision_with_proposal_id(
        record_operator_decision(
            inbox[0],
            decision="approved_by_operator",
            decided_by="local-operator",
        ),
        "different-proposal",
    )

    with pytest.raises(LedgerAuditError, match="proposal IDs"):
        record_decision_to_ledger(decision, inbox[0])


def test_duplicate_ledger_records_for_same_decision_fail_safely() -> None:
    inbox = _default_inbox()
    decision = record_operator_decision(
        inbox[0],
        decision="approved_by_operator",
        decided_by="local-operator",
    )

    with pytest.raises(LedgerAuditError, match="Duplicate operator decision"):
        record_decisions_to_ledger([decision, decision], inbox)


def test_duplicate_inbox_items_fail_safely() -> None:
    inbox = _default_inbox()
    decision = record_operator_decision(
        inbox[0],
        decision="approved_by_operator",
        decided_by="local-operator",
    )

    with pytest.raises(LedgerAuditError, match="Duplicate inbox item"):
        record_decisions_to_ledger([decision], [inbox[0], inbox[0]])


def test_unknown_decision_inbox_item_fails_safely() -> None:
    inbox = _default_inbox()
    decision = record_operator_decision(
        inbox[0],
        decision="approved_by_operator",
        decided_by="local-operator",
    )

    with pytest.raises(LedgerAuditError, match="supplied approval inbox"):
        record_decisions_to_ledger([decision], [])


def test_extra_evidence_refs_fail_safely() -> None:
    with pytest.raises(LedgerAuditError, match="Evidence refs"):
        record_decisions_to_ledger(
            [],
            _default_inbox(),
            evidence_refs_by_decision_id={"unknown-decision": ("evidence",)},
        )


def test_empty_decision_and_inbox_lists_return_empty_ledger_list() -> None:
    assert record_decisions_to_ledger([], []) == []


def test_batch_records_supplied_decisions_not_every_inbox_item() -> None:
    inbox = _default_inbox()
    decision = record_operator_decision(
        inbox[0],
        decision="approved_by_operator",
        decided_by="local-operator",
    )

    ledger_records = record_decisions_to_ledger([decision], inbox)

    assert len(ledger_records) == 1
    assert ledger_records[0].decision_id == decision.decision_id


def _unchecked_decision_with_proposal_id(
    decision: OperatorDecisionRecord,
    proposal_id: str,
) -> OperatorDecisionRecord:
    unchecked = object.__new__(OperatorDecisionRecord)
    for field in fields(OperatorDecisionRecord):
        value = proposal_id if field.name == "proposal_id" else getattr(
            decision,
            field.name,
        )
        object.__setattr__(unchecked, field.name, value)
    return unchecked


def _default_ledger_records() -> list[LedgerAuditRecord]:
    inbox = _default_inbox()
    decisions = [
        record_operator_decision(
            inbox[0],
            decision="approved_by_operator",
            decided_by="local-operator",
        )
    ]
    return record_decisions_to_ledger(decisions, inbox)


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
