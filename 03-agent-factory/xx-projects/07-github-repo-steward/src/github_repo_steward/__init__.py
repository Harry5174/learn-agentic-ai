"""Local fixture intake for Artifact 07 GitHub Repo Steward."""

from github_repo_steward.analyzer import analyze_repo_snapshot
from github_repo_steward.fake_proposal_provider import FakeProposalProvider
from github_repo_steward.models import (
    CiStatusSummary,
    CommentRecord,
    IssueRecord,
    LabelRecord,
    NormalizedRepoSnapshot,
    PullRequestRecord,
    RepoFinding,
    RepoProposal,
    RepoProposalValidationError,
    RepositoryIdentity,
    RepoSnapshotValidationError,
)
from github_repo_steward.normalizer import normalize_repo_snapshot
from github_repo_steward.proposal_provider import (
    ProposalProvider,
    validate_repo_proposal,
)
from github_repo_steward.repo_snapshot import (
    RawRepoSnapshot,
    load_default_fixture_snapshot,
    load_fixture_snapshot,
)

__all__ = [
    "CiStatusSummary",
    "CommentRecord",
    "FakeProposalProvider",
    "IssueRecord",
    "LabelRecord",
    "NormalizedRepoSnapshot",
    "ProposalProvider",
    "PullRequestRecord",
    "RepoFinding",
    "RepoProposal",
    "RepoProposalValidationError",
    "RawRepoSnapshot",
    "RepositoryIdentity",
    "RepoSnapshotValidationError",
    "analyze_repo_snapshot",
    "load_default_fixture_snapshot",
    "load_fixture_snapshot",
    "normalize_repo_snapshot",
    "validate_repo_proposal",
]
