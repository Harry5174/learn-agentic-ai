from __future__ import annotations

from dataclasses import fields, replace

import pytest

from github_repo_steward import (
    FakeProposalProvider,
    ProposalPolicyEvaluation,
    ProposalPolicyEvaluationError,
    RepoProposal,
    analyze_repo_snapshot,
    evaluate_repo_proposal,
    evaluate_repo_proposals,
    load_default_fixture_snapshot,
    normalize_repo_snapshot,
)


def test_policy_evaluation_model_contains_review_gate_fields_only() -> None:
    assert [field.name for field in fields(ProposalPolicyEvaluation)] == [
        "evaluation_id",
        "proposal_id",
        "verdict",
        "reasons",
        "risk_level",
        "requires_operator_approval",
        "safe_for_operator_review",
    ]


def test_safe_fake_proposals_are_allowed_for_operator_review() -> None:
    proposals = _generate_default_proposals()

    evaluations = evaluate_repo_proposals(proposals)

    assert len(evaluations) == 4
    assert {item.verdict for item in evaluations} == {
        "allowed_for_operator_review"
    }
    assert {item.safe_for_operator_review for item in evaluations} == {True}
    assert {item.requires_operator_approval for item in evaluations} == {True}
    assert all(item.reasons == () for item in evaluations)


def test_single_safe_proposal_has_stable_evaluation_id() -> None:
    proposal = _generate_default_proposals()[0]

    evaluation = evaluate_repo_proposal(proposal)

    assert evaluation.evaluation_id == f"a7e:{proposal.proposal_id}"
    assert evaluation.proposal_id == proposal.proposal_id


@pytest.mark.parametrize(
    ("field_name", "field_value", "reason_text"),
    [
        ("requires_approval", False, "requires_approval"),
        ("execution_status", "posted", "execution_status"),
        ("risk_level", "high", "risk_level"),
        ("proposal_type", "close_issue", "proposal_type"),
        ("target_type", "repository", "target_type"),
        ("draft_body", "", "draft_body"),
        (
            "draft_body",
            "I posted a comment on the issue.",
            "completed repository action",
        ),
        (
            "draft_body",
            "Use GITHUB_TOKEN=example for this draft.",
            "token-like or secret text",
        ),
    ],
)
def test_unsafe_proposals_are_blocked_with_reasons(
    field_name: str,
    field_value: object,
    reason_text: str,
) -> None:
    proposal = _generate_default_proposals()[0]
    unsafe = replace(proposal, **{field_name: field_value})

    evaluation = evaluate_repo_proposal(unsafe)

    assert evaluation.verdict == "blocked_by_policy"
    assert evaluation.safe_for_operator_review is False
    assert evaluation.requires_operator_approval is True
    assert evaluation.reasons
    assert any(reason_text in reason for reason in evaluation.reasons)


@pytest.mark.parametrize(
    "draft_body",
    [
        "Authorization: Bearer example",
        "Bearer example",
        "ghp_example",
        "github_pat_example",
        "OPENAI_API_KEY=example",
        "ANTHROPIC_API_KEY=example",
    ],
)
def test_token_like_draft_body_strings_are_blocked(draft_body: str) -> None:
    proposal = replace(_generate_default_proposals()[0], draft_body=draft_body)

    evaluation = evaluate_repo_proposal(proposal)

    assert evaluation.verdict == "blocked_by_policy"
    assert any("token-like or secret text" in reason for reason in evaluation.reasons)


def test_missing_proposal_id_uses_stable_missing_id_evaluation_id() -> None:
    proposal = replace(_generate_default_proposals()[0], proposal_id="")

    evaluation = evaluate_repo_proposal(proposal)

    assert evaluation.evaluation_id == "a7e:missing-proposal-id"
    assert evaluation.proposal_id == ""
    assert evaluation.verdict == "blocked_by_policy"
    assert any("proposal_id" in reason for reason in evaluation.reasons)


def test_empty_proposal_list_returns_empty_evaluation_list() -> None:
    assert evaluate_repo_proposals([]) == []


def test_policy_guard_rejects_non_proposal_input() -> None:
    with pytest.raises(ProposalPolicyEvaluationError, match="RepoProposal"):
        evaluate_repo_proposal("not-a-proposal")  # type: ignore[arg-type]


def _generate_default_proposals() -> list[RepoProposal]:
    raw = load_default_fixture_snapshot()
    snapshot = normalize_repo_snapshot(raw)
    findings = analyze_repo_snapshot(snapshot)
    return FakeProposalProvider().propose(snapshot, findings)
