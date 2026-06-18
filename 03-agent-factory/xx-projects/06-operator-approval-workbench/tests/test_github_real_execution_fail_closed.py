from pathlib import Path

import pytest

from app.github.real_mode import GitHubRealModeConfig
from app.github.remote_comments import RemoteIssueComment, RemoteIssueCommentListingError
from app.github.remote_marker import build_remote_idempotency_marker
from app.github.schemas import (
    GitHubIssueCommentFailure,
    GitHubIssueCommentRequest,
    GitHubIssueCommentResult,
)
from app.github.token_provider import MissingGitHubTokenError
from app.side_effects.durable_schemas import DurableSideEffectStatus
from app.side_effects.idempotency import validated_arguments_hash
from app.tools.context import ToolExecutionContext
from app.tools.github_comment import GITHUB_COMMENT_STEP_ID, GITHUB_COMMENT_TOOL_NAME
from app.tools.github_comment_real_execution import post_real_github_issue_comment
from restart_replay_helpers import (
    VALID_ARGUMENTS,
    argument_hash,
    persist_action_with_status,
    persist_approved_action,
    persist_planned_action,
    stores,
)


REAL_REPOSITORY = "Harry5174/artifact-5-github-comment-test"
REAL_ARGUMENTS = {
    **VALID_ARGUMENTS,
    "repository": REAL_REPOSITORY,
}


class CountingTokenProvider:
    def __init__(self, token: str = "server-side-token") -> None:
        self.token = token
        self.calls = 0

    def get_token(self) -> str:
        self.calls += 1
        return self.token


class MissingTokenProvider:
    def __init__(self) -> None:
        self.calls = 0

    def get_token(self) -> str:
        self.calls += 1
        raise MissingGitHubTokenError()


class FakeRealGitHubClient:
    def __init__(self, comments: list[RemoteIssueComment] | None = None) -> None:
        self.comments = list(comments or [])
        self.list_calls: list[GitHubIssueCommentRequest] = []
        self.post_calls: list[GitHubIssueCommentRequest] = []

    def list_issue_comments(
        self,
        request: GitHubIssueCommentRequest,
    ) -> list[RemoteIssueComment]:
        self.list_calls.append(request)
        return list(self.comments)

    def post_issue_comment(
        self,
        request: GitHubIssueCommentRequest,
    ) -> GitHubIssueCommentResult:
        self.post_calls.append(request)
        return GitHubIssueCommentResult(
            repository=request.repository,
            issue_number=request.issue_number,
            comment_id="real-comment-1",
            comment_url="https://example.invalid/real-comment-1",
            status="posted",
            dry_run=False,
        )


def request(arguments: dict[str, object] | None = None) -> GitHubIssueCommentRequest:
    return GitHubIssueCommentRequest.model_validate(arguments or REAL_ARGUMENTS)


def approved_context(
    tmp_path: Path,
    *,
    real_client: FakeRealGitHubClient | None = None,
    token_provider: CountingTokenProvider | None = None,
    config: GitHubRealModeConfig | None = None,
    arguments: dict[str, object] | None = None,
) -> tuple[ToolExecutionContext, str, str, CountingTokenProvider, FakeRealGitHubClient]:
    manager, ledger, approval_store = stores(tmp_path / "durable.sqlite")
    active_arguments = arguments or REAL_ARGUMENTS
    side_effect_id, args_hash = persist_approved_action(
        ledger,
        approval_store,
        arguments=active_arguments,
    )
    active_token_provider = token_provider or CountingTokenProvider()
    active_real_client = real_client or FakeRealGitHubClient()
    return (
        ToolExecutionContext(
            run_id="run-durable-1",
            step_id=GITHUB_COMMENT_STEP_ID,
            durable_side_effect_ledger=ledger,
            durable_approval_binding_store=approval_store,
            real_github_issue_comment_client=active_real_client,
            github_real_mode_config=config
            or GitHubRealModeConfig(
                enabled=True,
                allowed_repositories=(REAL_REPOSITORY,),
                client_mode="real",
            ),
            github_token_provider=active_token_provider,
        ),
        side_effect_id,
        args_hash,
        active_token_provider,
        active_real_client,
    )


def execute(
    execution_context: ToolExecutionContext,
    *,
    side_effect_id: str,
    args_hash: str,
    active_request: GitHubIssueCommentRequest | None = None,
):
    return post_real_github_issue_comment(
        tool_name=GITHUB_COMMENT_TOOL_NAME,
        request=active_request or request(),
        context=execution_context,
        side_effect_id=side_effect_id,
        argument_hash=args_hash,
    )


