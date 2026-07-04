from __future__ import annotations

from copy import deepcopy
from dataclasses import fields, replace
from pathlib import Path

import pytest

from github_repo_steward import (
    FakeProposalProvider,
    GitHubReadAdapterError,
    GitHubReadAdapterResult,
    RawRepoSnapshot,
    adapt_github_api_payloads,
    analyze_repo_snapshot,
    build_approval_inbox,
    dry_run_ledger_record,
    evaluate_repo_proposals,
    load_github_api_fixture_payloads,
    map_github_api_payloads_to_canonical_snapshot,
    normalize_repo_snapshot,
    record_decision_to_ledger,
    record_operator_decision,
)


def test_github_read_adapter_result_model_contains_local_fields_only() -> None:
    assert [field.name for field in fields(GitHubReadAdapterResult)] == [
        "source",
        "repository_full_name",
        "canonical_snapshot",
        "raw_endpoint_names",
        "warnings",
        "adapter_status",
        "github_status",
        "network_status",
    ]
    forbidden_fields = {field.name for field in fields(GitHubReadAdapterResult)}
    assert "github_request_id" not in forbidden_fields
    assert "rate_limit_remaining" not in forbidden_fields
    assert "etag_from_live_response" not in forbidden_fields
    assert "authenticated_user" not in forbidden_fields
    assert "installation_id" not in forbidden_fields
    assert "github_app_id" not in forbidden_fields
    assert "oauth_token_status" not in forbidden_fields


def test_default_raw_github_like_fixture_payloads_load_successfully() -> None:
    payloads = load_github_api_fixture_payloads()

    assert sorted(payloads) == [
        "check_runs",
        "issue_comments",
        "issues",
        "labels",
        "pull_reviews",
        "pulls",
        "repository",
        "statuses",
    ]
    assert payloads["repository"]["full_name"] == "fixture-owner/fixture-repo"  # type: ignore[index]
    assert len(payloads["issues"]) == 3  # type: ignore[arg-type]
    assert len(payloads["pulls"]) == 2  # type: ignore[arg-type]


def test_adapter_maps_raw_payloads_into_canonical_snapshot_dictionary() -> None:
    canonical = _default_canonical_snapshot()

    assert sorted(canonical) == [
        "ci_statuses",
        "comments",
        "issues",
        "labels",
        "pull_requests",
        "repository",
    ]
    assert canonical["repository"] == {
        "owner": "fixture-owner",
        "name": "fixture-repo",
        "default_branch": "main",
        "snapshot_generated_at": "2026-07-01T12:00:00Z",
    }
    assert [label["name"] for label in canonical["labels"]] == [
        "bug",
        "enhancement",
        "needs-info",
        "stale",
    ]


def test_adapter_separates_issue_like_pull_markers_from_canonical_issues() -> None:
    canonical = _default_canonical_snapshot()

    assert [issue["number"] for issue in canonical["issues"]] == [11, 12]
    assert [pull["number"] for pull in canonical["pull_requests"]] == [21, 22]
    assert 21 not in {issue["number"] for issue in canonical["issues"]}
    assert canonical["pull_requests"][0]["title"] == "Add archive importer validation"


def test_adapter_maps_comments_reviews_and_statuses_deterministically() -> None:
    canonical = _default_canonical_snapshot()

    assert canonical["comments"] == [
        {
            "id": 3001,
            "target_type": "issue",
            "target_number": 11,
            "author": "maintainer-fixture",
            "body": "Please add exact reproduction steps and the archive shape.",
            "created_at": "2026-06-08T10:30:00Z",
        },
        {
            "id": 4001,
            "target_type": "pull_request",
            "target_number": 21,
            "author": "reviewer-fixture",
            "body": "The validation approach is approved, pending the failing check.",
            "created_at": "2026-06-27T12:00:00Z",
        },
    ]
    assert canonical["ci_statuses"] == [
        {
            "target_type": "pull_request",
            "target_number": 21,
            "status": "completed",
            "conclusion": "failure",
            "updated_at": "2026-06-28T12:10:00Z",
        },
        {
            "target_type": "pull_request",
            "target_number": 22,
            "status": "completed",
            "conclusion": "success",
            "updated_at": "2026-06-25T16:05:00Z",
        },
    ]


