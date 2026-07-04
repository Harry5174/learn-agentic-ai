from __future__ import annotations

from dataclasses import fields, replace

import pytest

from github_repo_steward import (
    ApprovalInboxItem,
    DryRunExecutionError,
    DryRunExecutionResult,
    FakeProposalProvider,
    LedgerAuditRecord,
    ProposalPolicyEvaluation,
    RepoProposal,
    analyze_repo_snapshot,
    build_approval_inbox,
    dry_run_ledger_record,
    dry_run_ledger_records,
    evaluate_repo_proposals,
    load_default_fixture_snapshot,
    normalize_repo_snapshot,
    record_decisions_to_ledger,
    record_operator_decisions,
)


def test_dry_run_model_contains_local_result_fields_only() -> None:
    assert [field.name for field in fields(DryRunExecutionResult)] == [
        "dry_run_id",
        "ledger_record_id",
        "decision_id",
        "inbox_item_id",
        "proposal_id",
        "proposal_type",
        "target_type",
        "target_number",
        "decision",
        "planned_action",
        "dry_run_status",
        "execution_status",
        "github_status",
        "external_side_effect_status",
        "ledger_record_status",
        "evidence_refs",
        "summary",
    ]
    forbidden_fields = {field.name for field in fields(DryRunExecutionResult)}
    assert "executed_at" not in forbidden_fields
    assert "github_response" not in forbidden_fields
    assert "external_url" not in forbidden_fields
    assert "github_comment_id" not in forbidden_fields
    assert "applied_label" not in forbidden_fields
    assert "closed_issue" not in forbidden_fields
    assert "merged_pr" not in forbidden_fields
    assert "executor_run_id" not in forbidden_fields
    assert "real_github_request_id" not in forbidden_fields


def test_approved_ledger_record_can_be_dry_run_locally() -> None:
    inbox = _default_inbox()
    ledger_records = _default_ledger_records(inbox)

    dry_run = dry_run_ledger_record(ledger_records[0], inbox[0])

    assert dry_run == DryRunExecutionResult(
        dry_run_id=(
            f"a7x:{ledger_records[0].ledger_record_id}:"
            f"{ledger_records[0].proposal_id}"
        ),
        ledger_record_id=ledger_records[0].ledger_record_id,
        decision_id=ledger_records[0].decision_id,
        inbox_item_id=ledger_records[0].inbox_item_id,
        proposal_id=ledger_records[0].proposal_id,
        proposal_type=inbox[0].proposal_type,
        target_type=inbox[0].target_type,
        target_number=inbox[0].target_number,
        decision="approved_by_operator",
        planned_action="would_prepare_issue_comment",
        dry_run_status="dry_run_completed",
        execution_status="not_executed",
        github_status="not_called",
        external_side_effect_status="none",
        ledger_record_status="verified_local_audit_record",
        evidence_refs=("artifact-7.8-unit-test-approved",),
        summary=(
            "dry_run_completed: would_prepare_issue_comment for issue #11; "
            "not_executed; github_not_called; no_external_side_effect"
        ),
    )


def test_rejected_ledger_record_can_be_dry_run_as_no_op() -> None:
    inbox = _default_inbox()
    ledger_records = _default_ledger_records(inbox)

    dry_run = dry_run_ledger_record(ledger_records[1], inbox[1])

    assert dry_run.decision == "rejected_by_operator"
    assert dry_run.dry_run_status == "dry_run_skipped"
    assert dry_run.planned_action == "no_op_rejected_by_operator"
    assert dry_run.execution_status == "not_executed"
    assert dry_run.github_status == "not_called"
    assert dry_run.external_side_effect_status == "none"
    assert dry_run.ledger_record_status == "verified_local_audit_record"
    assert dry_run.evidence_refs == ("artifact-7.8-unit-test-rejected",)


def test_dry_run_preserves_upstream_ids_and_target_metadata() -> None:
    inbox = _default_inbox()
    ledger_record = _default_ledger_records(inbox)[0]

    dry_run = dry_run_ledger_record(ledger_record, inbox[0])

    assert dry_run.ledger_record_id == ledger_record.ledger_record_id
    assert dry_run.decision_id == ledger_record.decision_id
    assert dry_run.inbox_item_id == ledger_record.inbox_item_id
    assert dry_run.proposal_id == ledger_record.proposal_id
    assert dry_run.proposal_type == inbox[0].proposal_type
    assert dry_run.target_type == inbox[0].target_type
    assert dry_run.target_number == inbox[0].target_number


