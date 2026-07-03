from __future__ import annotations

from copy import deepcopy
from dataclasses import replace

from github_repo_steward import (
    FakeProposalProvider,
    analyze_repo_snapshot,
    load_default_fixture_snapshot,
    normalize_repo_snapshot,
)


def test_fake_proposal_ids_are_deterministic() -> None:
    snapshot, findings = _default_snapshot_and_findings()

    proposals = FakeProposalProvider().propose(snapshot, findings)

    assert [proposal.proposal_id for proposal in proposals] == [
        (
            "a7p:draft_issue_comment:issue:11:"
            "a7:issue_missing_reproduction:issue:11"
        ),
        (
            "a7p:draft_issue_comment:issue:12:"
            "a7:issue_stale_no_maintainer_response:issue:12"
        ),
        (
            "a7p:draft_pull_request_comment:pull_request:21:"
            "a7:pull_request_failing_ci:pull_request:21"
        ),
        (
            "a7p:draft_pull_request_comment:pull_request:22:"
            "a7:pull_request_waiting_for_review:pull_request:22"
        ),
    ]


def test_fake_proposal_order_is_stable_for_reordered_findings() -> None:
    snapshot, findings = _default_snapshot_and_findings()

    proposals = FakeProposalProvider().propose(snapshot, findings)
    reordered = FakeProposalProvider().propose(snapshot, list(reversed(findings)))

    assert reordered == proposals


def test_fake_provider_does_not_mutate_snapshot_or_findings() -> None:
    snapshot, findings = _default_snapshot_and_findings()
    snapshot_before = deepcopy(snapshot)
    findings_before = deepcopy(findings)

    FakeProposalProvider().propose(snapshot, findings)

    assert snapshot == snapshot_before
    assert findings == findings_before


def test_fake_provider_output_is_stable_for_reordered_snapshot_records() -> None:
    snapshot, findings = _default_snapshot_and_findings()
    reordered_snapshot = replace(
        snapshot,
        issues=tuple(reversed(snapshot.issues)),
        pull_requests=tuple(reversed(snapshot.pull_requests)),
        comments=tuple(reversed(snapshot.comments)),
        ci_statuses=tuple(reversed(snapshot.ci_statuses)),
    )

    assert FakeProposalProvider().propose(
        reordered_snapshot, findings
    ) == FakeProposalProvider().propose(snapshot, findings)


def _default_snapshot_and_findings():
    raw = load_default_fixture_snapshot()
    snapshot = normalize_repo_snapshot(raw)
    findings = analyze_repo_snapshot(snapshot)
    return snapshot, findings
