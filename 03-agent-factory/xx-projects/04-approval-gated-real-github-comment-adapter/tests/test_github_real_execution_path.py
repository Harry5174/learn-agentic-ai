import json
from pathlib import Path

from app.audit.durable_schemas import DurableAuditEventType
from app.audit.durable_store import DurableAuditStore
from app.github.real_mode import GitHubRealModeConfig
from app.github.remote_comments import RemoteIssueComment
from app.github.remote_marker import build_remote_idempotency_marker
from app.github.schemas import GitHubIssueCommentRequest, GitHubIssueCommentResult
from app.tools.context import ToolExecutionContext
from app.tools.github_comment import GITHUB_COMMENT_STEP_ID, GITHUB_COMMENT_TOOL_NAME
from app.tools.github_comment_real_execution import post_real_github_issue_comment
from restart_replay_helpers import (
    VALID_ARGUMENTS,
    persist_approved_action,
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


def request() -> GitHubIssueCommentRequest:
    return GitHubIssueCommentRequest.model_validate(REAL_ARGUMENTS)


def context(
    *,
    db_path: Path,
    real_client: FakeRealGitHubClient,
    token_provider: CountingTokenProvider,
) -> tuple[ToolExecutionContext, str, str]:
    manager, ledger, approval_store = stores(db_path)
    audit_store = DurableAuditStore(manager)
    audit_store.initialize()
    side_effect_id, args_hash = persist_approved_action(
        ledger,
        approval_store,
        arguments=REAL_ARGUMENTS,
    )
    return (
        ToolExecutionContext(
            run_id="run-durable-1",
            step_id=GITHUB_COMMENT_STEP_ID,
            durable_side_effect_ledger=ledger,
            durable_approval_binding_store=approval_store,
            durable_audit_store=audit_store,
            real_github_issue_comment_client=real_client,
            github_real_mode_config=GitHubRealModeConfig(
                enabled=True,
                allowed_repositories=(REAL_REPOSITORY,),
                client_mode="real",
            ),
            github_token_provider=token_provider,
        ),
        side_effect_id,
        args_hash,
    )


def test_remote_marker_absent_posts_once_and_persists_comment(
    tmp_path: Path,
) -> None:
    real_client = FakeRealGitHubClient()
    token_provider = CountingTokenProvider()
    execution_context, side_effect_id, args_hash = context(
        db_path=tmp_path / "durable.sqlite",
        real_client=real_client,
        token_provider=token_provider,
    )

    result = post_real_github_issue_comment(
        tool_name=GITHUB_COMMENT_TOOL_NAME,
        request=request(),
        context=execution_context,
        side_effect_id=side_effect_id,
        argument_hash=args_hash,
    )

    record = execution_context.durable_side_effect_ledger.get(side_effect_id)
    external_result = json.loads(record.external_result_json or "{}")
    audit_events = execution_context.durable_audit_store.list_by_side_effect_id(
        side_effect_id
    )

    assert result.success is True
    assert result.dry_run is False
    assert result.result["mode"] == "real_client"
    assert result.result["client_called"] is True
    assert token_provider.calls == 1
    assert len(real_client.list_calls) == 1
    assert len(real_client.post_calls) == 1
    assert build_remote_idempotency_marker(
        side_effect_id=side_effect_id,
        validated_arguments_hash=args_hash,
    ) in real_client.post_calls[0].comment_body
    assert external_result["comment_id"] == "real-comment-1"
    assert DurableAuditEventType.REAL_CLIENT_LIST_COMMENTS_CALLED in {
        event.event_type for event in audit_events
    }
    assert DurableAuditEventType.REAL_CLIENT_CREATE_COMMENT_CALLED in {
        event.event_type for event in audit_events
    }
    assert DurableAuditEventType.EXECUTION_SUCCEEDED in {
        event.event_type for event in audit_events
    }


def test_remote_marker_found_reconciles_and_does_not_post(tmp_path: Path) -> None:
    token_provider = CountingTokenProvider()
    db_path = tmp_path / "durable.sqlite"
    marker_context, side_effect_id, args_hash = context(
        db_path=db_path,
        real_client=FakeRealGitHubClient(),
        token_provider=token_provider,
    )
    marker = build_remote_idempotency_marker(
        side_effect_id=side_effect_id,
        validated_arguments_hash=args_hash,
    )
    real_client = FakeRealGitHubClient(
        comments=[
            RemoteIssueComment(
                comment_id="remote-existing-1",
                comment_url="https://example.invalid/remote-existing-1",
                body=f"Already posted.\n{marker}",
            )
        ]
    )
    marker_context = ToolExecutionContext(
        **{
            **marker_context.__dict__,
            "real_github_issue_comment_client": real_client,
        }
    )

    result = post_real_github_issue_comment(
        tool_name=GITHUB_COMMENT_TOOL_NAME,
        request=request(),
        context=marker_context,
        side_effect_id=side_effect_id,
        argument_hash=args_hash,
    )

    record = marker_context.durable_side_effect_ledger.get(side_effect_id)
    external_result = json.loads(record.external_result_json or "{}")

    assert result.success is True
    assert result.result["remote_reconciled"] is True
    assert len(real_client.list_calls) == 1
    assert real_client.post_calls == []
    assert external_result["comment_id"] == "remote-existing-1"
