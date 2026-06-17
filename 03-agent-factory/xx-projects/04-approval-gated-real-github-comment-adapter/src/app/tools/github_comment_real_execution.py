import hashlib
import json
from typing import Any

from app.audit.durable_schemas import DurableAuditEventType
from app.github.client import GitHubIssueCommentRemoteClient
from app.github.real_client import RealGitHubIssueCommentClient
from app.github.remote_marker import build_remote_idempotency_marker
from app.github.remote_reconciliation import (
    RemoteMarkerLookupService,
    RemoteMarkerLookupStatus,
)
from app.github.schemas import (
    GitHubIssueCommentFailure,
    GitHubIssueCommentRequest,
    GitHubIssueCommentResult,
)
from app.github.token_provider import MissingGitHubTokenError
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


def post_real_github_issue_comment(
    *,
    tool_name: str,
    request: GitHubIssueCommentRequest,
    context: ToolExecutionContext,
    side_effect_id: str,
    argument_hash: str,
) -> ToolExecutionResult:
    durable_ledger = context.durable_side_effect_ledger
    approval_store = context.durable_approval_binding_store
    config = context.github_real_mode_config

    if durable_ledger is None or approval_store is None:
        return failed_result(
            tool_name=tool_name,
            message="Real GitHub comment execution requires durable stores.",
            error_type="missing_durable_execution_dependencies",
            client_called=False,
            extra={
                "mode": "real_client",
                "side_effect_id": side_effect_id,
                "validated_arguments_hash": argument_hash,
            },
        )

    _append_audit_event(
        context=context,
        side_effect_id=side_effect_id,
        event_type=DurableAuditEventType.EXECUTION_REQUESTED,
        message="Real GitHub issue-comment execution was requested.",
        metadata={
            "repository": request.repository,
            "issue_number": request.issue_number,
            "validated_arguments_hash": argument_hash,
            "mode": "real_client",
        },
    )

    if config is None or not config.enabled or config.client_mode != "real":
        return _blocked_result(
            tool_name=tool_name,
            request=request,
            side_effect_id=side_effect_id,
            argument_hash=argument_hash,
            status=None,
            error_type="real_github_execution_disabled",
            skip_reason="real_mode_disabled",
            message="Real GitHub execution is disabled.",
        )

    if not config.has_valid_exact_repository_allowlist():
        return _blocked_result(
            tool_name=tool_name,
            request=request,
            side_effect_id=side_effect_id,
            argument_hash=argument_hash,
            status=None,
            error_type="invalid_repository_allowlist",
            skip_reason="invalid_repository_allowlist",
            message="Real GitHub repository allowlist is invalid.",
        )

    if not config.repository_is_allowed(request.repository):
        _append_audit_event(
            context=context,
            side_effect_id=side_effect_id,
            event_type=DurableAuditEventType.REPOSITORY_BLOCKED,
            message="Repository is not allowlisted for real GitHub comments.",
            metadata={
                "repository": request.repository,
                "issue_number": request.issue_number,
                "validated_arguments_hash": argument_hash,
                "repository_allowed": False,
            },
        )
        return _blocked_result(
            tool_name=tool_name,
            request=request,
            side_effect_id=side_effect_id,
            argument_hash=argument_hash,
            status=None,
            error_type="repository_not_allowlisted",
            skip_reason="repository_not_allowlisted",
            message="Repository is not allowlisted for real GitHub comments.",
        )

    _append_audit_event(
        context=context,
        side_effect_id=side_effect_id,
        event_type=DurableAuditEventType.REPOSITORY_ALLOWED,
        message="Repository is allowlisted for real GitHub comments.",
        metadata={
            "repository": request.repository,
            "issue_number": request.issue_number,
            "validated_arguments_hash": argument_hash,
            "repository_allowed": True,
        },
    )

    try:
        record = durable_ledger.get(side_effect_id)
    except SideEffectRecordNotFoundError:
        return _blocked_result(
            tool_name=tool_name,
            request=request,
            side_effect_id=side_effect_id,
            argument_hash=argument_hash,
            status=None,
            error_type="side_effect_record_not_found",
            skip_reason="local_record_absent",
            message="Real GitHub execution requires an existing durable record.",
        )

    if record.status == DurableSideEffectStatus.SUCCEEDED:
        _append_audit_event(
            context=context,
            side_effect_id=side_effect_id,
            event_type=DurableAuditEventType.DUPLICATE_SUPPRESSED,
            message="Local durable success suppressed real GitHub execution.",
            metadata={
                "repository": request.repository,
                "issue_number": request.issue_number,
                "validated_arguments_hash": argument_hash,
                "side_effect_status": record.status.value,
                "replay_outcome": "already_succeeded",
            },
        )
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
            message="Skipped real GitHub execution after local durable success.",
            mode="real_client",
            dry_run=False,
        )

    record_mismatch = _record_mismatch(
        request=request,
        record_repository=record.repository,
        record_issue_number=record.issue_number,
        record_tool_name=record.tool_name,
        tool_name=tool_name,
        record_hash=record.validated_arguments_hash,
        record_comment_body_hash=record.comment_body_hash,
        argument_hash=argument_hash,
    )
    if record_mismatch is not None:
        return _blocked_result(
            tool_name=tool_name,
            request=request,
            side_effect_id=side_effect_id,
            argument_hash=argument_hash,
            status=record.status,
            error_type="local_record_mismatch",
            skip_reason=record_mismatch,
            message="Local durable record did not match the requested action.",
        )

    if record.status in {
        DurableSideEffectStatus.BLOCKED,
        DurableSideEffectStatus.REJECTED,
        DurableSideEffectStatus.FAILED,
        DurableSideEffectStatus.SKIPPED_DUPLICATE,
    }:
        return _blocked_result(
            tool_name=tool_name,
            request=request,
            side_effect_id=side_effect_id,
            argument_hash=argument_hash,
            status=record.status,
            error_type="side_effect_status_not_executable",
            skip_reason=f"side_effect_{record.status.value}",
            message="Durable side-effect status does not allow real execution.",
        )

    try:
        approval_store.assert_approved_for_action(side_effect_id, argument_hash)
    except ApprovalNotAuthorizedError:
        _append_audit_event(
            context=context,
            side_effect_id=side_effect_id,
            event_type=DurableAuditEventType.EXECUTION_BLOCKED,
            message="Durable approval binding did not authorize real execution.",
            metadata={
                "repository": request.repository,
                "issue_number": request.issue_number,
                "validated_arguments_hash": argument_hash,
                "side_effect_status": record.status.value,
                "replay_outcome": "approval_blocked",
            },
        )
        return _blocked_result(
            tool_name=tool_name,
            request=request,
            side_effect_id=side_effect_id,
            argument_hash=argument_hash,
            status=record.status,
            error_type="approval_not_authorized",
            skip_reason="approval_not_authorized",
            message="Durable approval binding did not authorize real execution.",
            approval_checked=True,
        )

    _append_audit_event(
        context=context,
        side_effect_id=side_effect_id,
        event_type=DurableAuditEventType.APPROVAL_AUTHORIZED,
        message="Durable approval binding authorized real execution.",
        metadata={
            "repository": request.repository,
            "issue_number": request.issue_number,
            "validated_arguments_hash": argument_hash,
            "side_effect_status": record.status.value,
        },
    )

    token_provider = context.github_token_provider
    if token_provider is None:
        return _blocked_result(
            tool_name=tool_name,
            request=request,
            side_effect_id=side_effect_id,
            argument_hash=argument_hash,
            status=record.status,
            error_type="missing_github_token_provider",
            skip_reason="missing_github_token_provider",
            message="GitHub credentials are unavailable.",
            approval_checked=True,
        )

    try:
        token = token_provider.get_token()
    except MissingGitHubTokenError:
        return _blocked_result(
            tool_name=tool_name,
            request=request,
            side_effect_id=side_effect_id,
            argument_hash=argument_hash,
            status=record.status,
            error_type="missing_github_token",
            skip_reason="missing_github_token",
            message="GitHub credentials are unavailable.",
            approval_checked=True,
        )

    real_client = _real_client(context, token)
    lookup_service = RemoteMarkerLookupService(real_client)

    _append_audit_event(
        context=context,
        side_effect_id=side_effect_id,
        event_type=DurableAuditEventType.REMOTE_MARKER_CHECK_STARTED,
        message="Remote marker lookup started before real GitHub posting.",
        metadata={
            "repository": request.repository,
            "issue_number": request.issue_number,
            "validated_arguments_hash": argument_hash,
        },
    )
    _append_audit_event(
        context=context,
        side_effect_id=side_effect_id,
        event_type=DurableAuditEventType.REAL_CLIENT_LIST_COMMENTS_CALLED,
        message="Real GitHub issue-comment listing was invoked.",
        metadata={
            "repository": request.repository,
            "issue_number": request.issue_number,
            "validated_arguments_hash": argument_hash,
        },
    )
    lookup = lookup_service.lookup(
        request=request,
        side_effect_id=side_effect_id,
        validated_arguments_hash=argument_hash,
    )
    _append_lookup_audit(
        context=context,
        side_effect_id=side_effect_id,
        request=request,
        argument_hash=argument_hash,
        lookup_status=lookup.status,
        comment_id=lookup.comment_id,
        comment_url=lookup.comment_url,
    )

    if lookup.status == RemoteMarkerLookupStatus.MARKER_FOUND:
        external_result = {
            "comment_id": lookup.comment_id,
            "comment_url": lookup.comment_url,
            "remote_reconciled": True,
            "client_called": False,
            "source": "remote_marker",
            "reconciliation_status": "remote_reconciled",
        }
        durable_ledger.mark_remote_reconciled(
            side_effect_id,
            external_result=external_result,
        )
        _append_audit_event(
            context=context,
            side_effect_id=side_effect_id,
            event_type=DurableAuditEventType.REMOTE_RECONCILED,
            message="Remote marker reconciled local durable state.",
            metadata={
                "repository": request.repository,
                "issue_number": request.issue_number,
                "validated_arguments_hash": argument_hash,
                "comment_id": lookup.comment_id,
                "comment_url": lookup.comment_url,
                "reconciliation_status": "remote_reconciled",
            },
        )
        refreshed = durable_ledger.get(side_effect_id)
        return durable_result(
            tool_name=tool_name,
            request=request,
            side_effect_id=side_effect_id,
            argument_hash=argument_hash,
            status=refreshed.status,
            success=True,
            client_called=False,
            skipped=True,
            ledger_hit=True,
            skip_reason="remote_marker_found",
            replay_outcome="remote_reconciled",
            remote_reconciled=True,
            cached_external_result=_json_object_or_none(
                refreshed.external_result_json
            ),
            message="Remote marker reconciled local durable state without posting.",
            mode="real_client",
            dry_run=False,
        )

    if lookup.status != RemoteMarkerLookupStatus.MARKER_ABSENT:
        return _blocked_result(
            tool_name=tool_name,
            request=request,
            side_effect_id=side_effect_id,
            argument_hash=argument_hash,
            status=record.status,
            error_type=lookup.status.value,
            skip_reason=lookup.status.value,
            message="Remote marker lookup did not allow real GitHub posting.",
            approval_checked=True,
        )

    marked_request = _request_with_marker(
        request=request,
        side_effect_id=side_effect_id,
        argument_hash=argument_hash,
    )

    if record.status != DurableSideEffectStatus.EXECUTING:
        try:
            durable_ledger.mark_executing(side_effect_id)
        except (InvalidSideEffectTransitionError, TerminalSideEffectStateError):
            refreshed = durable_ledger.get(side_effect_id)
            return _blocked_result(
                tool_name=tool_name,
                request=request,
                side_effect_id=side_effect_id,
                argument_hash=argument_hash,
                status=refreshed.status,
                error_type="side_effect_transition_failed",
                skip_reason="mark_executing_failed",
                message="Durable side effect could not transition to executing.",
                approval_checked=True,
            )

    _append_audit_event(
        context=context,
        side_effect_id=side_effect_id,
        event_type=DurableAuditEventType.REAL_CLIENT_CREATE_COMMENT_CALLED,
        message="Real GitHub issue-comment creation was invoked.",
        metadata={
            "repository": request.repository,
            "issue_number": request.issue_number,
            "validated_arguments_hash": argument_hash,
        },
    )
    response = real_client.post_issue_comment(marked_request)
    if isinstance(response, GitHubIssueCommentResult):
        external_result = response.model_dump(mode="json")
        durable_ledger.mark_succeeded(
            side_effect_id,
            external_result=external_result,
        )
        _append_audit_event(
            context=context,
            side_effect_id=side_effect_id,
            event_type=DurableAuditEventType.EXECUTION_SUCCEEDED,
            message="Real GitHub issue-comment execution succeeded.",
            metadata={
                "repository": response.repository,
                "issue_number": response.issue_number,
                "validated_arguments_hash": argument_hash,
                "comment_id": response.comment_id,
                "comment_url": response.comment_url,
                "side_effect_status": DurableSideEffectStatus.SUCCEEDED.value,
            },
        )
        return ToolExecutionResult(
            tool_name=tool_name,
            success=True,
            dry_run=False,
            result={
                "mode": "real_client",
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
                "remote_reconciled": False,
                "replay_outcome": "executed",
            },
            message="Posted one real GitHub issue comment through the approved path.",
        )

    failure = _safe_failure(response, request)
    failure_payload = failure.model_dump(mode="json")
    if failure.error_type == "github_timeout":
        _append_audit_event(
            context=context,
            side_effect_id=side_effect_id,
            event_type=DurableAuditEventType.EXECUTION_FAILED,
            message="Real GitHub issue-comment execution outcome was ambiguous.",
            metadata={
                "repository": failure.repository,
                "issue_number": failure.issue_number,
                "validated_arguments_hash": argument_hash,
                "error_type": _audit_safe_error_type(failure.error_type),
                "retryable": failure.retryable,
                "side_effect_status": DurableSideEffectStatus.EXECUTING.value,
                "replay_required": True,
            },
        )
        return ToolExecutionResult(
            tool_name=tool_name,
            success=False,
            dry_run=False,
            result={
                "mode": "real_client",
                "persistence": "durable_sqlite",
                "repository": failure.repository,
                "issue_number": failure.issue_number,
                "error_type": failure.error_type,
                "retryable": failure.retryable,
                "side_effect_id": side_effect_id,
                "validated_arguments_hash": argument_hash,
                "side_effect_status": DurableSideEffectStatus.EXECUTING.value,
                "ledger_hit": True,
                "ledger_miss": False,
                "approval_checked": True,
                "client_called": True,
                "skipped": False,
                "duplicate_suppressed": False,
                "remote_reconciled": False,
                "replay_outcome": "ambiguous_create_outcome",
                "failure": failure_payload,
            },
            message=failure.message,
        )

    durable_ledger.mark_failed(side_effect_id, failure=failure_payload)
    _append_audit_event(
        context=context,
        side_effect_id=side_effect_id,
        event_type=DurableAuditEventType.EXECUTION_FAILED,
        message="Real GitHub issue-comment execution failed.",
        metadata={
            "repository": failure.repository,
            "issue_number": failure.issue_number,
            "validated_arguments_hash": argument_hash,
            "error_type": _audit_safe_error_type(failure.error_type),
            "retryable": failure.retryable,
        },
    )
    return ToolExecutionResult(
        tool_name=tool_name,
        success=False,
        dry_run=False,
        result={
            "mode": "real_client",
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
            "remote_reconciled": False,
            "replay_outcome": "failed_terminal",
            "failure": failure_payload,
        },
        message=failure.message,
    )


