"""Local fixture intake for Artifact 07 GitHub Repo Steward."""

from github_repo_steward.models import (
    CiStatusSummary,
    CommentRecord,
    IssueRecord,
    LabelRecord,
    NormalizedRepoSnapshot,
    PullRequestRecord,
    RepositoryIdentity,
    RepoSnapshotValidationError,
)
from github_repo_steward.normalizer import normalize_repo_snapshot
from github_repo_steward.repo_snapshot import (
    RawRepoSnapshot,
    load_default_fixture_snapshot,
    load_fixture_snapshot,
)

__all__ = [
    "CiStatusSummary",
    "CommentRecord",
    "IssueRecord",
    "LabelRecord",
    "NormalizedRepoSnapshot",
    "PullRequestRecord",
    "RawRepoSnapshot",
    "RepositoryIdentity",
    "RepoSnapshotValidationError",
    "load_default_fixture_snapshot",
    "load_fixture_snapshot",
    "normalize_repo_snapshot",
]
