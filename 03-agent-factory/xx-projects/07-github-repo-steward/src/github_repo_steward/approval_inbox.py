"""Deterministic local approval inbox intake for proposal drafts."""

from __future__ import annotations

from github_repo_steward.models import (
    ApprovalInboxError,
    ApprovalInboxItem,
    ProposalPolicyEvaluation,
    RepoProposal,
)
from github_repo_steward.policy_guard import SAFE_VERDICT

PENDING_OPERATOR_REVIEW = "pending_operator_review"


def build_approval_inbox_item(
    proposal: RepoProposal,
    evaluation: ProposalPolicyEvaluation,
) -> ApprovalInboxItem:
    """Create one pending local approval inbox item from an allowed proposal."""

    _require_repo_proposal(proposal)
    _require_policy_evaluation(evaluation)
    _require_matching_pair(proposal, evaluation)
    _require_allowed_evaluation(evaluation)

    return ApprovalInboxItem(
        inbox_item_id=f"a7i:{proposal.proposal_id}:{evaluation.evaluation_id}",
        proposal_id=proposal.proposal_id,
        evaluation_id=evaluation.evaluation_id,
        proposal_type=proposal.proposal_type,
        target_type=proposal.target_type,
        target_number=proposal.target_number,
        title=proposal.title,
        draft_body=proposal.draft_body,
        risk_level=proposal.risk_level,
        status=PENDING_OPERATOR_REVIEW,
        requires_operator_approval=True,
        created_from_policy_verdict=evaluation.verdict,
        policy_reasons=tuple(evaluation.reasons),
    )


def build_approval_inbox(
    proposals: list[RepoProposal],
    evaluations: list[ProposalPolicyEvaluation],
) -> list[ApprovalInboxItem]:
    """Build deterministic pending inbox items for policy-allowed proposals."""

    if not proposals and not evaluations:
        return []
    for proposal in proposals:
        _require_repo_proposal(proposal)
    for evaluation in evaluations:
        _require_policy_evaluation(evaluation)

    evaluations_by_proposal_id = _evaluations_by_proposal_id(evaluations)
    proposal_ids = {proposal.proposal_id for proposal in proposals}
    extra_evaluation_ids = set(evaluations_by_proposal_id) - proposal_ids
    if extra_evaluation_ids:
        raise ApprovalInboxError(
            "Policy evaluations must correspond to supplied proposals."
        )

    inbox_items: list[ApprovalInboxItem] = []
    for proposal in sorted(proposals, key=_proposal_sort_key):
        evaluation = evaluations_by_proposal_id.get(proposal.proposal_id)
        if evaluation is None:
            raise ApprovalInboxError(
                f"Missing policy evaluation for proposal: {proposal.proposal_id}"
            )
        _require_matching_pair(proposal, evaluation)
        if evaluation.verdict != SAFE_VERDICT:
            continue
        inbox_items.append(build_approval_inbox_item(proposal, evaluation))

    return inbox_items


def _evaluations_by_proposal_id(
    evaluations: list[ProposalPolicyEvaluation],
) -> dict[str, ProposalPolicyEvaluation]:
    by_proposal_id: dict[str, ProposalPolicyEvaluation] = {}
    for evaluation in evaluations:
        if evaluation.proposal_id in by_proposal_id:
            raise ApprovalInboxError(
                "Duplicate policy evaluation for proposal: "
                f"{evaluation.proposal_id}"
            )
        by_proposal_id[evaluation.proposal_id] = evaluation
    return by_proposal_id


def _require_matching_pair(
    proposal: RepoProposal,
    evaluation: ProposalPolicyEvaluation,
) -> None:
    if proposal.proposal_id != evaluation.proposal_id:
        raise ApprovalInboxError(
            "Proposal and policy evaluation proposal IDs must match."
        )
    expected_evaluation_id = f"a7e:{proposal.proposal_id}"
    if evaluation.evaluation_id != expected_evaluation_id:
        raise ApprovalInboxError(
            "Policy evaluation ID must match the proposal ID."
        )
    if evaluation.risk_level != proposal.risk_level:
        raise ApprovalInboxError(
            "Proposal and policy evaluation risk levels must match."
        )


def _require_allowed_evaluation(evaluation: ProposalPolicyEvaluation) -> None:
    if evaluation.verdict != SAFE_VERDICT:
        raise ApprovalInboxError(
            "Only allowed_for_operator_review evaluations enter the inbox."
        )
    if evaluation.safe_for_operator_review is not True:
        raise ApprovalInboxError(
            "Allowed evaluations must be safe for operator review."
        )
    if evaluation.requires_operator_approval is not True:
        raise ApprovalInboxError(
            "Inbox items require future operator approval."
        )
    if evaluation.reasons:
        raise ApprovalInboxError(
            "Allowed evaluations must not include policy block reasons."
        )


def _proposal_sort_key(proposal: RepoProposal) -> tuple[str, int, str, str]:
    target_number = (
        proposal.target_number
        if isinstance(proposal.target_number, int)
        else 0
    )
    return (
        proposal.target_type,
        target_number,
        proposal.proposal_type,
        proposal.proposal_id,
    )


def _require_repo_proposal(proposal: RepoProposal) -> None:
    if not isinstance(proposal, RepoProposal):
        raise ApprovalInboxError(
            "Approval inbox can only intake RepoProposal objects."
        )


def _require_policy_evaluation(evaluation: ProposalPolicyEvaluation) -> None:
    if not isinstance(evaluation, ProposalPolicyEvaluation):
        raise ApprovalInboxError(
            "Approval inbox can only intake ProposalPolicyEvaluation objects."
        )
