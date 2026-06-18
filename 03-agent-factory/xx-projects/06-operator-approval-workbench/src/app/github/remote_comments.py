from typing import Protocol

from pydantic import BaseModel, ConfigDict, Field

from app.github.schemas import GitHubIssueCommentRequest


class RemoteIssueComment(BaseModel):
    """Safe fake/mocked representation of an existing remote issue comment."""

    model_config = ConfigDict(extra="forbid")

    comment_id: str = Field(min_length=1)
    comment_url: str | None = None
    body: str = Field(min_length=1)


class RemoteIssueCommentListingError(RuntimeError):
    """Raised when fake/mocked remote comment listing fails."""


class IncompleteRemoteIssueCommentListingError(RemoteIssueCommentListingError):
    """Raised when a remote listing cannot prove marker-search completeness."""


class RemoteIssueCommentLister(Protocol):
    """Fake/mocked-only boundary for listing existing issue comments."""

    def list_issue_comments(
        self,
        request: GitHubIssueCommentRequest,
    ) -> list[RemoteIssueComment]:
        """Return safe existing comment data for an already validated request."""


class FakeRemoteIssueCommentLister:
    """Deterministic in-memory lister for remote marker reconciliation tests."""

    def __init__(
        self,
        comments: list[RemoteIssueComment] | None = None,
        *,
        should_fail: bool = False,
        failure_message: str = "Simulated remote issue-comment listing failure.",
    ) -> None:
        self.comments = list(comments or [])
        self.should_fail = should_fail
        self.failure_message = failure_message
        self.calls: list[GitHubIssueCommentRequest] = []

    def list_issue_comments(
        self,
        request: GitHubIssueCommentRequest,
    ) -> list[RemoteIssueComment]:
        self.calls.append(request)

        if self.should_fail:
            raise RemoteIssueCommentListingError(self.failure_message)

        return list(self.comments)
