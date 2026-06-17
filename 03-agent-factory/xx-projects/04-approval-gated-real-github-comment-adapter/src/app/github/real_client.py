from app.github.client import GitHubIssueCommentResponse
from app.github.real_mode import GitHubRealModeConfig
from app.github.schemas import GitHubIssueCommentFailure, GitHubIssueCommentRequest
from app.github.token_provider import (
    GITHUB_CREDENTIALS_UNAVAILABLE_MESSAGE,
    GitHubTokenProvider,
    MissingGitHubTokenError,
)


class DisabledRealGitHubIssueCommentClient:
    """Non-executing boundary for a future real GitHub issue-comment client."""

    def __init__(
        self,
        *,
        config: GitHubRealModeConfig | None = None,
        token_provider: GitHubTokenProvider | None = None,
    ) -> None:
        self.config = config or GitHubRealModeConfig()
        self._token_provider = token_provider

    def post_issue_comment(
        self,
        request: GitHubIssueCommentRequest,
    ) -> GitHubIssueCommentResponse:
        if not self.config.enabled:
            return GitHubIssueCommentFailure.credentials_unavailable(
                request=request,
                error_type="real_github_execution_disabled",
            )

        if self._token_provider is None:
            return GitHubIssueCommentFailure.credentials_unavailable(
                request=request,
                error_type="missing_github_token_provider",
            )

        try:
            self._token_provider.get_token()
        except MissingGitHubTokenError:
            return GitHubIssueCommentFailure.credentials_unavailable(
                request=request,
                error_type="missing_github_token",
            )

        return GitHubIssueCommentFailure(
            repository=request.repository,
            issue_number=request.issue_number,
            error_type="real_github_execution_not_implemented",
            message=GITHUB_CREDENTIALS_UNAVAILABLE_MESSAGE,
            retryable=False,
        )