def test_real_mode_disabled_fails_before_token_or_network(tmp_path: Path) -> None:
    execution_context, side_effect_id, args_hash, token_provider, real_client = (
        approved_context(
            tmp_path,
            config=GitHubRealModeConfig(
                enabled=False,
                allowed_repositories=(REAL_REPOSITORY,),
            ),
        )
    )

    result = execute(
        execution_context,
        side_effect_id=side_effect_id,
        args_hash=args_hash,
    )

    assert result.success is False
    assert result.result["error_type"] == "real_github_execution_disabled"
    assert token_provider.calls == 0
    assert real_client.list_calls == []
    assert real_client.post_calls == []


def test_missing_token_provider_fails_before_network(tmp_path: Path) -> None:
    execution_context, side_effect_id, args_hash, _, real_client = approved_context(
        tmp_path,
        token_provider=CountingTokenProvider(),
    )
    execution_context = ToolExecutionContext(
        **{
            **execution_context.__dict__,
            "github_token_provider": None,
        }
    )

    result = execute(
        execution_context,
        side_effect_id=side_effect_id,
        args_hash=args_hash,
    )

    assert result.success is False
    assert result.result["error_type"] == "missing_github_token_provider"
    assert real_client.list_calls == []
    assert real_client.post_calls == []


def test_missing_token_fails_before_network(tmp_path: Path) -> None:
    token_provider = MissingTokenProvider()
    execution_context, side_effect_id, args_hash, _, real_client = approved_context(
        tmp_path,
        token_provider=token_provider,
    )

    result = execute(
        execution_context,
        side_effect_id=side_effect_id,
        args_hash=args_hash,
    )

    assert result.success is False
    assert result.result["error_type"] == "missing_github_token"
    assert token_provider.calls == 1
    assert real_client.list_calls == []
    assert real_client.post_calls == []


def test_repo_not_allowlisted_blocks_before_token_or_network(tmp_path: Path) -> None:
    denied_arguments = {**REAL_ARGUMENTS, "repository": "Harry5174/not-allowed"}
    execution_context, side_effect_id, args_hash, token_provider, real_client = (
        approved_context(
            tmp_path,
            arguments=denied_arguments,
        )
    )

    result = execute(
        execution_context,
        side_effect_id=side_effect_id,
        args_hash=args_hash,
        active_request=request(denied_arguments),
    )

    assert result.success is False
    assert result.result["error_type"] == "repository_not_allowlisted"
    assert token_provider.calls == 0
    assert real_client.list_calls == []
    assert real_client.post_calls == []


def test_missing_approval_blocks_before_token_or_network(tmp_path: Path) -> None:
    manager, ledger, approval_store = stores(tmp_path / "durable.sqlite")
    side_effect_id = persist_planned_action(ledger, arguments=REAL_ARGUMENTS)
    token_provider = CountingTokenProvider()
    real_client = FakeRealGitHubClient()
    execution_context = ToolExecutionContext(
        run_id="run-durable-1",
        step_id=GITHUB_COMMENT_STEP_ID,
        durable_side_effect_ledger=ledger,
        durable_approval_binding_store=approval_store,
        real_github_issue_comment_client=real_client,
        github_real_mode_config=GitHubRealModeConfig(
            enabled=True,
            allowed_repositories=(REAL_REPOSITORY,),
            client_mode="real",
        ),
        github_token_provider=token_provider,
    )

    result = execute(
        execution_context,
        side_effect_id=side_effect_id,
        args_hash=validated_arguments_hash(REAL_ARGUMENTS),
    )

    assert result.success is False
    assert result.result["error_type"] == "approval_not_authorized"
    assert token_provider.calls == 0
    assert real_client.list_calls == []
    assert real_client.post_calls == []


def test_approval_hash_mismatch_blocks_before_token_or_network(
    tmp_path: Path,
) -> None:
    execution_context, side_effect_id, args_hash, token_provider, real_client = (
        approved_context(tmp_path)
    )
    with execution_context.durable_side_effect_ledger.db_manager.get_connection() as conn:
        conn.execute(
            "UPDATE approval_bindings SET validated_arguments_hash = ? WHERE side_effect_id = ?",
            ("wrong_hash", side_effect_id),
        )
        conn.commit()

    result = execute(
        execution_context,
        side_effect_id=side_effect_id,
        args_hash=args_hash,
    )

    assert result.success is False
    assert result.result["error_type"] == "approval_not_authorized"
    assert token_provider.calls == 0
    assert real_client.list_calls == []
    assert real_client.post_calls == []


