import json
from pathlib import Path

from app.audit.durable_schemas import DurableAuditEventType
from app.audit.durable_store import DurableAuditStore
from app.github.real_mode import GitHubRealModeConfig
from app.github.remote_comments import RemoteIssueComment
from app.github.remote_marker import build_remote_idempotency_marker
from app.github.schemas import (
    GitHubIssueCommentFailure,
    GitHubIssueCommentRequest,
    GitHubIssueCommentResult,
)
from app.side_effects.durable_schemas import DurableSideEffectStatus
from app.tools.context import ToolExecutionContext
from app.tools.github_comment import GITHUB_COMMENT_STEP_ID, GITHUB_COMMENT_TOOL_NAME
from app.tools.github_comment_real_execution import post_real_github_issue_comment
from restart_replay_helpers import VALID_ARGUMENTS, persist_approved_action, stores


REAL_REPOSITORY = "Harry5174/artifact-5-github-comment-test"
REAL_ARGUMENTS = {
    **VALID_ARGUMENTS,
    "repository": REAL_REPOSITORY,
}


class CountingTokenProvider:
    def __init__(self, token: str = "secret-token-123") -> None:
        self.token = token
        self.calls = 0

    def get_token(self) -> str:
        self.calls += 1
        return self.token


class SharedRemoteClient:
    def __init__(
        self,
        comments: list[RemoteIssueComment],
        *,
        crash_after_create: bool = False,
        timeout_after_create: bool = False,
    ) -> None:
        self.comments = comments
        self.crash_after_create = crash_after_create
        self.timeout_after_create = timeout_after_create
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
    ) -> GitHubIssueCommentResult | GitHubIssueCommentFailure:
        self.post_calls.append(request)
        self.comments.append(
            RemoteIssueComment(
                comment_id=f"remote-comment-{len(self.comments) + 1}",
                comment_url=f"https://example.invalid/{len(self.comments) + 1}",
                body=request.comment_body,
            )
        )
        if self.crash_after_create:
            raise RuntimeError("simulated process crash after remote create")
        if self.timeout_after_create:
            return GitHubIssueCommentFailure(
                repository=request.repository,
                issue_number=request.issue_number,
                error_type="github_timeout",
                message="GitHub issue-comment request failed.",
                retryable=True,
            )
        return GitHubIssueCommentResult(
            repository=request.repository,
            issue_number=request.issue_number,
            comment_id=self.comments[-1].comment_id,
            comment_url=self.comments[-1].comment_url,
            status="posted",
            dry_run=False,
        )


def request() -> GitHubIssueCommentRequest:
    return GitHubIssueCommentRequest.model_validate(REAL_ARGUMENTS)


def context(
    *,
    db_path: Path,
    client: SharedRemoteClient,
    token_provider: CountingTokenProvider,
) -> ToolExecutionContext:
    manager, ledger, approval_store = stores(db_path)
    audit_store = DurableAuditStore(manager)
    audit_store.initialize()
    return ToolExecutionContext(
        run_id="run-durable-1",
        step_id=GITHUB_COMMENT_STEP_ID,
        durable_side_effect_ledger=ledger,
        durable_approval_binding_store=approval_store,
        durable_audit_store=audit_store,
        real_github_issue_comment_client=client,
        github_real_mode_config=GitHubRealModeConfig(
            enabled=True,
            allowed_repositories=(REAL_REPOSITORY,),
            client_mode="real",
        ),
        github_token_provider=token_provider,
    )


def execute(
    execution_context: ToolExecutionContext,
    *,
    side_effect_id: str,
    args_hash: str,
):
    return post_real_github_issue_comment(
        tool_name=GITHUB_COMMENT_TOOL_NAME,
        request=request(),
        context=execution_context,
        side_effect_id=side_effect_id,
        argument_hash=args_hash,
    )


