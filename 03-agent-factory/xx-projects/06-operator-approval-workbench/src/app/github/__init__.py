"""GitHub issue-comment boundary contracts for Artifact 2."""

from app.github.client import GitHubIssueCommentClient
from app.github.fake_client import FakeGitHubIssueCommentClient
from app.github.schemas import (
    GitHubIssueCommentFailure,
    GitHubIssueCommentRequest,
    GitHubIssueCommentResult,
)
from app.github.remote_comments import (
    FakeRemoteIssueCommentLister,
    RemoteIssueComment,
    RemoteIssueCommentLister,
)
from app.github.remote_marker import build_remote_idempotency_marker

__all__ = [
    "FakeGitHubIssueCommentClient",
    "FakeRemoteIssueCommentLister",
    "GitHubIssueCommentClient",
    "GitHubIssueCommentFailure",
    "GitHubIssueCommentRequest",
    "GitHubIssueCommentResult",
    "RemoteIssueComment",
    "RemoteIssueCommentLister",
    "build_remote_idempotency_marker",
]
