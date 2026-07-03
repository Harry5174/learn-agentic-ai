"""Deterministic fake provider for non-executing repository proposal drafts."""

from __future__ import annotations

from collections.abc import Callable

from github_repo_steward.models import (
    NormalizedRepoSnapshot,
    RepoFinding,
    RepoProposal,
)
from github_repo_steward.proposal_provider import validate_repo_proposal

ProposalBuilder = Callable[[RepoFinding], RepoProposal]


class FakeProposalProvider:
    """Create deterministic fake proposal drafts from analyzer findings."""

    def propose(
        self,
        snapshot: NormalizedRepoSnapshot,
        findings: list[RepoFinding],
    ) -> list[RepoProposal]:
        """Return draft-only proposal objects for supported findings."""

        del snapshot

        proposals = []
        for finding in findings:
            builder = PROPOSAL_BUILDERS.get(finding.finding_type)
            if builder is None:
                continue
            proposal = builder(finding)
            validate_repo_proposal(proposal)
            proposals.append(proposal)

        return sorted(
            proposals,
            key=lambda proposal: (
                proposal.target_type,
                proposal.target_number,
                proposal.proposal_type,
                proposal.source_finding_id,
            ),
        )


def _issue_missing_reproduction(finding: RepoFinding) -> RepoProposal:
    return _proposal(
        finding=finding,
        proposal_type="draft_issue_comment",
        title="Draft request for reproduction details",
        draft_body=(
            "This issue appears to be missing reproduction details. A "
            "maintainer may ask the reporter to provide steps to reproduce, "
            "expected behavior, and actual behavior."
        ),
        rationale=(
            "The source finding indicates an open issue labeled needs-info."
        ),
        risk_level="low",
    )


def _issue_stale_no_maintainer_response(finding: RepoFinding) -> RepoProposal:
    return _proposal(
        finding=finding,
        proposal_type="draft_issue_comment",
        title="Draft maintainer follow-up for stale issue",
        draft_body=(
            "This issue appears stale with no recorded maintainer response in "
            "the local fixture. A maintainer may review whether a follow-up "
            "question or status update is useful."
        ),
        rationale=(
            "The source finding indicates a stale open issue with no comments."
        ),
        risk_level="low",
    )


def _pull_request_failing_ci(finding: RepoFinding) -> RepoProposal:
    return _proposal(
        finding=finding,
        proposal_type="draft_pull_request_comment",
        title="Draft review note for failing CI",
        draft_body=(
            "This pull request appears to have failing CI in the local "
            "snapshot. A maintainer may ask the contributor to inspect the "
            "failing check before further review."
        ),
        rationale=(
            "The source finding indicates an open pull request with failing CI."
        ),
        risk_level="medium",
    )


def _pull_request_waiting_for_review(finding: RepoFinding) -> RepoProposal:
    return _proposal(
        finding=finding,
        proposal_type="draft_pull_request_comment",
        title="Draft review availability note",
        draft_body=(
            "This pull request appears to be waiting for review in the local "
            "snapshot. A maintainer may review the change or identify a "
            "reviewer."
        ),
        rationale=(
            "The source finding indicates an open pull request waiting for "
            "review."
        ),
        risk_level="low",
    )


def _proposal(
    *,
    finding: RepoFinding,
    proposal_type: str,
    title: str,
    draft_body: str,
    rationale: str,
    risk_level: str,
) -> RepoProposal:
    return RepoProposal(
        proposal_id=(
            f"a7p:{proposal_type}:{finding.target_type}:"
            f"{finding.target_number}:{finding.finding_id}"
        ),
        source_finding_id=finding.finding_id,
        proposal_type=proposal_type,
        target_type=finding.target_type,
        target_number=finding.target_number,
        title=title,
        draft_body=draft_body,
        rationale=rationale,
        risk_level=risk_level,
        requires_approval=True,
        execution_status="draft_only",
    )


PROPOSAL_BUILDERS: dict[str, ProposalBuilder] = {
    "issue_missing_reproduction": _issue_missing_reproduction,
    "issue_stale_no_maintainer_response": _issue_stale_no_maintainer_response,
    "pull_request_failing_ci": _pull_request_failing_ci,
    "pull_request_waiting_for_review": _pull_request_waiting_for_review,
}