def _real_client(
    context: ToolExecutionContext,
    token: str,
) -> GitHubIssueCommentRemoteClient:
    if context.real_github_issue_comment_client is not None:
        return context.real_github_issue_comment_client

    return RealGitHubIssueCommentClient(token=token)


def _request_with_marker(
    *,
    request: GitHubIssueCommentRequest,
    side_effect_id: str,
    argument_hash: str,
) -> GitHubIssueCommentRequest:
    marker = build_remote_idempotency_marker(
        side_effect_id=side_effect_id,
        validated_arguments_hash=argument_hash,
    )
    return GitHubIssueCommentRequest(
        repository=request.repository,
        issue_number=request.issue_number,
        comment_body=f"{request.comment_body}\n\n{marker}",
    )


def _append_lookup_audit(
    *,
    context: ToolExecutionContext,
    side_effect_id: str,
    request: GitHubIssueCommentRequest,
    argument_hash: str,
    lookup_status: RemoteMarkerLookupStatus,
    comment_id: str | None,
    comment_url: str | None,
) -> None:
    event_type = {
        RemoteMarkerLookupStatus.MARKER_FOUND: (
            DurableAuditEventType.REMOTE_MARKER_FOUND
        ),
        RemoteMarkerLookupStatus.MARKER_ABSENT: (
            DurableAuditEventType.REMOTE_MARKER_NOT_FOUND
        ),
        RemoteMarkerLookupStatus.MARKER_AMBIGUOUS: (
            DurableAuditEventType.REMOTE_MARKER_AMBIGUOUS
        ),
        RemoteMarkerLookupStatus.MARKER_MISMATCH: (
            DurableAuditEventType.REMOTE_MARKER_MISMATCH
        ),
        RemoteMarkerLookupStatus.MARKER_LOOKUP_FAILED: (
            DurableAuditEventType.REMOTE_MARKER_LOOKUP_FAILED
        ),
    }[lookup_status]
    _append_audit_event(
        context=context,
        side_effect_id=side_effect_id,
        event_type=event_type,
        message=f"Remote marker lookup outcome: {lookup_status.value}.",
        metadata={
            "repository": request.repository,
            "issue_number": request.issue_number,
            "validated_arguments_hash": argument_hash,
            "marker_status": lookup_status.value,
            "comment_id": comment_id,
            "comment_url": comment_url,
        },
    )


