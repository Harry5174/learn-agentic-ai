from __future__ import annotations

from copy import deepcopy
from dataclasses import replace

from github_repo_steward import (
    FakeProposalProvider,
    ProposalPolicyEvaluation,
    RepoProposal,
    analyze_repo_snapshot,
    build_approval_inbox,
    evaluate_repo_proposals,
    load_default_fixture_snapshot,
    normalize_repo_snapshot,
)


def test_approval_inbox_item_ids_are_deterministic() -> None:
    proposals, evaluations = _default_proposals_and_evaluations()

    inbox = build_approval_inbox(proposals, evaluations)

    assert [item.inbox_item_id for item in inbox] == [
        (
            "a7i:a7p:draft_issue_comment:issue:11:"
            "a7:issue_missing_reproduction:issue:11:"
            "a7e:a7p:draft_issue_comment:issue:11:"
            "a7:issue_missing_reproduction:issue:11"
        ),
        (
            "a7i:a7p:draft_issue_comment:issue:12:"
            "a7:issue_stale_no_maintainer_response:issue:12:"
            "a7e:a7p:draft_issue_comment:issue:12:"
            "a7:issue_stale_no_maintainer_response:issue:12"
        ),
        (
            "a7i:a7p:draft_pull_request_comment:pull_request:21:"
            "a7:pull_request_failing_ci:pull_request:21:"
            "a7e:a7p:draft_pull_request_comment:pull_request:21:"
            "a7:pull_request_failing_ci:pull_request:21"
        ),
        (
            "a7i:a7p:draft_pull_request_comment:pull_request:22:"
            "a7:pull_request_waiting_for_review:pull_request:22:"
            "a7e:a7p:draft_pull_request_comment:pull_request:22:"
            "a7:pull_request_waiting_for_review:pull_request:22"
        ),
    ]


def test_approval_inbox_order_is_stable_for_reordered_inputs() -> None:
    proposals, evaluations = _default_proposals_and_evaluations()

    inbox = build_approval_inbox(proposals, evaluations)
    reordered = build_approval_inbox(
        list(reversed(proposals)),
        list(reversed(evaluations)),
    )

    assert reordered == inbox


def test_approval_inbox_does_not_mutate_proposals_or_evaluations() -> None:
    proposals, evaluations = _default_proposals_and_evaluations()
    proposals_before = deepcopy(proposals)
    evaluations_before = deepcopy(evaluations)

    build_approval_inbox(proposals, evaluations)

    assert proposals == proposals_before
    assert evaluations == evaluations_before


def test_blocked_exclusion_order_is_stable() -> None:
    proposals, _ = _default_proposals_and_evaluations()
    mixed_proposals = [
        replace(proposals[2], risk_level="high"),
        proposals[1],
        proposals[0],
    ]
    evaluations = evaluate_repo_proposals(mixed_proposals)

    inbox = build_approval_inbox(mixed_proposals, evaluations)

    assert [item.proposal_id for item in inbox] == [
        proposals[0].proposal_id,
        proposals[1].proposal_id,
    ]


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
