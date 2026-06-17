"""GitHub issue-comment boundary contracts for Artifact 3."""

from app.github.client import GitHubIssueCommentClient
from app.github.fake_client import FakeGitHubIssueCommentClient
from app.github.schemas import (
    GitHubIssueCommentFailure,
    GitHubIssueCommentRequest,
    GitHubIssueCommentResult,
)

__all__ = [
    "FakeGitHubIssueCommentClient",
    "GitHubIssueCommentClient",
    "GitHubIssueCommentFailure",
    "GitHubIssueCommentRequest",
    "GitHubIssueCommentResult",
]
