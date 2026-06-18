from typing import Protocol

from app.github.schemas import (
    GitHubIssueCommentFailure,
    GitHubIssueCommentRequest,
    GitHubIssueCommentResult,
)
from app.github.remote_comments import RemoteIssueCommentLister


GitHubIssueCommentResponse = GitHubIssueCommentResult | GitHubIssueCommentFailure


class GitHubIssueCommentClient(Protocol):
    """Minimal boundary for fake or future issue-comment clients."""

    def post_issue_comment(
        self,
        request: GitHubIssueCommentRequest,
    ) -> GitHubIssueCommentResponse:
        """Return a structured response for an already validated request."""


class GitHubIssueCommentRemoteClient(
    GitHubIssueCommentClient,
    RemoteIssueCommentLister,
    Protocol,
):
    """Narrow real-client protocol for listing and creating issue comments."""