def test_dry_run_result_invariants_reject_execution_or_external_claims() -> None:
    dry_run = _default_dry_runs()[0]

    with pytest.raises(DryRunExecutionError, match="dry-run status"):
        replace(dry_run, dry_run_status="executed")
    with pytest.raises(DryRunExecutionError, match="execution"):
        replace(dry_run, execution_status="executed")
    with pytest.raises(DryRunExecutionError, match="GitHub"):
        replace(dry_run, github_status="called")
    with pytest.raises(DryRunExecutionError, match="external side effects"):
        replace(dry_run, external_side_effect_status="posted_comment")
    with pytest.raises(DryRunExecutionError, match="verified local audit"):
        replace(dry_run, ledger_record_status="unverified")


def test_mismatched_ledger_and_inbox_data_fails_safely() -> None:
    inbox = _default_inbox()
    ledger_record = _default_ledger_records(inbox)[0]

    with pytest.raises(DryRunExecutionError, match="IDs must match"):
        dry_run_ledger_record(ledger_record, inbox[1])


def test_mismatched_ledger_and_inbox_proposal_id_fails_safely() -> None:
    inbox = _default_inbox()
    ledger_record = replace(
        _default_ledger_records(inbox)[0],
        proposal_id="different-proposal",
    )

    with pytest.raises(DryRunExecutionError, match="proposal IDs"):
        dry_run_ledger_record(ledger_record, inbox[0])


def test_duplicate_dry_run_records_for_same_ledger_record_fail_safely() -> None:
    inbox = _default_inbox()
    ledger_record = _default_ledger_records(inbox)[0]

    with pytest.raises(DryRunExecutionError, match="Duplicate ledger record"):
        dry_run_ledger_records([ledger_record, ledger_record], inbox)


def test_duplicate_inbox_items_fail_safely() -> None:
    inbox = _default_inbox()
    ledger_record = _default_ledger_records(inbox)[0]

    with pytest.raises(DryRunExecutionError, match="Duplicate inbox item"):
        dry_run_ledger_records([ledger_record], [inbox[0], inbox[0]])


def test_unknown_ledger_inbox_item_fails_safely() -> None:
    inbox = _default_inbox()
    ledger_record = _default_ledger_records(inbox)[0]

    with pytest.raises(DryRunExecutionError, match="supplied inbox"):
        dry_run_ledger_records([ledger_record], [])


def test_empty_ledger_and_inbox_lists_return_empty_dry_run_list() -> None:
    assert dry_run_ledger_records([], []) == []


def test_batch_dry_runs_supplied_ledger_records_not_every_inbox_item() -> None:
    inbox = _default_inbox()
    ledger_record = _default_ledger_records(inbox)[0]

    dry_runs = dry_run_ledger_records([ledger_record], inbox)

    assert len(dry_runs) == 1
    assert dry_runs[0].ledger_record_id == ledger_record.ledger_record_id


def test_dry_run_rejects_non_ledger_input() -> None:
    with pytest.raises(DryRunExecutionError, match="LedgerAuditRecord"):
        dry_run_ledger_record(  # type: ignore[arg-type]
            "not-a-ledger-record",
            _default_inbox()[0],
        )


def test_dry_run_rejects_non_inbox_input() -> None:
    ledger_record = _default_ledger_records(_default_inbox())[0]

    with pytest.raises(DryRunExecutionError, match="ApprovalInboxItem"):
        dry_run_ledger_record(  # type: ignore[arg-type]
            ledger_record,
            "not-an-inbox-item",
        )


def _default_dry_runs() -> list[DryRunExecutionResult]:
    inbox = _default_inbox()
    return dry_run_ledger_records(_default_ledger_records(inbox), inbox)


def _default_ledger_records(
    inbox: list[ApprovalInboxItem],
) -> list[LedgerAuditRecord]:
    decisions = record_operator_decisions(
        inbox,
        [
            _decision_input(inbox[0], "approved_by_operator"),
            _decision_input(
                inbox[1],
                "rejected_by_operator",
                "Not enough context.",
            ),
        ],
    )
    return record_decisions_to_ledger(
        decisions,
        inbox,
        evidence_refs_by_decision_id={
            decisions[0].decision_id: ("artifact-7.8-unit-test-approved",),
            decisions[1].decision_id: ("artifact-7.8-unit-test-rejected",),
        },
        source_snapshot_id="fake-repo",
    )


def _decision_input(
    inbox_item: ApprovalInboxItem,
    decision: str,
    rationale: str = "Approved for local dry-run test only.",
) -> dict[str, str]:
    return {
        "inbox_item_id": inbox_item.inbox_item_id,
        "decision": decision,
        "decided_by": "local-operator",
        "rationale": rationale,
    }


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
