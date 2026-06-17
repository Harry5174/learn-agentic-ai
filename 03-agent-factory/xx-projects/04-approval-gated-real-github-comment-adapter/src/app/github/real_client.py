import json
import socket
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from typing import Any, Protocol
from urllib import error, parse, request as urllib_request

from app.github.client import GitHubIssueCommentResponse
from app.github.remote_comments import (
    IncompleteRemoteIssueCommentListingError,
    RemoteIssueComment,
    RemoteIssueCommentListingError,
)
from app.github.real_mode import GitHubRealModeConfig
from app.github.schemas import (
    GitHubIssueCommentFailure,
    GitHubIssueCommentRequest,
    GitHubIssueCommentResult,
)
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


class GitHubHTTPResponse(Protocol):
    """Minimal response boundary used by the narrow real GitHub client."""

    status: int
    headers: Mapping[str, str]

    def read(self) -> bytes:
        """Return the response body bytes."""


GitHubHTTPTransport = Callable[
    [urllib_request.Request, float],
    GitHubHTTPResponse,
]


@dataclass(frozen=True)
class RealGitHubIssueCommentClient:
    """Narrow real GitHub issue-comment client for list/create only."""

    token: str = field(repr=False)
    transport: GitHubHTTPTransport | None = field(default=None, repr=False)
    timeout_seconds: float = 10.0
    max_pages: int = 10

    def list_issue_comments(
        self,
        request: GitHubIssueCommentRequest,
    ) -> list[RemoteIssueComment]:
        comments: list[RemoteIssueComment] = []
        next_url: str | None = _issue_comments_url(request)
        pages_seen = 0

        while next_url is not None:
            pages_seen += 1
            if pages_seen > self.max_pages:
                raise IncompleteRemoteIssueCommentListingError(
                    "Remote issue-comment listing exceeded the safe page bound."
                )

            response = self._send(
                "GET",
                next_url,
            )
            payload = _decode_json(response)
            if not isinstance(payload, list):
                raise RemoteIssueCommentListingError(
                    "Malformed GitHub issue-comment listing response."
                )

            comments.extend(_remote_comments_from_payload(payload))
            next_url = _next_link(response.headers)

        return comments

    def post_issue_comment(
        self,
        request: GitHubIssueCommentRequest,
    ) -> GitHubIssueCommentResponse:
        response = self.create_issue_comment(request)
        return response

    def create_issue_comment(
        self,
        request: GitHubIssueCommentRequest,
    ) -> GitHubIssueCommentResponse:
        try:
            response = self._send(
                "POST",
                _issue_comments_url(request),
                body={"body": request.comment_body},
            )
            payload = _decode_json(response)
        except GitHubRealClientSafeError as exc:
            return GitHubIssueCommentFailure(
                repository=request.repository,
                issue_number=request.issue_number,
                error_type=exc.error_type,
                message=exc.safe_message,
                retryable=exc.retryable,
            )

        if not isinstance(payload, dict):
            return _malformed_response_failure(request)

        comment_id = payload.get("id")
        comment_url = payload.get("html_url")
        if not isinstance(comment_id, int | str) or not isinstance(
            comment_url,
            str,
        ):
            return _malformed_response_failure(request)

        return GitHubIssueCommentResult(
            repository=request.repository,
            issue_number=request.issue_number,
            comment_id=str(comment_id),
            comment_url=comment_url,
            status="posted",
            dry_run=False,
        )

    def _send(
        self,
        method: str,
        url: str,
        body: dict[str, Any] | None = None,
    ) -> GitHubHTTPResponse:
        body_bytes: bytes | None = None
        if body is not None:
            body_bytes = json.dumps(body).encode("utf-8")

        outbound_request = urllib_request.Request(
            url,
            data=body_bytes,
            method=method,
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
                "User-Agent": "agent-factory-artifact-5",
                "X-GitHub-Api-Version": "2022-11-28",
            },
        )

        try:
            active_transport = self.transport or _urlopen_transport
            return active_transport(outbound_request, self.timeout_seconds)
        except error.HTTPError as exc:
            raise _safe_http_failure(exc.code)
        except TimeoutError:
            raise GitHubRealClientSafeError(
                error_type="github_timeout",
                retryable=True,
            )
        except socket.timeout:
            raise GitHubRealClientSafeError(
                error_type="github_timeout",
                retryable=True,
            )
        except GitHubRealClientSafeError:
            raise
        except Exception:
            raise GitHubRealClientSafeError(
                error_type="github_transport_failed",
                retryable=True,
            )


