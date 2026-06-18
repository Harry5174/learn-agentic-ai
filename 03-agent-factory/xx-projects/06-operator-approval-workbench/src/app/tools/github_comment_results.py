from typing import Any

from app.github.schemas import GitHubIssueCommentRequest
from app.side_effects.durable_schemas import DurableSideEffectStatus
from app.tools.schemas import ToolExecutionResult


def durable_result(
    *,
    tool_name: str,
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
    remote_reconciled: bool = False,
    cached_external_result: dict[str, Any] | None = None,
    cached_failure: dict[str, Any] | None = None,
    failure_message: str | None = None,
    mode: str = "fake_client",
    dry_run: bool = True,
) -> ToolExecutionResult:
    result: dict[str, Any] = {
        "mode": mode,
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
        "remote_reconciled": remote_reconciled,
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
        tool_name=tool_name,
        success=success,
        dry_run=dry_run,
        result=result,
        message=message,
    )


def failed_result(
    *,
    tool_name: str,
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
        tool_name=tool_name,
        success=False,
        dry_run=True,
        result=result,
        message=message,
    )
