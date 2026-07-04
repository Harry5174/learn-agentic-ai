from __future__ import annotations

from copy import deepcopy

from github_repo_steward import (
    ApprovalInboxItem,
    FakeProposalProvider,
    OperatorDecisionRecord,
    ProposalPolicyEvaluation,
    RepoProposal,
    analyze_repo_snapshot,
    build_approval_inbox,
    evaluate_repo_proposals,
    load_default_fixture_snapshot,
    normalize_repo_snapshot,
    record_decisions_to_ledger,
    record_operator_decisions,
)


def test_ledger_record_ids_are_deterministic() -> None:
    inbox = _default_inbox()
    decisions = _default_decisions(inbox)

    ledger_records = record_decisions_to_ledger(decisions, inbox)

    assert [record.ledger_record_id for record in ledger_records] == [
        (
            "a7l:a7d:a7i:a7p:draft_issue_comment:issue:11:"
            "a7:issue_missing_reproduction:issue:11:"
            "a7e:a7p:draft_issue_comment:issue:11:"
            "a7:issue_missing_reproduction:issue:11:approved_by_operator:"
            "a7i:a7p:draft_issue_comment:issue:11:"
            "a7:issue_missing_reproduction:issue:11:"
            "a7e:a7p:draft_issue_comment:issue:11:"
            "a7:issue_missing_reproduction:issue:11"
        ),
        (
            "a7l:a7d:a7i:a7p:draft_issue_comment:issue:12:"
            "a7:issue_stale_no_maintainer_response:issue:12:"
            "a7e:a7p:draft_issue_comment:issue:12:"
            "a7:issue_stale_no_maintainer_response:issue:12:"
            "rejected_by_operator:"
            "a7i:a7p:draft_issue_comment:issue:12:"
            "a7:issue_stale_no_maintainer_response:issue:12:"
            "a7e:a7p:draft_issue_comment:issue:12:"
            "a7:issue_stale_no_maintainer_response:issue:12"
        ),
    ]


def test_ledger_record_order_is_stable_for_reordered_inputs() -> None:
    inbox = _default_inbox()
    decisions = _default_decisions(inbox)

    ledger_records = record_decisions_to_ledger(decisions, inbox)
    reordered = record_decisions_to_ledger(
        list(reversed(decisions)),
        list(reversed(inbox)),
    )

    assert reordered == ledger_records
    assert [record.inbox_item_id for record in ledger_records] == [
        inbox[0].inbox_item_id,
        inbox[1].inbox_item_id,
    ]


def test_ledger_handler_does_not_mutate_decision_records() -> None:
    inbox = _default_inbox()
    decisions = _default_decisions(inbox)
    before = deepcopy(decisions)

    record_decisions_to_ledger(decisions, inbox)

    assert decisions == before


def test_ledger_handler_does_not_mutate_inbox_items() -> None:
    inbox = _default_inbox()
    decisions = _default_decisions(inbox)
    before = deepcopy(inbox)

    record_decisions_to_ledger(decisions, inbox)

    assert inbox == before


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
    rationale: str = "Approved for local ledger-record test only.",
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
