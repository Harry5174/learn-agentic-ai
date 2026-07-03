from __future__ import annotations

from dataclasses import fields, replace

import pytest

from github_repo_steward import (
    FakeProposalProvider,
    RepoProposal,
    RepoProposalValidationError,
    analyze_repo_snapshot,
    load_default_fixture_snapshot,
    normalize_repo_snapshot,
    validate_repo_proposal,
)


def test_proposal_model_contains_draft_fields_only() -> None:
    assert [field.name for field in fields(RepoProposal)] == [
        "proposal_id",
        "source_finding_id",
        "proposal_type",
        "target_type",
        "target_number",
        "title",
        "draft_body",
        "rationale",
        "risk_level",
        "requires_approval",
        "execution_status",
    ]
    assert "executed_at" not in {field.name for field in fields(RepoProposal)}
    assert "github_response" not in {field.name for field in fields(RepoProposal)}
    assert "external_url" not in {field.name for field in fields(RepoProposal)}


def test_valid_fake_proposal_drafts_pass_validation() -> None:
    proposals = _generate_default_proposals()

    for proposal in proposals:
        validate_repo_proposal(proposal)


def test_proposal_rejects_missing_future_approval_requirement() -> None:
    proposal = _generate_default_proposals()[0]
    invalid = replace(proposal, requires_approval=False)

    with pytest.raises(RepoProposalValidationError, match="requires_approval"):
        validate_repo_proposal(invalid)


def test_proposal_rejects_unsupported_execution_status() -> None:
    proposal = _generate_default_proposals()[0]
    invalid = replace(proposal, execution_status="posted")

    with pytest.raises(RepoProposalValidationError, match="execution_status"):
        validate_repo_proposal(invalid)


def _generate_default_proposals() -> list[RepoProposal]:
    raw = load_default_fixture_snapshot()
    snapshot = normalize_repo_snapshot(raw)
    findings = analyze_repo_snapshot(snapshot)
    return FakeProposalProvider().propose(snapshot, findings)
