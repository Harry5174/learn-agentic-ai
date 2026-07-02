from __future__ import annotations

from copy import deepcopy

import pytest

from github_repo_steward import (
    RawRepoSnapshot,
    RepoSnapshotValidationError,
    load_default_fixture_snapshot,
    normalize_repo_snapshot,
)


def test_normalized_snapshot_includes_expected_records() -> None:
    raw = load_default_fixture_snapshot()

    snapshot = normalize_repo_snapshot(raw)

    assert snapshot.repository.owner == "fixture-owner"
    assert snapshot.repository.name == "fixture-repo"
    assert snapshot.repository.default_branch == "main"
    assert snapshot.repository.snapshot_generated_at == "2026-06-30T12:00:00Z"

    assert [label.name for label in snapshot.labels] == [
        "bug",
        "needs-info",
        "stale",
        "enhancement",
    ]
    assert len(snapshot.issues) == 3
    assert len(snapshot.pull_requests) == 2
    assert len(snapshot.comments) == 3
    assert len(snapshot.ci_statuses) == 2


def test_issues_are_normalized_with_deterministic_stale_days() -> None:
    raw = load_default_fixture_snapshot()

    snapshot = normalize_repo_snapshot(raw)
    issue = next(item for item in snapshot.issues if item.number == 12)

    assert issue.labels == ("enhancement", "stale")
    assert issue.stale_days == 51
    assert issue.comments_count == 0


def test_pull_requests_include_review_and_ci_statuses() -> None:
    raw = load_default_fixture_snapshot()

    snapshot = normalize_repo_snapshot(raw)
    failing_pr = next(item for item in snapshot.pull_requests if item.number == 21)
    review_pr = next(item for item in snapshot.pull_requests if item.number == 22)

    assert failing_pr.ci_status == "failing"
    assert failing_pr.review_status == "approved"
    assert review_pr.ci_status == "passing"
    assert review_pr.review_status == "waiting_for_review"


def test_comments_and_ci_statuses_are_normalized() -> None:
    raw = load_default_fixture_snapshot()

    snapshot = normalize_repo_snapshot(raw)
    pr_comment = next(
        item for item in snapshot.comments if item.target_type == "pull_request"
    )
    pr_status = next(item for item in snapshot.ci_statuses if item.target_number == 21)

    assert pr_comment.target_number == 21
    assert pr_status.status == "completed"
    assert pr_status.conclusion == "failure"


def test_missing_required_issue_field_fails_safely() -> None:
    raw = load_default_fixture_snapshot()
    data = deepcopy(raw.data)
    del data["issues"][0]["title"]

    malformed = RawRepoSnapshot(data=data, source_path=raw.source_path)

    with pytest.raises(RepoSnapshotValidationError, match="issues\\[0\\].*title"):
        normalize_repo_snapshot(malformed)


def test_missing_required_pull_request_field_fails_safely() -> None:
    raw = load_default_fixture_snapshot()
    data = deepcopy(raw.data)
    del data["pull_requests"][0]["base_branch"]

    malformed = RawRepoSnapshot(data=data, source_path=raw.source_path)

    with pytest.raises(
        RepoSnapshotValidationError, match="pull_requests\\[0\\].*base_branch"
    ):
        normalize_repo_snapshot(malformed)


def test_non_string_labels_fail_safely() -> None:
    raw = load_default_fixture_snapshot()
    data = deepcopy(raw.data)
    data["issues"][0]["labels"] = ["bug", {"name": "needs-info"}]

    malformed = RawRepoSnapshot(data=data, source_path=raw.source_path)

    with pytest.raises(RepoSnapshotValidationError, match="labels\\[1\\]"):
        normalize_repo_snapshot(malformed)
