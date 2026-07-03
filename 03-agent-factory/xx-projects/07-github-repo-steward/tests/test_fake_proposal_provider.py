from __future__ import annotations

from github_repo_steward import (
    FakeProposalProvider,
    RepoFinding,
    analyze_repo_snapshot,
    load_default_fixture_snapshot,
    normalize_repo_snapshot,
)


def test_fake_provider_returns_expected_proposal_drafts() -> None:
    snapshot, findings = _default_snapshot_and_findings()

    proposals = FakeProposalProvider().propose(snapshot, findings)

    assert [proposal.proposal_type for proposal in proposals] == [
        "draft_issue_comment",
        "draft_issue_comment",
        "draft_pull_request_comment",
        "draft_pull_request_comment",
    ]
    assert [proposal.source_finding_id for proposal in proposals] == [
        "a7:issue_missing_reproduction:issue:11",
        "a7:issue_stale_no_maintainer_response:issue:12",
        "a7:pull_request_failing_ci:pull_request:21",
        "a7:pull_request_waiting_for_review:pull_request:22",
    ]


def test_fake_provider_maps_each_required_finding_type() -> None:
    snapshot, findings = _default_snapshot_and_findings()

    proposals = FakeProposalProvider().propose(snapshot, findings)
    mapped_finding_types = {
        finding.finding_type
        for finding in findings
        if any(
            proposal.source_finding_id == finding.finding_id
            for proposal in proposals
        )
    }

    assert mapped_finding_types == {
        "issue_missing_reproduction",
        "issue_stale_no_maintainer_response",
        "pull_request_failing_ci",
        "pull_request_waiting_for_review",
    }


def test_all_fake_proposal_drafts_require_future_approval() -> None:
    snapshot, findings = _default_snapshot_and_findings()

    proposals = FakeProposalProvider().propose(snapshot, findings)

    assert {proposal.requires_approval for proposal in proposals} == {True}
    assert {proposal.execution_status for proposal in proposals} == {"draft_only"}


def test_fake_provider_ignores_unknown_future_finding_type() -> None:
    snapshot, findings = _default_snapshot_and_findings()
    unknown = RepoFinding(
        finding_id="a7:future:repository:0",
        finding_type="future_unmapped_finding",
        severity="info",
        target_type="repository",
        target_number=0,
        title="Future finding",
        summary="Future local observation.",
        evidence=(),
    )

    proposals = FakeProposalProvider().propose(snapshot, [*findings, unknown])

    assert len(proposals) == 4
    assert all(proposal.source_finding_id != unknown.finding_id for proposal in proposals)


def test_fake_provider_returns_empty_list_for_empty_findings() -> None:
    snapshot, _ = _default_snapshot_and_findings()

    assert FakeProposalProvider().propose(snapshot, []) == []


def _default_snapshot_and_findings():
    raw = load_default_fixture_snapshot()
    snapshot = normalize_repo_snapshot(raw)
    findings = analyze_repo_snapshot(snapshot)
    return snapshot, findings