class GitHubRealClientSafeError(RuntimeError):
    """Credential-free client failure category."""

    def __init__(
        self,
        *,
        error_type: str,
        safe_message: str = "GitHub issue-comment request failed.",
        retryable: bool = False,
    ) -> None:
        super().__init__(safe_message)
        self.error_type = error_type
        self.safe_message = safe_message
        self.retryable = retryable


def _urlopen_transport(
    outbound_request: urllib_request.Request,
    timeout_seconds: float,
) -> GitHubHTTPResponse:
    return urllib_request.urlopen(outbound_request, timeout=timeout_seconds)


def _issue_comments_url(request: GitHubIssueCommentRequest) -> str:
    owner, repository = _repository_parts(request.repository)
    return (
        "https://api.github.com/repos/"
        f"{parse.quote(owner, safe='')}/"
        f"{parse.quote(repository, safe='')}/issues/"
        f"{request.issue_number}/comments?per_page=100"
    )


def _repository_parts(repository: str) -> tuple[str, str]:
    owner, repo = repository.split("/", maxsplit=1)
    return owner, repo


def _decode_json(response: GitHubHTTPResponse) -> Any:
    try:
        return json.loads(response.read().decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        raise GitHubRealClientSafeError(
            error_type="github_malformed_response",
            retryable=False,
        )


def _remote_comments_from_payload(payload: list[Any]) -> list[RemoteIssueComment]:
    comments: list[RemoteIssueComment] = []
    for item in payload:
        if not isinstance(item, dict):
            raise RemoteIssueCommentListingError(
                "Malformed GitHub issue-comment listing response."
            )
        comment_id = item.get("id")
        body = item.get("body")
        comment_url = item.get("html_url")
        if not isinstance(comment_id, int | str) or not isinstance(body, str):
            raise RemoteIssueCommentListingError(
                "Malformed GitHub issue-comment listing response."
            )
        if comment_url is not None and not isinstance(comment_url, str):
            raise RemoteIssueCommentListingError(
                "Malformed GitHub issue-comment listing response."
            )
        comments.append(
            RemoteIssueComment(
                comment_id=str(comment_id),
                comment_url=comment_url,
                body=body,
            )
        )
    return comments


def _next_link(headers: Mapping[str, str]) -> str | None:
    link_value = _header_value(headers, "Link")
    if link_value is None:
        return None

    for segment in link_value.split(","):
        pieces = [piece.strip() for piece in segment.split(";")]
        if len(pieces) < 2:
            continue
        url_part = pieces[0]
        rel_parts = {piece for piece in pieces[1:] if piece.startswith("rel=")}
        if 'rel="next"' in rel_parts:
            if not (url_part.startswith("<") and url_part.endswith(">")):
                raise IncompleteRemoteIssueCommentListingError(
                    "Remote issue-comment pagination link was malformed."
                )
            return url_part[1:-1]

    return None


def _header_value(headers: Mapping[str, str], name: str) -> str | None:
    for key, value in headers.items():
        if key.lower() == name.lower():
            return value
    return None


def _safe_http_failure(status_code: int) -> GitHubRealClientSafeError:
    retryable = status_code >= 500
    known_statuses = {401, 403, 404, 422}
    error_type = (
        f"github_http_{status_code}"
        if status_code in known_statuses or status_code >= 500
        else "github_http_error"
    )
    return GitHubRealClientSafeError(
        error_type=error_type,
        retryable=retryable,
    )


def _malformed_response_failure(
    request: GitHubIssueCommentRequest,
) -> GitHubIssueCommentFailure:
    return GitHubIssueCommentFailure(
        repository=request.repository,
        issue_number=request.issue_number,
        error_type="github_malformed_response",
        message="GitHub issue-comment response was malformed.",
        retryable=False,
    )
