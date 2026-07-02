"""Typed internal records for local GitHub-like fixture snapshots."""

from __future__ import annotations

from dataclasses import dataclass


class RepoSnapshotValidationError(ValueError):
    """Raised when a local fixture snapshot is missing required data."""


@dataclass(frozen=True)
class RepositoryIdentity:
    owner: str
    name: str
    default_branch: str
    snapshot_generated_at: str


@dataclass(frozen=True)
class LabelRecord:
    name: str
    description: str
    color: str | None = None


@dataclass(frozen=True)
class IssueRecord:
    id: int
    number: int
    title: str
    body: str
    state: str
    labels: tuple[str, ...]
    author: str
    created_at: str
    updated_at: str
    comments_count: int
    stale_days: int


@dataclass(frozen=True)
class PullRequestRecord:
    id: int
    number: int
    title: str
    body: str
    state: str
    labels: tuple[str, ...]
    author: str
    created_at: str
    updated_at: str
    branch: str
    base_branch: str
    review_status: str
    ci_status: str
    stale_days: int


@dataclass(frozen=True)
class CommentRecord:
    id: int
    target_type: str
    target_number: int
    author: str
    body: str
    created_at: str


@dataclass(frozen=True)
class CiStatusSummary:
    target_type: str
    target_number: int
    status: str
    conclusion: str
    updated_at: str


@dataclass(frozen=True)
class NormalizedRepoSnapshot:
    repository: RepositoryIdentity
    labels: tuple[LabelRecord, ...]
    issues: tuple[IssueRecord, ...]
    pull_requests: tuple[PullRequestRecord, ...]
    comments: tuple[CommentRecord, ...]
    ci_statuses: tuple[CiStatusSummary, ...]
