from typing import Any

from pydantic import ValidationError

from app.github.schemas import (
    GitHubIssueCommentFailure,
    GitHubIssueCommentRequest,
    GitHubIssueCommentResult,
)
from app.tools.github_comment_durable_execution import (
    post_durable_github_issue_comment,
)
from app.tools.github_comment_results import failed_result
from app.side_effects.idempotency import (
    build_side_effect_id,
    validated_arguments_hash,
)
from app.side_effects.schemas import SideEffectStatus
from app.tools.context import ToolExecutionContext
from app.tools.schemas import ToolExecutionResult


GITHUB_COMMENT_SKILL_ID = "post_github_issue_comment"
GITHUB_COMMENT_STEP_ID = "post_comment"
GITHUB_COMMENT_TOOL_NAME = "post_github_issue_comment"
GITHUB_COMMENT_REQUIRED_SCOPE = "tools:post_github_comment"
DEFAULT_ALLOWED_GITHUB_COMMENT_REPOSITORIES = ("Harry5174/learn-agentic-ai",)


def repository_is_allowed(
    repository: str,
    allowed_repositories: tuple[str, ...] = DEFAULT_ALLOWED_GITHUB_COMMENT_REPOSITORIES,
) -> bool:
    """Return whether a repository is trusted for local/demo GitHub comments."""

    return repository in allowed_repositories


def post_github_issue_comment(
    arguments: dict[str, Any],
    context: ToolExecutionContext | None = None,
) -> ToolExecutionResult:
    """Simulate an approval-gated GitHub issue comment through the fake client."""

    if context is None:
        return failed_result(
            tool_name=GITHUB_COMMENT_TOOL_NAME,
            message="GitHub comment execution requires graph-owned context.",
            error_type="missing_execution_context",
            client_called=False,
        )

    if context.github_issue_comment_client is None:
        return failed_result(
            tool_name=GITHUB_COMMENT_TOOL_NAME,
            message="GitHub comment execution requires a configured fake client.",
            error_type="missing_github_comment_client",
            client_called=False,
        )

    try:
        request = GitHubIssueCommentRequest.model_validate(arguments)
        argument_hash = validated_arguments_hash(request.model_dump())
    except (TypeError, ValidationError) as exc:
        return failed_result(
            tool_name=GITHUB_COMMENT_TOOL_NAME,
            message="GitHub comment arguments failed final execution validation.",
            error_type="invalid_validated_arguments",
            client_called=False,
            extra={"failure_message": str(exc)},
        )

    side_effect_id = build_side_effect_id(
        skill_run_id=context.run_id,
        step_id=context.step_id,
        tool_name=GITHUB_COMMENT_TOOL_NAME,
        validated_arguments_hash=argument_hash,
    )

    if _has_durable_dependencies(context):
        return post_durable_github_issue_comment(
            tool_name=GITHUB_COMMENT_TOOL_NAME,
            request=request,
            context=context,
            side_effect_id=side_effect_id,
            argument_hash=argument_hash,
        )

    if context.side_effect_ledger is None:
        return failed_result(
            tool_name=GITHUB_COMMENT_TOOL_NAME,
            message="GitHub comment execution requires a side-effect ledger.",
            error_type="missing_side_effect_ledger",
            client_called=False,
        )

    existing_record = context.side_effect_ledger.get(side_effect_id)

    if existing_record is not None and existing_record.status == SideEffectStatus.SUCCEEDED:
        return ToolExecutionResult(
            tool_name=GITHUB_COMMENT_TOOL_NAME,
            success=True,
            dry_run=True,
            result={
                "mode": "fake_client",
                "repository": request.repository,
                "issue_number": request.issue_number,
                "side_effect_id": side_effect_id,
                "validated_arguments_hash": argument_hash,
                "side_effect_status": existing_record.status.value,
                "ledger_hit": True,
                "ledger_miss": False,
                "client_called": False,
                "skipped": True,
                "skip_reason": "side_effect_already_succeeded",
                "cached_external_result": existing_record.external_result,
            },
            message="Skipped duplicate simulated GitHub comment after ledger hit.",
        )

    context.side_effect_ledger.record_started(
        side_effect_id=side_effect_id,
        skill_run_id=context.run_id,
        step_id=context.step_id,
        tool_name=GITHUB_COMMENT_TOOL_NAME,
        validated_arguments_hash=argument_hash,
    )
    response = context.github_issue_comment_client.post_issue_comment(request)

    if isinstance(response, GitHubIssueCommentResult):
        context.side_effect_ledger.record_succeeded(
            side_effect_id,
            external_result=response.model_dump(mode="json"),
        )
        return ToolExecutionResult(
            tool_name=GITHUB_COMMENT_TOOL_NAME,
            success=True,
            dry_run=response.dry_run,
            result={
                "mode": "fake_client",
                "repository": response.repository,
                "issue_number": response.issue_number,
                "comment_id": response.comment_id,
                "comment_url": response.comment_url,
                "status": response.status,
                "side_effect_id": side_effect_id,
                "validated_arguments_hash": argument_hash,
                "side_effect_status": SideEffectStatus.SUCCEEDED.value,
                "ledger_hit": False,
                "ledger_miss": True,
                "client_called": True,
                "skipped": False,
            },
            message="Simulated GitHub issue comment through fake client.",
        )

    failure = _safe_failure(response)
    context.side_effect_ledger.record_failed(
        side_effect_id,
        failure=failure.model_dump(mode="json"),
    )

    return ToolExecutionResult(
        tool_name=GITHUB_COMMENT_TOOL_NAME,
        success=False,
        dry_run=True,
        result={
            "mode": "fake_client",
            "repository": failure.repository,
            "issue_number": failure.issue_number,
            "error_type": failure.error_type,
            "retryable": failure.retryable,
            "side_effect_id": side_effect_id,
            "validated_arguments_hash": argument_hash,
            "side_effect_status": SideEffectStatus.FAILED.value,
            "ledger_hit": False,
            "ledger_miss": True,
            "client_called": True,
            "skipped": False,
        },
        message=failure.message,
    )


def _has_durable_dependencies(context: ToolExecutionContext) -> bool:
    return (
        context.durable_side_effect_ledger is not None
        or context.durable_approval_binding_store is not None
    )


def _safe_failure(response: object) -> GitHubIssueCommentFailure:
    if isinstance(response, GitHubIssueCommentFailure):
        return response

    return GitHubIssueCommentFailure(
        repository="unknown",
        issue_number=1,
        error_type="invalid_github_client_response",
        message="GitHub issue-comment client returned an invalid response.",
        retryable=False,
    )