def test_adapter_result_invariants_reject_live_github_or_network_claims() -> None:
    result = adapt_github_api_payloads(load_github_api_fixture_payloads())

    assert result.source == "local_github_like_fixture"
    assert result.repository_full_name == "fixture-owner/fixture-repo"
    assert result.adapter_status == "mapped_locally"
    assert result.github_status == "not_called"
    assert result.network_status == "not_used"

    with pytest.raises(GitHubReadAdapterError, match="mapped_locally"):
        replace(result, adapter_status="read_live")
    with pytest.raises(GitHubReadAdapterError, match="GitHub"):
        replace(result, github_status="called")
    with pytest.raises(GitHubReadAdapterError, match="network"):
        replace(result, network_status="used")


def test_mapped_snapshot_runs_through_full_local_pipeline() -> None:
    canonical = _default_canonical_snapshot()
    raw = RawRepoSnapshot(
        data=canonical,
        source_path=Path("local-github-like-fixture"),
    )

    snapshot = normalize_repo_snapshot(raw)
    findings = analyze_repo_snapshot(snapshot)
    proposals = FakeProposalProvider().propose(snapshot, findings)
    evaluations = evaluate_repo_proposals(proposals)
    inbox = build_approval_inbox(proposals, evaluations)
    decision = record_operator_decision(
        inbox[0],
        decision="approved_by_operator",
        decided_by="local-operator",
        rationale="Approved for adapter contract test only.",
    )
    ledger_record = record_decision_to_ledger(
        decision,
        inbox[0],
        evidence_refs=("artifact-7.9-adapter-test",),
        source_snapshot_id=snapshot.repository.name,
    )
    dry_run = dry_run_ledger_record(ledger_record, inbox[0])

    assert snapshot.repository.name == "fixture-repo"
    assert len(snapshot.issues) == 2
    assert len(snapshot.pull_requests) == 2
    assert findings
    assert proposals
    assert inbox
    assert dry_run.github_status == "not_called"
    assert dry_run.execution_status == "not_executed"


def test_missing_repository_payload_fails_safely() -> None:
    payloads = load_github_api_fixture_payloads()
    del payloads["repository"]

    with pytest.raises(GitHubReadAdapterError, match="repository"):
        map_github_api_payloads_to_canonical_snapshot(payloads)


def test_malformed_issue_payload_fails_safely() -> None:
    payloads = load_github_api_fixture_payloads()
    malformed = deepcopy(payloads)
    del malformed["issues"][0]["number"]  # type: ignore[index]

    with pytest.raises(GitHubReadAdapterError, match="issues\\[0\\].number"):
        map_github_api_payloads_to_canonical_snapshot(malformed)


def test_malformed_pull_request_payload_fails_safely() -> None:
    payloads = load_github_api_fixture_payloads()
    malformed = deepcopy(payloads)
    del malformed["pulls"][0]["head"]  # type: ignore[index]

    with pytest.raises(GitHubReadAdapterError, match="head"):
        map_github_api_payloads_to_canonical_snapshot(malformed)


def test_missing_pull_payload_family_fails_safely() -> None:
    payloads = load_github_api_fixture_payloads()
    del payloads["pulls"]

    with pytest.raises(GitHubReadAdapterError, match="pulls"):
        map_github_api_payloads_to_canonical_snapshot(payloads)


def _default_canonical_snapshot() -> dict[str, object]:
    return map_github_api_payloads_to_canonical_snapshot(
        load_github_api_fixture_payloads()
    )
