"""Deterministic local policy guard for non-executing proposal drafts."""

from __future__ import annotations

from github_repo_steward.models import (
    ProposalPolicyEvaluation,
    ProposalPolicyEvaluationError,
    RepoProposal,
)
from github_repo_steward.proposal_provider import (
    ALLOWED_PROPOSAL_TYPES,
    ALLOWED_TARGET_TYPES,
)

ALLOWED_POLICY_RISK_LEVELS = frozenset({"low", "medium"})
SAFE_VERDICT = "allowed_for_operator_review"
BLOCKED_VERDICT = "blocked_by_policy"
MISSING_PROPOSAL_ID_EVALUATION_ID = "a7e:missing-proposal-id"
UNSAFE_COMPLETION_PHRASES = (
    "i posted",
    "i have posted",
    "comment has been posted",
    "label has been applied",
    "issue has been closed",
    "pr has been merged",
    "merged this pull request",
    "closed this issue",
    "applied the label",
)
TOKEN_LIKE_PATTERNS = (
    "ghp_",
    "github_pat_",
    "Bearer ",
    "Authorization:",
    "OPENAI_API_KEY=",
    "ANTHROPIC_API_KEY=",
    "GITHUB_TOKEN=",
)


def evaluate_repo_proposal(proposal: RepoProposal) -> ProposalPolicyEvaluation:
    """Evaluate one local proposal draft for future operator-review safety."""

    _require_repo_proposal(proposal)

    reasons = _policy_block_reasons(proposal)
    verdict = BLOCKED_VERDICT if reasons else SAFE_VERDICT

    return ProposalPolicyEvaluation(
        evaluation_id=_evaluation_id_for(proposal),
        proposal_id=proposal.proposal_id,
        verdict=verdict,
        reasons=tuple(reasons),
        risk_level=proposal.risk_level,
        requires_operator_approval=True,
        safe_for_operator_review=verdict == SAFE_VERDICT,
    )


def evaluate_repo_proposals(
    proposals: list[RepoProposal],
) -> list[ProposalPolicyEvaluation]:
    """Evaluate proposal drafts in deterministic policy order."""

    for proposal in proposals:
        _require_repo_proposal(proposal)

    return [
        evaluate_repo_proposal(proposal)
        for proposal in sorted(proposals, key=_proposal_sort_key)
    ]


def _policy_block_reasons(proposal: RepoProposal) -> list[str]:
    reasons: list[str] = []

    _require_present(proposal.proposal_id, "proposal_id", reasons)
    _require_present(
        proposal.source_finding_id,
        "source_finding_id",
        reasons,
    )
    _require_present(proposal.title, "title", reasons)
    _require_present(proposal.draft_body, "draft_body", reasons)
    _require_present(proposal.rationale, "rationale", reasons)

    if not isinstance(proposal.target_number, int) or proposal.target_number < 1:
        reasons.append("target_number must be present.")
    if proposal.proposal_type not in ALLOWED_PROPOSAL_TYPES:
        reasons.append(f"Unsupported proposal_type: {proposal.proposal_type}")
    if proposal.target_type not in ALLOWED_TARGET_TYPES:
        reasons.append(f"Unsupported target_type: {proposal.target_type}")
    if proposal.risk_level not in ALLOWED_POLICY_RISK_LEVELS:
        reasons.append(f"Unsupported or unsafe risk_level: {proposal.risk_level}")
    if proposal.requires_approval is not True:
        reasons.append("requires_approval must be True.")
    if proposal.execution_status != "draft_only":
        reasons.append("execution_status must be draft_only.")
    if _claims_completed_action(proposal.draft_body):
        reasons.append("draft_body must not claim a completed repository action.")
    if _contains_token_like_text(proposal.draft_body):
        reasons.append("draft_body must not contain token-like or secret text.")

    return reasons


def _evaluation_id_for(proposal: RepoProposal) -> str:
    if not proposal.proposal_id:
        return MISSING_PROPOSAL_ID_EVALUATION_ID
    return f"a7e:{proposal.proposal_id}"


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


def _claims_completed_action(draft_body: str) -> bool:
    lowered = draft_body.lower()
    return any(phrase in lowered for phrase in UNSAFE_COMPLETION_PHRASES)


def _contains_token_like_text(draft_body: str) -> bool:
    return any(pattern in draft_body for pattern in TOKEN_LIKE_PATTERNS)


def _require_present(value: str, field_name: str, reasons: list[str]) -> None:
    if not value:
        reasons.append(f"{field_name} is required.")


def _require_repo_proposal(proposal: RepoProposal) -> None:
    if not isinstance(proposal, RepoProposal):
        raise ProposalPolicyEvaluationError(
            "Policy guard can only evaluate RepoProposal objects."
        )
