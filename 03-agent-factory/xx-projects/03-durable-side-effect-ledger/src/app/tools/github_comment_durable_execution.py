import json
from typing import Any

from app.github.schemas import (
    GitHubIssueCommentFailure,
    GitHubIssueCommentRequest,
    GitHubIssueCommentResult,
)
from app.side_effects.approval_schemas import ApprovalNotAuthorizedError
from app.side_effects.durable_schemas import (
    DurableSideEffectStatus,
    InvalidSideEffectTransitionError,
    SideEffectRecordNotFoundError,
    TerminalSideEffectStateError,
)
from app.tools.context import ToolExecutionContext
from app.tools.github_comment_results import durable_result, failed_result
from app.tools.schemas import ToolExecutionResult


def post_durable_github_issue_comment(
    *,
    tool_name: str,
    request: GitHubIssueCommentRequest,
    context: ToolExecutionContext,
    side_effect_id: str,
    argument_hash: str,
) -> ToolExecutionResult:
    durable_ledger = context.durable_side_effect_ledger
    approval_store = context.durable_approval_binding_store

    if durable_ledger is None or approval_store is None:
        return failed_result(
            tool_name=tool_name,
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
        return durable_result(
            tool_name=tool_name,
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
        return durable_result(
            tool_name=tool_name,
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
        return durable_result(
            tool_name=tool_name,
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
        return durable_result(
            tool_name=tool_name,
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
        return durable_result(
            tool_name=tool_name,
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
        return durable_result(
            tool_name=tool_name,
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
        return durable_result(
            tool_name=tool_name,
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
            tool_name=tool_name,
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
        tool_name=tool_name,
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


def _json_object_or_none(raw_json: str | None) -> dict[str, Any] | None:
    if raw_json is None:
        return None

    value = json.loads(raw_json)
    return value if isinstance(value, dict) else None