def test_local_succeeded_suppresses_before_token_or_network(tmp_path: Path) -> None:
    manager, ledger, approval_store = stores(tmp_path / "durable.sqlite")
    side_effect_id = persist_action_with_status(
        ledger,
        approval_store,
        DurableSideEffectStatus.SUCCEEDED,
    )
    token_provider = CountingTokenProvider()
    real_client = FakeRealGitHubClient()
    execution_context = ToolExecutionContext(
        run_id="run-durable-1",
        step_id=GITHUB_COMMENT_STEP_ID,
        durable_side_effect_ledger=ledger,
        durable_approval_binding_store=approval_store,
        real_github_issue_comment_client=real_client,
        github_real_mode_config=GitHubRealModeConfig(
            enabled=True,
            allowed_repositories=("Harry5174/learn-agentic-ai",),
            client_mode="real",
        ),
        github_token_provider=token_provider,
    )

    result = post_real_github_issue_comment(
        tool_name=GITHUB_COMMENT_TOOL_NAME,
        request=GitHubIssueCommentRequest.model_validate(VALID_ARGUMENTS),
        context=execution_context,
        side_effect_id=side_effect_id,
        argument_hash=argument_hash(),
    )

    assert result.success is True
    assert result.result["duplicate_suppressed"] is True
    assert token_provider.calls == 0
    assert real_client.list_calls == []
    assert real_client.post_calls == []


@pytest.mark.parametrize(
    ("comments", "expected_error"),
    [
        (
            [RemoteIssueComment(comment_id="1", body="x", comment_url=None)],
            "marker_absent",
        ),
        (
            [
                RemoteIssueComment(
                    comment_id="1",
                    body="<!-- agent_factory:v1 side_effect_id=wrong args_hash=x -->",
                    comment_url=None,
                )
            ],
            "marker_absent",
        ),
    ],
)
def test_marker_absent_is_the_only_lookup_state_that_posts(
    tmp_path: Path,
    comments: list[RemoteIssueComment],
    expected_error: str,
) -> None:
    execution_context, side_effect_id, args_hash, _, real_client = approved_context(
        tmp_path,
        real_client=FakeRealGitHubClient(comments=comments),
    )

    result = execute(
        execution_context,
        side_effect_id=side_effect_id,
        args_hash=args_hash,
    )

    assert result.success is True
    assert expected_error == "marker_absent"
    assert len(real_client.post_calls) == 1


@pytest.mark.parametrize(
    "comments",
    [
        [
            RemoteIssueComment(
                comment_id="1",
                body="<!-- agent_factory:v1 side_effect_id=TARGET args_hash=wrong -->",
                comment_url=None,
            )
        ],
        [
            RemoteIssueComment(
                comment_id="1",
                body="marker one",
                comment_url=None,
            ),
            RemoteIssueComment(
                comment_id="2",
                body="marker two",
                comment_url=None,
            ),
        ],
    ],
)
def test_marker_unsafe_states_fail_closed(tmp_path: Path, comments) -> None:  # noqa: ANN001
    execution_context, side_effect_id, args_hash, _, real_client = approved_context(
        tmp_path,
        real_client=FakeRealGitHubClient(comments=[]),
    )
    if len(comments) == 1:
        real_client.comments = [
            RemoteIssueComment(
                comment_id="1",
                body=build_remote_idempotency_marker(
                    side_effect_id=side_effect_id,
                    validated_arguments_hash="wrong",
                ),
                comment_url=None,
            )
        ]
    else:
        marker = build_remote_idempotency_marker(
            side_effect_id=side_effect_id,
            validated_arguments_hash=args_hash,
        )
        real_client.comments = [
            RemoteIssueComment(comment_id="1", body=marker, comment_url=None),
            RemoteIssueComment(comment_id="2", body=marker, comment_url=None),
        ]

    result = execute(
        execution_context,
        side_effect_id=side_effect_id,
        args_hash=args_hash,
    )

    assert result.success is False
    assert result.result["error_type"] in {"marker_mismatch", "marker_ambiguous"}
    assert real_client.post_calls == []


def test_lookup_failure_fails_closed(tmp_path: Path) -> None:
    class FailingListClient(FakeRealGitHubClient):
        def list_issue_comments(self, request):  # noqa: ANN001, ANN201
            self.list_calls.append(request)
            raise RemoteIssueCommentListingError("safe fake listing failure")

    execution_context, side_effect_id, args_hash, _, real_client = approved_context(
        tmp_path,
        real_client=FailingListClient(),
    )

    result = execute(
        execution_context,
        side_effect_id=side_effect_id,
        args_hash=args_hash,
    )

    assert result.success is False
    assert result.result["error_type"] == "marker_lookup_failed"
    assert real_client.post_calls == []


def test_real_client_failure_marks_failed_safely(tmp_path: Path) -> None:
    class FailingPostClient(FakeRealGitHubClient):
        def post_issue_comment(self, request):  # noqa: ANN001, ANN201
            self.post_calls.append(request)
            return GitHubIssueCommentFailure(
                repository=request.repository,
                issue_number=request.issue_number,
                error_type="github_http_500",
                message="GitHub issue-comment request failed.",
                retryable=True,
            )

    execution_context, side_effect_id, args_hash, _, real_client = approved_context(
        tmp_path,
        real_client=FailingPostClient(),
    )

    result = execute(
        execution_context,
        side_effect_id=side_effect_id,
        args_hash=args_hash,
    )

    assert result.success is False
    assert result.result["error_type"] == "github_http_500"
    assert len(real_client.post_calls) == 1
