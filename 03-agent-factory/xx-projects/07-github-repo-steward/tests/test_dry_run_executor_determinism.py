from __future__ import annotations

from copy import deepcopy

from github_repo_steward import (
    ApprovalInboxItem,
    FakeProposalProvider,
    LedgerAuditRecord,
    OperatorDecisionRecord,
    ProposalPolicyEvaluation,
    RepoProposal,
    analyze_repo_snapshot,
    build_approval_inbox,
    dry_run_ledger_records,
    evaluate_repo_proposals,
    load_default_fixture_snapshot,
    normalize_repo_snapshot,
    record_decisions_to_ledger,
    record_operator_decisions,
)


def test_dry_run_ids_are_deterministic() -> None:
    inbox = _default_inbox()
    ledger_records = _default_ledger_records(inbox)

    dry_runs = dry_run_ledger_records(ledger_records, inbox)

    assert [dry_run.dry_run_id for dry_run in dry_runs] == [
        f"a7x:{ledger_records[0].ledger_record_id}:{ledger_records[0].proposal_id}",
        f"a7x:{ledger_records[1].ledger_record_id}:{ledger_records[1].proposal_id}",
    ]


def test_dry_run_order_is_stable_for_reordered_inputs() -> None:
    inbox = _default_inbox()
    ledger_records = _default_ledger_records(inbox)

    dry_runs = dry_run_ledger_records(ledger_records, inbox)
    reordered = dry_run_ledger_records(
        list(reversed(ledger_records)),
        list(reversed(inbox)),
    )

    assert reordered == dry_runs
    assert [record.inbox_item_id for record in dry_runs] == [
        inbox[0].inbox_item_id,
        inbox[1].inbox_item_id,
    ]


def test_dry_run_handler_does_not_mutate_ledger_records() -> None:
    inbox = _default_inbox()
    ledger_records = _default_ledger_records(inbox)
    before = deepcopy(ledger_records)

    dry_run_ledger_records(ledger_records, inbox)

    assert ledger_records == before


def test_dry_run_handler_does_not_mutate_inbox_items() -> None:
    inbox = _default_inbox()
    ledger_records = _default_ledger_records(inbox)
    before = deepcopy(inbox)

    dry_run_ledger_records(ledger_records, inbox)

    assert inbox == before


def _default_ledger_records(
    inbox: list[ApprovalInboxItem],
) -> list[LedgerAuditRecord]:
    decisions = _default_decisions(inbox)
    return record_decisions_to_ledger(decisions, inbox)


def _default_decisions(
    inbox: list[ApprovalInboxItem],
) -> list[OperatorDecisionRecord]:
    return record_operator_decisions(
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
