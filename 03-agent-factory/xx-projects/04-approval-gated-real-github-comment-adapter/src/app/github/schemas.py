from pydantic import BaseModel, ConfigDict, Field, field_validator


class GitHubIssueCommentRequest(BaseModel):
    """Already validated request to post a GitHub issue comment."""

    model_config = ConfigDict(extra="forbid")

    repository: str = Field(min_length=1)
    issue_number: int = Field(ge=1)
    comment_body: str = Field(min_length=1)

    @field_validator("issue_number", mode="before")
    @classmethod
    def reject_bool_issue_number(cls, value: object) -> object:
        if isinstance(value, bool):
            raise ValueError("issue_number must be an integer")

        return value


class GitHubIssueCommentResult(BaseModel):
    """Safe audit-facing result for an issue-comment client call."""

    model_config = ConfigDict(extra="forbid")

    repository: str
    issue_number: int
    comment_id: str | None = None
    comment_url: str | None = None
    status: str
    dry_run: bool = True


class GitHubIssueCommentFailure(BaseModel):
    """Safe audit-facing failure for an issue-comment client call."""

    model_config = ConfigDict(extra="forbid")

    repository: str
    issue_number: int
    error_type: str
    message: str
    retryable: bool = False

    @classmethod
    def credentials_unavailable(
        cls,
        *,
        request: GitHubIssueCommentRequest,
        error_type: str = "github_credentials_unavailable",
    ) -> "GitHubIssueCommentFailure":
        return cls(
            repository=request.repository,
            issue_number=request.issue_number,
            error_type=error_type,
            message="GitHub credentials are unavailable.",
            retryable=False,
        )
