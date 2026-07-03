from __future__ import annotations

from dataclasses import fields

from github_repo_steward import (
    NormalizedRepoSnapshot,
    RepoFinding,
    RepositoryIdentity,
    analyze_repo_snapshot,
    load_default_fixture_snapshot,
    normalize_repo_snapshot,
)


def test_analyzer_returns_structured_expected_findings() -> None:
    raw = load_default_fixture_snapshot()
    snapshot = normalize_repo_snapshot(raw)

    findings = analyze_repo_snapshot(snapshot)

    assert all(isinstance(finding, RepoFinding) for finding in findings)
    assert [(finding.finding_type, finding.target_type, finding.target_number) for finding in findings] == [
        ("issue_missing_reproduction", "issue", 11),
        ("issue_stale_no_maintainer_response", "issue", 12),
        ("pull_request_failing_ci", "pull_request", 21),
        ("pull_request_waiting_for_review", "pull_request", 22),
    ]


def test_finding_model_contains_observational_fields_only() -> None:
    assert [field.name for field in fields(RepoFinding)] == [
        "finding_id",
        "finding_type",
        "severity",
        "target_type",
        "target_number",
        "title",
        "summary",
        "evidence",
    ]


def test_expected_finding_ids_are_stable() -> None:
    raw = load_default_fixture_snapshot()
    snapshot = normalize_repo_snapshot(raw)

    findings = analyze_repo_snapshot(snapshot)

    assert [finding.finding_id for finding in findings] == [
        "a7:issue_missing_reproduction:issue:11",
        "a7:issue_stale_no_maintainer_response:issue:12",
        "a7:pull_request_failing_ci:pull_request:21",
        "a7:pull_request_waiting_for_review:pull_request:22",
    ]


def test_analyzer_handles_empty_snapshot() -> None:
    snapshot = NormalizedRepoSnapshot(
        repository=RepositoryIdentity(
            owner="fixture-owner",
            name="empty-fixture-repo",
            default_branch="main",
            snapshot_generated_at="2026-06-30T12:00:00Z",
        ),
        labels=(),
        issues=(),
        pull_requests=(),
        comments=(),
        ci_statuses=(),
    )

    assert analyze_repo_snapshot(snapshot) == []