def _append_audit_event(
    *,
    context: ToolExecutionContext,
    side_effect_id: str,
    event_type: DurableAuditEventType,
    message: str,
    metadata: dict[str, Any],
) -> None:
    audit_store = context.durable_audit_store
    if audit_store is None:
        return

    audit_store.append_event(
        run_id=context.run_id,
        side_effect_id=side_effect_id,
        event_type=event_type,
        message=message,
        metadata=metadata,
    )


def _blocked_result(
    *,
    tool_name: str,
    request: GitHubIssueCommentRequest,
    side_effect_id: str,
    argument_hash: str,
    status: DurableSideEffectStatus | None,
    error_type: str,
    skip_reason: str,
    message: str,
    approval_checked: bool = False,
) -> ToolExecutionResult:
    return durable_result(
        tool_name=tool_name,
        request=request,
        side_effect_id=side_effect_id,
        argument_hash=argument_hash,
        status=status,
        success=False,
        client_called=False,
        skipped=True,
        ledger_hit=status is not None,
        error_type=error_type,
        skip_reason=skip_reason,
        replay_outcome="real_execution_blocked",
        approval_checked=approval_checked,
        message=message,
        mode="real_client",
        dry_run=False,
    )


def _record_mismatch(
    *,
    request: GitHubIssueCommentRequest,
    record_repository: str | None,
    record_issue_number: int | None,
    record_tool_name: str,
    tool_name: str,
    record_hash: str,
    record_comment_body_hash: str | None,
    argument_hash: str,
) -> str | None:
    if record_hash != argument_hash:
        return "validated_arguments_hash"
    if record_comment_body_hash != _comment_body_hash(request.comment_body):
        return "comment_body_hash"
    if record_repository != request.repository:
        return "repository"
    if record_issue_number != request.issue_number:
        return "issue_number"
    if record_tool_name != tool_name:
        return "tool_name"
    return None


