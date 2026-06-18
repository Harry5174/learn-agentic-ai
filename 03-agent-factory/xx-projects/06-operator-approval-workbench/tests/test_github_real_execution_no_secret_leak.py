import json
from pathlib import Path

from app.audit.durable_store import DurableAuditStore
from app.github.real_mode import GitHubRealModeConfig
from app.github.remote_comments import RemoteIssueComment
from app.github.schemas import (
    GitHubIssueCommentFailure,
    GitHubIssueCommentRequest,
    GitHubIssueCommentResult,
)
from app.tools.context import ToolExecutionContext
from app.tools.github_comment import GITHUB_COMMENT_STEP_ID, GITHUB_COMMENT_TOOL_NAME
from app.tools.github_comment_real_execution import post_real_github_issue_comment
from restart_replay_helpers import VALID_ARGUMENTS
from restart_replay_helpers import persist_approved_action, stores


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


class SecretFailingClient(FakeRealGitHubClient):
    def post_issue_comment(self, request):  # noqa: ANN001, ANN201
        self.post_calls.append(request)
        return GitHubIssueCommentFailure(
            repository=request.repository,
            issue_number=request.issue_number,
            error_type="github_http_403",
            message="GitHub issue-comment request failed.",
            retryable=False,
        )


def test_token_and_authorization_do_not_appear_in_results_or_audit(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "durable.sqlite"
    manager, ledger, approval_store = stores(db_path)
    audit_store = DurableAuditStore(manager)
    audit_store.initialize()
    side_effect_id, args_hash = persist_approved_action(
        ledger,
        approval_store,
        arguments=REAL_ARGUMENTS,
    )
    token_provider = CountingTokenProvider("ghp_should_not_leak")
    real_client = SecretFailingClient()
    execution_context = ToolExecutionContext(
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
    )

    result = post_real_github_issue_comment(
        tool_name=GITHUB_COMMENT_TOOL_NAME,
        request=request(),
        context=execution_context,
        side_effect_id=side_effect_id,
        argument_hash=args_hash,
    )

    result_payload = result.model_dump_json()
    audit_payload = json.dumps(
        [
            event.model_dump(mode="json")
            for event in audit_store.list_by_side_effect_id(side_effect_id)
        ],
        sort_keys=True,
    )

    assert "ghp_should_not_leak" not in result_payload
    assert "ghp_should_not_leak" not in audit_payload
    assert "Authorization" not in result_payload
    assert "Authorization" not in audit_payload
    assert "Bearer" not in result_payload
    assert "Bearer" not in audit_payload
