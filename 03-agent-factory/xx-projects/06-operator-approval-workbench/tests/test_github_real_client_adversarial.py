import json
from urllib import error

import pytest

from app.github.real_client import (
    GitHubRealClientSafeError,
    RealGitHubIssueCommentClient,
)
from app.github.remote_comments import (
    IncompleteRemoteIssueCommentListingError,
    RemoteIssueCommentListingError,
)
from app.github.schemas import GitHubIssueCommentFailure, GitHubIssueCommentRequest


SECRET_VALUES = (
    "ghp_should_not_leak",
    "github_pat_should_not_leak",
    "secret-token-123",
    "Authorization: Bearer should_not_leak",
)


class Response:
    def __init__(
        self,
        *,
        payload: object | str,
        headers: dict[str, str] | None = None,
    ) -> None:
        self.status = 200
        self.headers = dict(headers or {})
        self._payload = payload

    def read(self) -> bytes:
        if isinstance(self._payload, str):
            return self._payload.encode("utf-8")
        return json.dumps(self._payload).encode("utf-8")


def request() -> GitHubIssueCommentRequest:
    return GitHubIssueCommentRequest(
        repository="Harry5174/artifact-5-github-comment-test",
        issue_number=1,
        comment_body="A5.4 mocked real-client adversarial test.",
    )


def assert_no_secret_leak(payload: object) -> None:
    text = str(payload)
    for secret in SECRET_VALUES:
        assert secret not in text
    assert "Bearer should_not_leak" not in text


def test_real_client_repr_and_str_hide_token_and_transport_secrets() -> None:
    class HostileTransport:
        def __call__(self, outbound_request, timeout_seconds):  # noqa: ANN001, ANN202
            return Response(payload=[])

        def __repr__(self) -> str:
            return (
                "HostileTransport("
                "Authorization: Bearer should_not_leak, ghp_should_not_leak)"
            )

        __str__ = __repr__

    client = RealGitHubIssueCommentClient(
        token="github_pat_should_not_leak",
        transport=HostileTransport(),
    )

    assert_no_secret_leak(repr(client))
    assert_no_secret_leak(str(client))


def test_hostile_transport_exception_is_sanitized_and_not_retried() -> None:
    calls = 0

    def transport(outbound_request, timeout_seconds):  # noqa: ANN001, ANN202
        nonlocal calls
        calls += 1
        raise RuntimeError(
            "Authorization: Bearer ghp_should_not_leak api.github.com"
        )

    client = RealGitHubIssueCommentClient(
        token="ghp_should_not_leak",
        transport=transport,
    )

    result = client.post_issue_comment(request())

    assert isinstance(result, GitHubIssueCommentFailure)
    assert result.error_type == "github_transport_failed"
    assert result.message == "GitHub issue-comment request failed."
    assert result.retryable is True
    assert calls == 1
    assert_no_secret_leak(result.model_dump_json())


def test_timeout_failure_is_sanitized_and_not_retried() -> None:
    calls = 0

    def transport(outbound_request, timeout_seconds):  # noqa: ANN001, ANN202
        nonlocal calls
        calls += 1
        raise TimeoutError("Authorization: Bearer ghp_should_not_leak")

    client = RealGitHubIssueCommentClient(
        token="secret-token-123",
        transport=transport,
    )

    result = client.post_issue_comment(request())

    assert isinstance(result, GitHubIssueCommentFailure)
    assert result.error_type == "github_timeout"
    assert result.retryable is True
    assert calls == 1
    assert_no_secret_leak(result.model_dump_json())


@pytest.mark.parametrize("status", [401, 403, 404, 409, 422, 429, 500, 502, 503])
def test_http_failures_are_safe_and_status_specific(status: int) -> None:
    def transport(outbound_request, timeout_seconds):  # noqa: ANN001, ANN202
        raise error.HTTPError(
            outbound_request.full_url,
            status,
            "Authorization: Bearer ghp_should_not_leak",
            hdrs={},
            fp=None,
        )

    client = RealGitHubIssueCommentClient(
        token="github_pat_should_not_leak",
        transport=transport,
    )

    result = client.post_issue_comment(request())

    assert isinstance(result, GitHubIssueCommentFailure)
    assert result.error_type == f"github_http_{status}"
    assert result.message == "GitHub issue-comment request failed."
    assert result.retryable is (status >= 500 or status == 429)
    assert_no_secret_leak(result.model_dump_json())