def _safe_failure(
    response: object,
    request: GitHubIssueCommentRequest,
) -> GitHubIssueCommentFailure:
    if isinstance(response, GitHubIssueCommentFailure):
        return GitHubIssueCommentFailure(
            repository=response.repository,
            issue_number=response.issue_number,
            error_type=response.error_type,
            message=_safe_failure_message(response.message),
            retryable=response.retryable,
        )

    return GitHubIssueCommentFailure(
        repository=request.repository,
        issue_number=request.issue_number,
        error_type="invalid_github_client_response",
        message="GitHub issue-comment client returned an invalid response.",
        retryable=False,
    )


def _comment_body_hash(comment_body: str) -> str:
    return hashlib.sha256(comment_body.encode("utf-8")).hexdigest()


def _safe_failure_message(message: str) -> str:
    unsafe_markers = (
        "authorization",
        "bearer ",
        "ghp_",
        "github_pat_",
        "secret-token",
    )
    if any(marker in message.lower() for marker in unsafe_markers):
        return "GitHub issue-comment request failed."
    return message


def _audit_safe_error_type(error_type: str) -> str:
    if "transport" in error_type.lower():
        return "github_request_failed"
    return error_type


def _json_object_or_none(raw_json: str | None) -> dict[str, Any] | None:
    if raw_json is None:
        return None

    value = json.loads(raw_json)
    return value if isinstance(value, dict) else None