def test_crash_window_replay_reconciles_executing_record_without_second_create(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "durable.sqlite"
    remote_comments: list[RemoteIssueComment] = []
    setup_context = context(
        db_path=db_path,
        client=SharedRemoteClient(remote_comments),
        token_provider=CountingTokenProvider(),
    )
    side_effect_id, args_hash = persist_approved_action(
        setup_context.durable_side_effect_ledger,
        setup_context.durable_approval_binding_store,
        arguments=REAL_ARGUMENTS,
    )
    crashing_client = SharedRemoteClient(remote_comments, crash_after_create=True)
    first_context = ToolExecutionContext(
        **{**setup_context.__dict__, "real_github_issue_comment_client": crashing_client}
    )

    try:
        execute(first_context, side_effect_id=side_effect_id, args_hash=args_hash)
    except RuntimeError as exc:
        assert str(exc) == "simulated process crash after remote create"

    record_after_crash = first_context.durable_side_effect_ledger.get(side_effect_id)
    assert record_after_crash.status == DurableSideEffectStatus.EXECUTING
    assert len(crashing_client.post_calls) == 1
    assert build_remote_idempotency_marker(
        side_effect_id=side_effect_id,
        validated_arguments_hash=args_hash,
    ) in remote_comments[0].body

    replay_client = SharedRemoteClient(remote_comments)
    replay_context = context(
        db_path=db_path,
        client=replay_client,
        token_provider=CountingTokenProvider(),
    )

    replay_result = execute(
        replay_context,
        side_effect_id=side_effect_id,
        args_hash=args_hash,
    )

    refreshed = replay_context.durable_side_effect_ledger.get(side_effect_id)
    external_result = json.loads(refreshed.external_result_json or "{}")
    event_types = {
        event.event_type
        for event in replay_context.durable_audit_store.list_by_side_effect_id(
            side_effect_id
        )
    }

    assert replay_result.success is True
    assert replay_result.result["remote_reconciled"] is True
    assert replay_result.result["client_called"] is False
    assert replay_client.list_calls
    assert replay_client.post_calls == []
    assert refreshed.status == DurableSideEffectStatus.SUCCEEDED
    assert external_result["comment_id"] == "remote-comment-1"
    assert external_result["comment_url"] == "https://example.invalid/1"
    assert DurableAuditEventType.REMOTE_MARKER_FOUND in event_types
    assert DurableAuditEventType.REMOTE_RECONCILED in event_types


def test_timeout_after_create_stays_executing_then_replay_reconciles_marker(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "durable.sqlite"
    remote_comments: list[RemoteIssueComment] = []
    first_client = SharedRemoteClient(remote_comments, timeout_after_create=True)
    first_context = context(
        db_path=db_path,
        client=first_client,
        token_provider=CountingTokenProvider(),
    )
    side_effect_id, args_hash = persist_approved_action(
        first_context.durable_side_effect_ledger,
        first_context.durable_approval_binding_store,
        arguments=REAL_ARGUMENTS,
    )

    first_result = execute(
        first_context,
        side_effect_id=side_effect_id,
        args_hash=args_hash,
    )
    record_after_timeout = first_context.durable_side_effect_ledger.get(side_effect_id)

    assert first_result.success is False
    assert first_result.result["error_type"] == "github_timeout"
    assert first_result.result["side_effect_status"] == DurableSideEffectStatus.EXECUTING
    assert record_after_timeout.status == DurableSideEffectStatus.EXECUTING
    assert len(first_client.post_calls) == 1

    replay_client = SharedRemoteClient(remote_comments)
    replay_context = context(
        db_path=db_path,
        client=replay_client,
        token_provider=CountingTokenProvider(),
    )

    replay_result = execute(
        replay_context,
        side_effect_id=side_effect_id,
        args_hash=args_hash,
    )

    assert replay_result.success is True
    assert replay_result.result["remote_reconciled"] is True
    assert replay_client.post_calls == []
    assert replay_context.durable_side_effect_ledger.get(
        side_effect_id
    ).status == DurableSideEffectStatus.SUCCEEDED


def test_executing_replay_with_marker_absent_may_post_after_lookup(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "durable.sqlite"
    remote_comments: list[RemoteIssueComment] = []
    first_context = context(
        db_path=db_path,
        client=SharedRemoteClient(remote_comments, timeout_after_create=True),
        token_provider=CountingTokenProvider(),
    )
    side_effect_id, args_hash = persist_approved_action(
        first_context.durable_side_effect_ledger,
        first_context.durable_approval_binding_store,
        arguments=REAL_ARGUMENTS,
    )
    first_context.durable_side_effect_ledger.mark_executing(side_effect_id)

    replay_client = SharedRemoteClient(remote_comments)
    replay_context = context(
        db_path=db_path,
        client=replay_client,
        token_provider=CountingTokenProvider(),
    )

    result = execute(
        replay_context,
        side_effect_id=side_effect_id,
        args_hash=args_hash,
    )

    assert result.success is True
    assert len(replay_client.list_calls) == 1
    assert len(replay_client.post_calls) == 1
    assert replay_context.durable_side_effect_ledger.get(
        side_effect_id
    ).status == DurableSideEffectStatus.SUCCEEDED
