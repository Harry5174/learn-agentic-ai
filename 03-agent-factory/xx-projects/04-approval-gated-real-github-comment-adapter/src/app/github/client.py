from typing import Protocol

from app.github.schemas import (
    GitHubIssueCommentFailure,
    GitHubIssueCommentRequest,
    GitHubIssueCommentResult,
)


GitHubIssueCommentResponse = GitHubIssueCommentResult | GitHubIssueCommentFailure


class GitHubIssueCommentClient(Protocol):
    """Minimal boundary for fake or future issue-comment clients."""

    def post_issue_comment(
        self,
        request: GitHubIssueCommentRequest,
    ) -> GitHubIssueCommentResponse:
        """Return a structured response for an already validated request."""
