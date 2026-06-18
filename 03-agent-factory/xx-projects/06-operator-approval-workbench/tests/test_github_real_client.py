import json
from urllib import error

import pytest

from app.github.real_client import RealGitHubIssueCommentClient
from app.github.remote_comments import IncompleteRemoteIssueCommentListingError
from app.github.schemas import GitHubIssueCommentFailure, GitHubIssueCommentRequest


class Response:
    def __init__(
        self,
        *,
        status: int = 200,
        payload: object | str,
        headers: dict[str, str] | None = None,
    ) -> None:
        self.status = status
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
        comment_body="A real-mode test comment.",
    )


def test_real_client_repr_does_not_expose_token_or_transport() -> None:
    class SensitiveTransport:
        def __call__(self, outbound_request, timeout_seconds):  # noqa: ANN001, ANN202
            return Response(payload=[])

        def __repr__(self) -> str:
            return "SensitiveTransport(token=ghp_transport_secret Authorization=Bearer x)"

    client = RealGitHubIssueCommentClient(
        token="ghp_should_not_leak",
        transport=SensitiveTransport(),
    )

    client_repr = repr(client)

    assert "ghp_should_not_leak" not in client_repr
    assert "ghp_transport_secret" not in client_repr
    assert "Authorization" not in client_repr
    assert "Bearer" not in client_repr
    assert "SensitiveTransport" not in client_repr


def test_real_client_lists_paginated_issue_comments() -> None:
    calls = []

    def transport(outbound_request, timeout_seconds):  # noqa: ANN001, ANN202
        calls.append((outbound_request, timeout_seconds))
        if len(calls) == 1:
            return Response(
                payload=[{"id": 1, "html_url": "https://example.invalid/1", "body": "a"}],
                headers={
                    "Link": (
                        '<https://api.github.com/repositories/x/issues/1/comments'
                        '?page=2>; rel="next"'
                    )
                },
            )
        return Response(
            payload=[{"id": 2, "html_url": "https://example.invalid/2", "body": "b"}],
        )

    client = RealGitHubIssueCommentClient(
        token="secret-token",
        transport=transport,
        timeout_seconds=3.0,
    )

    comments = client.list_issue_comments(request())

    assert [comment.comment_id for comment in comments] == ["1", "2"]
    assert len(calls) == 2
    assert calls[0][1] == 3.0
    assert calls[0][0].get_method() == "GET"


def test_real_client_fails_closed_when_page_bound_exceeded() -> None:
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
        token="secret-token",
        transport=transport,
        max_pages=1,
    )

    with pytest.raises(IncompleteRemoteIssueCommentListingError):
        client.list_issue_comments(request())


def test_real_client_create_comment_returns_safe_result() -> None:
    captured_body = {}

    def transport(outbound_request, timeout_seconds):  # noqa: ANN001, ANN202
        captured_body["body"] = json.loads(outbound_request.data.decode("utf-8"))
        return Response(
            status=201,
            payload={"id": 123, "html_url": "https://example.invalid/comment/123"},
        )

    client = RealGitHubIssueCommentClient(token="secret-token", transport=transport)

    result = client.post_issue_comment(request())

    assert result.comment_id == "123"
    assert result.comment_url == "https://example.invalid/comment/123"
    assert result.dry_run is False
    assert captured_body["body"] == {"body": "A real-mode test comment."}


@pytest.mark.parametrize("status", [401, 403, 404, 422, 500])
def test_real_client_http_failures_are_safe(status: int) -> None:
    def transport(outbound_request, timeout_seconds):  # noqa: ANN001, ANN202
        raise error.HTTPError(
            outbound_request.full_url,
            status,
            "raw transport text must not leak",
            hdrs={},
            fp=None,
        )

    client = RealGitHubIssueCommentClient(token="secret-token", transport=transport)

    result = client.post_issue_comment(request())

    assert isinstance(result, GitHubIssueCommentFailure)
    assert result.error_type == f"github_http_{status}"
    assert result.message == "GitHub issue-comment request failed."
    assert "secret-token" not in result.model_dump_json()
    assert "raw transport text" not in result.model_dump_json()


def test_real_client_malformed_create_response_fails_safely() -> None:
    client = RealGitHubIssueCommentClient(
        token="secret-token",
        transport=lambda outbound_request, timeout_seconds: Response(payload={"id": 1}),
    )

    result = client.post_issue_comment(request())

    assert isinstance(result, GitHubIssueCommentFailure)
    assert result.error_type == "github_malformed_response"
    assert "secret-token" not in result.model_dump_json()
