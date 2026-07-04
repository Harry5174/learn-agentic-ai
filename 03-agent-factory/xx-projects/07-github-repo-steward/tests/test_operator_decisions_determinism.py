from __future__ import annotations

from copy import deepcopy

from github_repo_steward import (
    ApprovalInboxItem,
    FakeProposalProvider,
    ProposalPolicyEvaluation,
    RepoProposal,
    analyze_repo_snapshot,
    build_approval_inbox,
    evaluate_repo_proposals,
    load_default_fixture_snapshot,
    normalize_repo_snapshot,
    record_operator_decisions,
)


def test_operator_decision_ids_are_deterministic() -> None:
    inbox = _default_inbox()

    decisions = record_operator_decisions(
        inbox,
        [
            _decision_input(inbox[0], "approved_by_operator"),
            _decision_input(inbox[1], "rejected_by_operator", "Not enough context."),
        ],
    )

    assert [decision.decision_id for decision in decisions] == [
        (
            "a7d:a7i:a7p:draft_issue_comment:issue:11:"
            "a7:issue_missing_reproduction:issue:11:"
            "a7e:a7p:draft_issue_comment:issue:11:"
            "a7:issue_missing_reproduction:issue:11:approved_by_operator"
        ),
        (
            "a7d:a7i:a7p:draft_issue_comment:issue:12:"
            "a7:issue_stale_no_maintainer_response:issue:12:"
            "a7e:a7p:draft_issue_comment:issue:12:"
            "a7:issue_stale_no_maintainer_response:issue:12:"
            "rejected_by_operator"
        ),
    ]


def test_operator_decision_order_is_stable_for_reordered_inputs() -> None:
    inbox = _default_inbox()
    decision_inputs = [
        _decision_input(inbox[2], "approved_by_operator"),
        _decision_input(inbox[0], "approved_by_operator"),
        _decision_input(inbox[1], "rejected_by_operator", "Not enough context."),
    ]

    decisions = record_operator_decisions(inbox, decision_inputs)
    reordered = record_operator_decisions(
        list(reversed(inbox)),
        list(reversed(decision_inputs)),
    )

    assert reordered == decisions
    assert [decision.inbox_item_id for decision in decisions] == [
        inbox[0].inbox_item_id,
        inbox[1].inbox_item_id,
        inbox[2].inbox_item_id,
    ]


def test_operator_decision_handler_does_not_mutate_inbox_items() -> None:
    inbox = _default_inbox()
    before = deepcopy(inbox)

    record_operator_decisions(
        inbox,
        [
            _decision_input(inbox[0], "approved_by_operator"),
            _decision_input(inbox[1], "rejected_by_operator", "Not enough context."),
        ],
    )

    assert inbox == before


def _decision_input(
    inbox_item: ApprovalInboxItem,
    decision: str,
    rationale: str = "Approved for local decision-record test only.",
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
