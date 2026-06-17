from app.github.client import GitHubIssueCommentResponse
from app.github.schemas import (
    GitHubIssueCommentFailure,
    GitHubIssueCommentRequest,
    GitHubIssueCommentResult,
)


class FakeGitHubIssueCommentClient:
    """Deterministic in-memory fake for GitHub issue-comment tests."""

    def __init__(
        self,
        *,
        should_fail: bool = False,
        failure_error_type: str = "simulated_github_failure",
        failure_message: str = "Simulated GitHub issue-comment failure.",
        failure_retryable: bool = False,
    ) -> None:
        self.should_fail = should_fail
        self.failure_error_type = failure_error_type
        self.failure_message = failure_message
        self.failure_retryable = failure_retryable
        self.calls: list[GitHubIssueCommentRequest] = []

    def post_issue_comment(
        self,
        request: GitHubIssueCommentRequest,
    ) -> GitHubIssueCommentResponse:
        self.calls.append(request)

        if self.should_fail:
            return GitHubIssueCommentFailure(
                repository=request.repository,
                issue_number=request.issue_number,
                error_type=self.failure_error_type,
                message=self.failure_message,
                retryable=self.failure_retryable,
            )

        call_number = len(self.calls)
        comment_id = f"fake-comment-{call_number}"

        return GitHubIssueCommentResult(
            repository=request.repository,
            issue_number=request.issue_number,
            comment_id=comment_id,
            comment_url=(
                "https://example.invalid/"
                f"{request.repository}/issues/{request.issue_number}"
                f"#issuecomment-{comment_id}"
            ),
            status="simulated",
            dry_run=True,
        )
