import os

import pytest
from pydantic import ValidationError

from app.github.fake_client import FakeGitHubIssueCommentClient
from app.github.schemas import (
    GitHubIssueCommentFailure,
    GitHubIssueCommentRequest,
    GitHubIssueCommentResult,
)


def _request() -> GitHubIssueCommentRequest:
    return GitHubIssueCommentRequest(
        repository="Harry5174/learn-agentic-ai",
        issue_number=1,
        comment_body="A deterministic fake comment.",
    )


def test_request_schema_contains_only_issue_comment_fields() -> None:
    request = _request()

    assert request.model_dump() == {
        "repository": "Harry5174/learn-agentic-ai",
        "issue_number": 1,
        "comment_body": "A deterministic fake comment.",
    }

    with pytest.raises(ValidationError):
        GitHubIssueCommentRequest(
            repository="Harry5174/learn-agentic-ai",
            issue_number=1,
            comment_body="A deterministic fake comment.",
            token="ghp_secret",
        )


def test_request_schema_rejects_bool_issue_number() -> None:
    with pytest.raises(ValidationError):
        GitHubIssueCommentRequest(
            repository="Harry5174/learn-agentic-ai",
            issue_number=True,
            comment_body="A deterministic fake comment.",
        )


def test_fake_client_records_calls_and_returns_structured_success() -> None:
    client = FakeGitHubIssueCommentClient()
    request = _request()

    result = client.post_issue_comment(request)

    assert client.calls == [request]
    assert isinstance(result, GitHubIssueCommentResult)
    assert result.repository == request.repository
    assert result.issue_number == request.issue_number
    assert result.comment_id == "fake-comment-1"
    assert result.comment_url is not None
    assert result.status == "simulated"
    assert result.dry_run is True


def test_fake_client_can_simulate_structured_failure() -> None:
    client = FakeGitHubIssueCommentClient(
        should_fail=True,
        failure_error_type="rate_limited",
        failure_message="Simulated rate limit.",
        failure_retryable=True,
    )
    request = _request()

    failure = client.post_issue_comment(request)

    assert client.calls == [request]
    assert isinstance(failure, GitHubIssueCommentFailure)
    assert failure.repository == request.repository
    assert failure.issue_number == request.issue_number
    assert failure.error_type == "rate_limited"
    assert failure.message == "Simulated rate limit."
    assert failure.retryable is True


def test_fake_client_does_not_require_token_or_environment(monkeypatch) -> None:
    monkeypatch.setenv("GITHUB_TOKEN", "ghp_should_not_be_read")
    client = FakeGitHubIssueCommentClient()

    result = client.post_issue_comment(_request())

    assert isinstance(result, GitHubIssueCommentResult)
    assert result.dry_run is True
    assert os.environ["GITHUB_TOKEN"] == "ghp_should_not_be_read"


def test_failure_result_does_not_expose_secret_values() -> None:
    client = FakeGitHubIssueCommentClient(
        should_fail=True,
        failure_message="Simulated failure without credentials.",
    )

    failure = client.post_issue_comment(_request())

    assert isinstance(failure, GitHubIssueCommentFailure)
    assert "ghp_" not in failure.model_dump_json()
    assert "token" not in failure.model_dump_json().lower()
