import json
from typing import Any

from pydantic import ValidationError

from app.github.schemas import (
    GitHubIssueCommentFailure,
    GitHubIssueCommentRequest,
    GitHubIssueCommentResult,
)
from app.side_effects.idempotency import (
    build_side_effect_id,
    validated_arguments_hash,
)
from app.side_effects.approval_schemas import ApprovalNotAuthorizedError
from app.side_effects.durable_schemas import (
    DurableSideEffectStatus,
    InvalidSideEffectTransitionError,
    SideEffectRecordNotFoundError,
    TerminalSideEffectStateError,
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
        return _failed_result(
            message="GitHub comment execution requires graph-owned context.",
            error_type="missing_execution_context",
            client_called=False,
        )

    if context.github_issue_comment_client is None:
        return _failed_result(
            message="GitHub comment execution requires a configured fake client.",
            error_type="missing_github_comment_client",
            client_called=False,
        )

    try:
        request = GitHubIssueCommentRequest.model_validate(arguments)
        argument_hash = validated_arguments_hash(request.model_dump())
    except (TypeError, ValidationError) as exc:
        return _failed_result(
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
        return _post_durable_github_issue_comment(
            request=request,
            context=context,
            side_effect_id=side_effect_id,
            argument_hash=argument_hash,
        )

    if context.side_effect_ledger is None:
        return _failed_result(
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


def _post_durable_github_issue_comment(
    *,
    request: GitHubIssueCommentRequest,
    context: ToolExecutionContext,
    side_effect_id: str,
    argument_hash: str,
) -> ToolExecutionResult:
    durable_ledger = context.durable_side_effect_ledger
    approval_store = context.durable_approval_binding_store

    if durable_ledger is None or approval_store is None:
        return _failed_result(
            message=(
                "Durable GitHub comment execution requires both durable "
                "side-effect and approval stores."
            ),
            error_type="missing_durable_execution_dependencies",
            client_called=False,
            extra={
                "side_effect_id": side_effect_id,
                "validated_arguments_hash": argument_hash,
            },
        )

    try:
        record = durable_ledger.get(side_effect_id)
    except SideEffectRecordNotFoundError:
        return _durable_result(
            request=request,
            side_effect_id=side_effect_id,
            argument_hash=argument_hash,
            status=None,
            success=False,
            client_called=False,
            skipped=True,
            ledger_hit=False,
            error_type="side_effect_record_not_found",
            message="Durable side-effect record was not found.",
            replay_outcome="not_found",
        )

    if record.status == DurableSideEffectStatus.SUCCEEDED:
        return _durable_result(
            request=request,
            side_effect_id=side_effect_id,
            argument_hash=argument_hash,
            status=record.status,
            success=True,
            client_called=False,
            skipped=True,
            ledger_hit=True,
            skip_reason="already_succeeded",
            replay_outcome="already_succeeded",
            duplicate_suppressed=True,
            cached_external_result=_json_object_or_none(record.external_result_json),
            message=(
                "Skipped duplicate simulated GitHub comment after durable "
                "success was already recorded."
            ),
        )

    if record.status == DurableSideEffectStatus.EXECUTING:
        return _durable_result(
            request=request,
            side_effect_id=side_effect_id,
            argument_hash=argument_hash,
            status=record.status,
            success=False,
            client_called=False,
            skipped=True,
            ledger_hit=True,
            error_type="side_effect_already_executing",
            skip_reason="unsafe_to_retry",
            replay_outcome="unsafe_to_retry",
            message=(
                "Durable side effect is already executing; automatic replay "
                "is unsafe."
            ),
        )

    if record.status in {
        DurableSideEffectStatus.BLOCKED,
        DurableSideEffectStatus.REJECTED,
        DurableSideEffectStatus.FAILED,
        DurableSideEffectStatus.SKIPPED_DUPLICATE,
    }:
        return _durable_result(
            request=request,
            side_effect_id=side_effect_id,
            argument_hash=argument_hash,
            status=record.status,
            success=False,
            client_called=False,
            skipped=True,
            ledger_hit=True,
            error_type="side_effect_status_not_executable",
            skip_reason=f"side_effect_{record.status.value}",
            replay_outcome=f"{record.status.value}_terminal",
            cached_failure=_json_object_or_none(record.failure_json),
            message=(
                "Durable side-effect status does not allow automatic execution."
            ),
        )

    try:
        approval_store.assert_approved_for_action(side_effect_id, argument_hash)
    except ApprovalNotAuthorizedError as exc:
        return _durable_result(
            request=request,
            side_effect_id=side_effect_id,
            argument_hash=argument_hash,
            status=record.status,
            success=False,
            client_called=False,
            skipped=True,
            ledger_hit=True,
            error_type="approval_not_authorized",
            skip_reason="approval_not_authorized",
            replay_outcome="approval_blocked",
            failure_message=str(exc),
            message="Durable approval binding did not authorize execution.",
        )

    if record.status != DurableSideEffectStatus.APPROVED:
        return _durable_result(
            request=request,
            side_effect_id=side_effect_id,
            argument_hash=argument_hash,
            status=record.status,
            success=False,
            client_called=False,
            skipped=True,
            ledger_hit=True,
            error_type="side_effect_not_approved",
            skip_reason=f"side_effect_{record.status.value}",
            replay_outcome="not_approved",
            approval_checked=True,
            message="Durable side-effect record is not approved for execution.",
        )

    try:
        durable_ledger.mark_executing(side_effect_id)
    except (InvalidSideEffectTransitionError, TerminalSideEffectStateError) as exc:
        refreshed = durable_ledger.get(side_effect_id)
        return _durable_result(
            request=request,
            side_effect_id=side_effect_id,
            argument_hash=argument_hash,
            status=refreshed.status,
            success=False,
            client_called=False,
            skipped=True,
            ledger_hit=True,
            error_type="side_effect_transition_failed",
            skip_reason="mark_executing_failed",
            replay_outcome="transition_blocked",
            approval_checked=True,
            failure_message=str(exc),
            message="Durable side effect could not transition to executing.",
        )

    response = context.github_issue_comment_client.post_issue_comment(request)

    if isinstance(response, GitHubIssueCommentResult):
        external_result = response.model_dump(mode="json")
        durable_ledger.mark_succeeded(
            side_effect_id,
            external_result=external_result,
        )
        return ToolExecutionResult(
            tool_name=GITHUB_COMMENT_TOOL_NAME,
            success=True,
            dry_run=response.dry_run,
            result={
                "mode": "fake_client",
                "persistence": "durable_sqlite",
                "repository": response.repository,
                "issue_number": response.issue_number,
                "comment_id": response.comment_id,
                "comment_url": response.comment_url,
                "status": response.status,
                "side_effect_id": side_effect_id,
                "validated_arguments_hash": argument_hash,
                "side_effect_status": DurableSideEffectStatus.SUCCEEDED.value,
                "ledger_hit": True,
                "ledger_miss": False,
                "approval_checked": True,
                "client_called": True,
                "skipped": False,
                "duplicate_suppressed": False,
                "replay_outcome": "executed",
            },
            message="Simulated GitHub issue comment through durable fake-client path.",
        )

    failure = _safe_failure(response)
    failure_payload = failure.model_dump(mode="json")
    durable_ledger.mark_failed(side_effect_id, failure=failure_payload)

    return ToolExecutionResult(
        tool_name=GITHUB_COMMENT_TOOL_NAME,
        success=False,
        dry_run=True,
        result={
            "mode": "fake_client",
            "persistence": "durable_sqlite",
            "repository": failure.repository,
            "issue_number": failure.issue_number,
            "error_type": failure.error_type,
            "retryable": failure.retryable,
            "side_effect_id": side_effect_id,
            "validated_arguments_hash": argument_hash,
            "side_effect_status": DurableSideEffectStatus.FAILED.value,
            "ledger_hit": True,
            "ledger_miss": False,
            "approval_checked": True,
            "client_called": True,
            "skipped": False,
            "duplicate_suppressed": False,
            "replay_outcome": "failed_terminal",
            "failure": failure_payload,
        },
        message=failure.message,
    )


def _has_durable_dependencies(context: ToolExecutionContext) -> bool:
    return (
        context.durable_side_effect_ledger is not None
        or context.durable_approval_binding_store is not None
    )


def _durable_result(
    *,
    request: GitHubIssueCommentRequest,
    side_effect_id: str,
    argument_hash: str,
    status: DurableSideEffectStatus | None,
    success: bool,
    client_called: bool,
    skipped: bool,
    ledger_hit: bool,
    message: str,
    error_type: str | None = None,
    skip_reason: str | None = None,
    replay_outcome: str | None = None,
    duplicate_suppressed: bool = False,
    approval_checked: bool = False,
    cached_external_result: dict[str, Any] | None = None,
    cached_failure: dict[str, Any] | None = None,
    failure_message: str | None = None,
) -> ToolExecutionResult:
    result: dict[str, Any] = {
        "mode": "fake_client",
        "persistence": "durable_sqlite",
        "repository": request.repository,
        "issue_number": request.issue_number,
        "side_effect_id": side_effect_id,
        "validated_arguments_hash": argument_hash,
        "side_effect_status": None if status is None else status.value,
        "ledger_hit": ledger_hit,
        "ledger_miss": not ledger_hit,
        "approval_checked": approval_checked,
        "client_called": client_called,
        "skipped": skipped,
        "duplicate_suppressed": duplicate_suppressed,
    }

    if error_type is not None:
        result["error_type"] = error_type
    if skip_reason is not None:
        result["skip_reason"] = skip_reason
    if replay_outcome is not None:
        result["replay_outcome"] = replay_outcome
    if cached_external_result is not None:
        result["cached_external_result"] = cached_external_result
    if cached_failure is not None:
        result["cached_failure"] = cached_failure
    if failure_message is not None:
        result["failure_message"] = failure_message

    if error_type == "approval_not_authorized":
        result["approval_checked"] = True

    return ToolExecutionResult(
        tool_name=GITHUB_COMMENT_TOOL_NAME,
        success=success,
        dry_run=True,
        result=result,
        message=message,
    )


def _json_object_or_none(raw_json: str | None) -> dict[str, Any] | None:
    if raw_json is None:
        return None

    value = json.loads(raw_json)
    return value if isinstance(value, dict) else None


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


def _failed_result(
    *,
    message: str,
    error_type: str,
    client_called: bool,
    extra: dict[str, Any] | None = None,
) -> ToolExecutionResult:
    result = {
        "mode": "fake_client",
        "error_type": error_type,
        "client_called": client_called,
        "skipped": True,
    }
    if extra is not None:
        result.update(extra)

    return ToolExecutionResult(
        tool_name=GITHUB_COMMENT_TOOL_NAME,
        success=False,
        dry_run=True,
        result=result,
        message=message,
    )
