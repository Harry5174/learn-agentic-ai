"""Provider-neutral boundary for non-executing fake proposal drafts."""

from __future__ import annotations

from typing import Protocol

from github_repo_steward.models import (
    NormalizedRepoSnapshot,
    RepoFinding,
    RepoProposal,
    RepoProposalValidationError,
)

ALLOWED_PROPOSAL_TYPES = frozenset(
    {
        "draft_issue_comment",
        "draft_pull_request_comment",
        "suggest_label",
        "suggest_priority",
        "suggest_follow_up_question",
        "suggest_maintainer_next_step",
    }
)
ALLOWED_TARGET_TYPES = frozenset({"issue", "pull_request"})
ALLOWED_RISK_LEVELS = frozenset({"low", "medium", "high"})
ALLOWED_EXECUTION_STATUSES = frozenset({"draft_only"})
DRAFT_COMMENT_TYPES = frozenset(
    {"draft_issue_comment", "draft_pull_request_comment"}
)


class ProposalProvider(Protocol):
    """Boundary for providers that turn findings into proposal drafts."""

    def propose(
        self,
        snapshot: NormalizedRepoSnapshot,
        findings: list[RepoFinding],
    ) -> list[RepoProposal]:
        """Return non-executing proposal objects for local review."""


def validate_repo_proposal(proposal: RepoProposal) -> None:
    """Validate local proposal-shape invariants without policy decisions."""

    _require_present(proposal.proposal_id, "proposal_id")
    _require_present(proposal.source_finding_id, "source_finding_id")
    _require_present(proposal.title, "title")
    _require_present(proposal.rationale, "rationale")

    if proposal.proposal_type not in ALLOWED_PROPOSAL_TYPES:
        raise RepoProposalValidationError(
            f"Unsupported proposal_type: {proposal.proposal_type}"
        )
    if proposal.target_type not in ALLOWED_TARGET_TYPES:
        raise RepoProposalValidationError(
            f"Unsupported target_type: {proposal.target_type}"
        )
    if proposal.risk_level not in ALLOWED_RISK_LEVELS:
        raise RepoProposalValidationError(
            f"Unsupported risk_level: {proposal.risk_level}"
        )
    if proposal.requires_approval is not True:
        raise RepoProposalValidationError("requires_approval must be True.")
    if proposal.execution_status not in ALLOWED_EXECUTION_STATUSES:
        raise RepoProposalValidationError(
            "execution_status must be draft_only."
        )
    if proposal.proposal_type in DRAFT_COMMENT_TYPES:
        _require_present(proposal.draft_body, "draft_body")


def _require_present(value: str, field_name: str) -> None:
    if not value:
        raise RepoProposalValidationError(f"{field_name} is required.")