@pytest.mark.parametrize(
    "payload",
    [
        "not-json Authorization: Bearer should_not_leak",
        [],
        {"id": 123},
        {"html_url": "https://example.invalid/comment/123"},
        {"id": 123, "html_url": None},
        {"id": 123, "url": "https://example.invalid/api/comment/123"},
    ],
)
def test_malformed_create_responses_fail_safely(payload: object | str) -> None:
    client = RealGitHubIssueCommentClient(
        token="ghp_should_not_leak",
        transport=lambda outbound_request, timeout_seconds: Response(payload=payload),
    )

    result = client.post_issue_comment(request())

    assert isinstance(result, GitHubIssueCommentFailure)
    assert result.error_type == "github_malformed_response"
    assert_no_secret_leak(result.model_dump_json())


def test_listing_http_failure_raises_safe_error_without_secret_text() -> None:
    def transport(outbound_request, timeout_seconds):  # noqa: ANN001, ANN202
        raise error.HTTPError(
            outbound_request.full_url,
            503,
            "Authorization: Bearer ghp_should_not_leak",
            hdrs={},
            fp=None,
        )

    client = RealGitHubIssueCommentClient(
        token="secret-token-123",
        transport=transport,
    )

    with pytest.raises(GitHubRealClientSafeError) as exc_info:
        client.list_issue_comments(request())

    assert exc_info.value.error_type == "github_http_503"
    assert_no_secret_leak(str(exc_info.value))
    assert_no_secret_leak(repr(exc_info.value))


@pytest.mark.parametrize(
    "payload",
    [
        {"not": "a-list"},
        [{"id": 1}],
        [{"body": "missing id"}],
        [{"id": 1, "body": ["not", "text"]}],
        [{"id": 1, "body": "ok", "html_url": {"not": "text"}}],
    ],
)
def test_malformed_listing_responses_fail_safely(payload: object) -> None:
    client = RealGitHubIssueCommentClient(
        token="github_pat_should_not_leak",
        transport=lambda outbound_request, timeout_seconds: Response(payload=payload),
    )

    with pytest.raises(
        (GitHubRealClientSafeError, RemoteIssueCommentListingError)
    ) as exc_info:
        client.list_issue_comments(request())

    assert_no_secret_leak(str(exc_info.value))
    assert_no_secret_leak(repr(exc_info.value))


def test_marker_after_page_bound_is_incomplete_and_safe() -> None:
    def transport(outbound_request, timeout_seconds):  # noqa: ANN001, ANN202
        return Response(
            payload=[],
            headers={
                "Link": (
                    '<https://api.github.com/repositories/x/issues/1/comments'
                    '?page=2>; rel="next"'
                )
            },
        )

    client = RealGitHubIssueCommentClient(
        token="ghp_should_not_leak",
        transport=transport,
        max_pages=1,
    )

    with pytest.raises(IncompleteRemoteIssueCommentListingError) as exc_info:
        client.list_issue_comments(request())

    assert "page bound" in str(exc_info.value)
    assert_no_secret_leak(str(exc_info.value))


def test_malformed_pagination_link_fails_closed_without_secret_text() -> None:
    client = RealGitHubIssueCommentClient(
        token="github_pat_should_not_leak",
        transport=lambda outbound_request, timeout_seconds: Response(
            payload=[],
            headers={"Link": 'https://example.invalid?page=2; rel="next"'},
        ),
    )

    with pytest.raises(IncompleteRemoteIssueCommentListingError) as exc_info:
        client.list_issue_comments(request())

    assert "pagination link was malformed" in str(exc_info.value)
    assert_no_secret_leak(str(exc_info.value))
