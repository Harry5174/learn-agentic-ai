from __future__ import annotations

from copy import deepcopy
from dataclasses import replace

from github_repo_steward import (
    FakeProposalProvider,
    RepoProposal,
    analyze_repo_snapshot,
    evaluate_repo_proposals,
    load_default_fixture_snapshot,
    normalize_repo_snapshot,
)


def test_policy_evaluation_ids_are_deterministic() -> None:
    proposals = _generate_default_proposals()

    evaluations = evaluate_repo_proposals(proposals)

    assert [evaluation.evaluation_id for evaluation in evaluations] == [
        (
            "a7e:a7p:draft_issue_comment:issue:11:"
            "a7:issue_missing_reproduction:issue:11"
        ),
        (
            "a7e:a7p:draft_issue_comment:issue:12:"
            "a7:issue_stale_no_maintainer_response:issue:12"
        ),
        (
            "a7e:a7p:draft_pull_request_comment:pull_request:21:"
            "a7:pull_request_failing_ci:pull_request:21"
        ),
        (
            "a7e:a7p:draft_pull_request_comment:pull_request:22:"
            "a7:pull_request_waiting_for_review:pull_request:22"
        ),
    ]


def test_policy_evaluation_order_is_stable_for_reordered_proposals() -> None:
    proposals = _generate_default_proposals()

    evaluations = evaluate_repo_proposals(proposals)
    reordered = evaluate_repo_proposals(list(reversed(proposals)))

    assert reordered == evaluations


def test_policy_guard_does_not_mutate_proposals() -> None:
    proposals = _generate_default_proposals()
    before = deepcopy(proposals)

    evaluate_repo_proposals(proposals)

    assert proposals == before


def test_blocked_policy_evaluation_order_is_stable() -> None:
    proposals = _generate_default_proposals()
    blocked = [
        replace(proposals[2], risk_level="high"),
        replace(proposals[0], requires_approval=False),
    ]

    evaluations = evaluate_repo_proposals(blocked)

    assert [evaluation.proposal_id for evaluation in evaluations] == [
        proposals[0].proposal_id,
        proposals[2].proposal_id,
    ]
    assert {evaluation.verdict for evaluation in evaluations} == {
        "blocked_by_policy"
    }


def _generate_default_proposals() -> list[RepoProposal]:
    raw = load_default_fixture_snapshot()
    snapshot = normalize_repo_snapshot(raw)
    findings = analyze_repo_snapshot(snapshot)
    return FakeProposalProvider().propose(snapshot, findings)
