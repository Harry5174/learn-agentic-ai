from __future__ import annotations

from dataclasses import fields, replace

import pytest

from github_repo_steward import (
    ApprovalInboxError,
    ApprovalInboxItem,
    FakeProposalProvider,
    ProposalPolicyEvaluation,
    RepoProposal,
    analyze_repo_snapshot,
    build_approval_inbox,
    build_approval_inbox_item,
    evaluate_repo_proposal,
    evaluate_repo_proposals,
    load_default_fixture_snapshot,
    normalize_repo_snapshot,
)


def test_approval_inbox_model_contains_pending_review_fields_only() -> None:
    assert [field.name for field in fields(ApprovalInboxItem)] == [
        "inbox_item_id",
        "proposal_id",
        "evaluation_id",
        "proposal_type",
        "target_type",
        "target_number",
        "title",
        "draft_body",
        "risk_level",
        "status",
        "requires_operator_approval",
        "created_from_policy_verdict",
        "policy_reasons",
    ]


def test_policy_allowed_fake_proposals_enter_approval_inbox() -> None:
    proposals, evaluations = _default_proposals_and_evaluations()

    inbox = build_approval_inbox(proposals, evaluations)

    assert len(inbox) == 4
    assert all(isinstance(item, ApprovalInboxItem) for item in inbox)
    assert {item.status for item in inbox} == {"pending_operator_review"}
    assert {item.requires_operator_approval for item in inbox} == {True}
    assert {item.created_from_policy_verdict for item in inbox} == {
        "allowed_for_operator_review"
    }
    assert all(item.policy_reasons == () for item in inbox)


def test_single_inbox_item_is_built_from_allowed_policy_evaluation() -> None:
    proposals, evaluations = _default_proposals_and_evaluations()
    proposal = proposals[0]
    evaluation = evaluations[0]

    item = build_approval_inbox_item(proposal, evaluation)

    assert item.inbox_item_id == f"a7i:{proposal.proposal_id}:{evaluation.evaluation_id}"
    assert item.proposal_id == proposal.proposal_id
    assert item.evaluation_id == evaluation.evaluation_id
    assert item.title == proposal.title
    assert item.draft_body == proposal.draft_body
    assert item.status == "pending_operator_review"


def test_blocked_proposals_do_not_enter_approval_inbox() -> None:
    proposals, _ = _default_proposals_and_evaluations()
    blocked_proposal = replace(proposals[0], risk_level="high")
    mixed_proposals = [blocked_proposal, *proposals[1:]]
    evaluations = evaluate_repo_proposals(mixed_proposals)

    inbox = build_approval_inbox(mixed_proposals, evaluations)

    assert len(inbox) == 3
    assert blocked_proposal.proposal_id not in {
        item.proposal_id for item in inbox
    }


def test_build_single_item_rejects_blocked_policy_evaluation() -> None:
    proposal = replace(_default_proposals_and_evaluations()[0][0], risk_level="high")
    evaluation = evaluate_repo_proposal(proposal)

    with pytest.raises(ApprovalInboxError, match="allowed_for_operator_review"):
        build_approval_inbox_item(proposal, evaluation)


def test_empty_proposal_and_evaluation_lists_return_empty_inbox() -> None:
    assert build_approval_inbox([], []) == []


def test_missing_matching_evaluation_fails_safely() -> None:
    proposals, evaluations = _default_proposals_and_evaluations()

    with pytest.raises(ApprovalInboxError, match="Missing policy evaluation"):
        build_approval_inbox(proposals, evaluations[1:])


def test_extra_evaluation_fails_safely() -> None:
    proposals, evaluations = _default_proposals_and_evaluations()
    extra_evaluation = replace(
        evaluations[0],
        proposal_id="a7p:extra:issue:999",
        evaluation_id="a7e:a7p:extra:issue:999",
    )

    with pytest.raises(ApprovalInboxError, match="correspond"):
        build_approval_inbox(proposals, [*evaluations, extra_evaluation])


def test_duplicate_evaluation_fails_safely() -> None:
    proposals, evaluations = _default_proposals_and_evaluations()

    with pytest.raises(ApprovalInboxError, match="Duplicate"):
        build_approval_inbox(proposals, [*evaluations, evaluations[0]])


def test_mismatched_proposal_and_evaluation_ids_fail_safely() -> None:
    proposals, evaluations = _default_proposals_and_evaluations()
    mismatched = replace(evaluations[0], proposal_id=proposals[1].proposal_id)

    with pytest.raises(ApprovalInboxError, match="proposal IDs"):
        build_approval_inbox_item(proposals[0], mismatched)


def test_mismatched_evaluation_id_fails_safely() -> None:
    proposals, evaluations = _default_proposals_and_evaluations()
    mismatched = replace(evaluations[0], evaluation_id="a7e:wrong")

    with pytest.raises(ApprovalInboxError, match="evaluation ID"):
        build_approval_inbox_item(proposals[0], mismatched)


def test_mismatched_risk_level_fails_safely() -> None:
    proposals, evaluations = _default_proposals_and_evaluations()
    mismatched = replace(evaluations[0], risk_level="medium")

    with pytest.raises(ApprovalInboxError, match="risk levels"):
        build_approval_inbox_item(proposals[0], mismatched)


def test_inbox_rejects_non_proposal_or_evaluation_input() -> None:
    proposals, evaluations = _default_proposals_and_evaluations()
    proposal = proposals[0]
    evaluation = evaluations[0]

    with pytest.raises(ApprovalInboxError, match="RepoProposal"):
        build_approval_inbox_item("not-a-proposal", evaluation)  # type: ignore[arg-type]
    with pytest.raises(ApprovalInboxError, match="ProposalPolicyEvaluation"):
        build_approval_inbox_item(proposal, "not-an-evaluation")  # type: ignore[arg-type]


def test_inbox_item_invariants_reject_non_pending_states() -> None:
    proposals, evaluations = _default_proposals_and_evaluations()
    proposal = proposals[0]
    evaluation = evaluations[0]
    item = build_approval_inbox_item(proposal, evaluation)

    with pytest.raises(ApprovalInboxError, match="pending_operator_review"):
        replace(item, status="approved")
    with pytest.raises(ApprovalInboxError, match="operator approval"):
        replace(item, requires_operator_approval=False)
    with pytest.raises(ApprovalInboxError, match="allowed policy"):
        replace(item, created_from_policy_verdict="blocked_by_policy")
    with pytest.raises(ApprovalInboxError, match="policy reasons"):
        replace(item, policy_reasons=("blocked",))


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
