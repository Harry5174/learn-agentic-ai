from typing import Protocol

from app.github.schemas import (
    GitHubIssueCommentFailure,
    GitHubIssueCommentRequest,
    GitHubIssueCommentResult,
)


GitHubIssueCommentResponse = GitHubIssueCommentResult | GitHubIssueCommentFailure


class GitHubIssueCommentClient(Protocol):
    """Minimal boundary for posting a GitHub issue comment."""

    def post_issue_comment(
        self,
        request: GitHubIssueCommentRequest,
    ) -> GitHubIssueCommentResponse:
        """Post or simulate posting an issue comment for an already validated request."""
