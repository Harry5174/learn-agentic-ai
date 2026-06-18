from dataclasses import dataclass
from enum import StrEnum
from typing import Any

from app.audit.durable_schemas import DurableAuditEventType
from app.audit.durable_store import DurableAuditStore
from app.github.remote_comments import (
    IncompleteRemoteIssueCommentListingError,
    RemoteIssueComment,
    RemoteIssueCommentLister,
    RemoteIssueCommentListingError,
)
from app.github.remote_marker import (
    RemoteMarkerMatchStatus,
    find_remote_idempotency_markers,
)
from app.github.schemas import GitHubIssueCommentRequest
from app.side_effects.durable_ledger import DurableSideEffectLedger
from app.side_effects.durable_schemas import (
    DurableSideEffectRecord,
    DurableSideEffectStatus,
    SideEffectRecordNotFoundError,
)
from app.tools.github_comment_results import durable_result
from app.tools.schemas import ToolExecutionResult


class RemoteMarkerLookupStatus(StrEnum):
    """Safe outcomes from fake/mocked remote marker lookup."""

    MARKER_FOUND = "marker_found"
    MARKER_ABSENT = "marker_absent"
    MARKER_MISMATCH = "marker_mismatch"
    MARKER_AMBIGUOUS = "marker_ambiguous"
    MARKER_LOOKUP_FAILED = "marker_lookup_failed"


@dataclass(frozen=True)
class RemoteMarkerLookupResult:
    """Remote marker lookup outcome with safe external evidence only."""

    status: RemoteMarkerLookupStatus
    comment_id: str | None = None
    comment_url: str | None = None
    message: str | None = None


class RemoteMarkerLookupService:
    """Find a target marker through a fake/mocked remote comment lister."""

    def __init__(self, lister: RemoteIssueCommentLister) -> None:
        self.lister = lister

    def lookup(
        self,
        *,
        request: GitHubIssueCommentRequest,
        side_effect_id: str,
        validated_arguments_hash: str,
    ) -> RemoteMarkerLookupResult:
        try:
            comments = self.lister.list_issue_comments(request)
        except IncompleteRemoteIssueCommentListingError:
            return RemoteMarkerLookupResult(
                status=RemoteMarkerLookupStatus.MARKER_LOOKUP_FAILED,
                message="Remote issue-comment listing was incomplete.",
            )
        except RemoteIssueCommentListingError:
            return RemoteMarkerLookupResult(
                status=RemoteMarkerLookupStatus.MARKER_LOOKUP_FAILED,
                message="Remote issue-comment listing failed.",
            )
        except Exception:
            return RemoteMarkerLookupResult(
                status=RemoteMarkerLookupStatus.MARKER_LOOKUP_FAILED,
                message="Remote issue-comment listing failed.",
            )

        exact_matches: list[RemoteIssueComment] = []
        found_relevant_mismatch = False

        for comment in comments:
            marker_matches = find_remote_idempotency_markers(
                comment.body,
                side_effect_id=side_effect_id,
                validated_arguments_hash=validated_arguments_hash,
            )
            for marker_match in marker_matches:
                if marker_match.status == RemoteMarkerMatchStatus.EXACT:
                    exact_matches.append(comment)
                elif marker_match.status in {
                    RemoteMarkerMatchStatus.WRONG_ARGUMENTS_HASH,
                    RemoteMarkerMatchStatus.MALFORMED_RELEVANT,
                }:
                    found_relevant_mismatch = True

        if found_relevant_mismatch:
            return RemoteMarkerLookupResult(
                status=RemoteMarkerLookupStatus.MARKER_MISMATCH,
                message=(
                    "Remote marker uses the same side_effect_id but does not "
                    "prove the expected validated argument hash."
                ),
            )

        if len(exact_matches) > 1:
            return RemoteMarkerLookupResult(
                status=RemoteMarkerLookupStatus.MARKER_AMBIGUOUS,
                message="Multiple exact remote idempotency markers were found.",
            )

        if len(exact_matches) == 1:
            comment = exact_matches[0]
            return RemoteMarkerLookupResult(
                status=RemoteMarkerLookupStatus.MARKER_FOUND,
                comment_id=comment.comment_id,
                comment_url=comment.comment_url,
                message="Exact remote idempotency marker was found.",
            )

        return RemoteMarkerLookupResult(
            status=RemoteMarkerLookupStatus.MARKER_ABSENT,
            message="Exact remote idempotency marker was not found.",
        )


class RemoteReconciliationService:
    """Recover eligible durable local state from a fake/mocked remote marker."""

    ELIGIBLE_STATUSES = {
        DurableSideEffectStatus.APPROVED,
        DurableSideEffectStatus.EXECUTING,
    }

    def __init__(
        self,
        *,
        durable_ledger: DurableSideEffectLedger,
        audit_store: DurableAuditStore | None,
        lookup_service: RemoteMarkerLookupService,
    ) -> None:
        self.durable_ledger = durable_ledger
        self.audit_store = audit_store
        self.lookup_service = lookup_service

    def reconcile(
        self,
        *,
        tool_name: str,
        run_id: str,
        request: GitHubIssueCommentRequest,
        side_effect_id: str,
        validated_arguments_hash: str,
    ) -> ToolExecutionResult:
        try:
            record = self.durable_ledger.get(side_effect_id)
        except SideEffectRecordNotFoundError:
            self._append_audit(
                run_id=run_id,
                side_effect_id=side_effect_id,
                event_type=DurableAuditEventType.EXECUTION_BLOCKED,
                message="Remote reconciliation blocked because local record is absent.",
                metadata={
                    "marker_status": "local_record_absent",
                    "repository": request.repository,
                    "issue_number": request.issue_number,
                    "validated_arguments_hash": validated_arguments_hash,
                    "reconciliation_status": "blocked",
                },
            )
            return _blocked_result(
                tool_name=tool_name,
                request=request,
                side_effect_id=side_effect_id,
                validated_arguments_hash=validated_arguments_hash,
                status=None,
                error_type="side_effect_record_not_found",
                skip_reason="local_record_absent",
                message="Remote reconciliation requires an existing local record.",
            )

        record_mismatch = _record_mismatch(
            record=record,
            request=request,
            tool_name=tool_name,
            validated_arguments_hash=validated_arguments_hash,
        )
        if record_mismatch is not None:
            self._append_audit(
                run_id=run_id,
                side_effect_id=side_effect_id,
                event_type=DurableAuditEventType.EXECUTION_BLOCKED,
                message="Remote reconciliation blocked by local record mismatch.",
                metadata={
                    "marker_status": "local_record_mismatch",
                    "repository": request.repository,
                    "issue_number": request.issue_number,
                    "validated_arguments_hash": validated_arguments_hash,
                    "reconciliation_status": "blocked",
                    "mismatch": record_mismatch,
                },
            )
            return _blocked_result(
                tool_name=tool_name,
                request=request,
                side_effect_id=side_effect_id,
                validated_arguments_hash=validated_arguments_hash,
                status=record.status,
                error_type="local_record_mismatch",
                skip_reason=record_mismatch,
                message="Remote reconciliation local record check failed.",
            )

        if record.status == DurableSideEffectStatus.SUCCEEDED:
            return durable_result(
                tool_name=tool_name,
                request=request,
                side_effect_id=side_effect_id,
                argument_hash=validated_arguments_hash,
                status=record.status,
                success=True,
                client_called=False,
                skipped=True,
                ledger_hit=True,
                skip_reason="already_succeeded",
                replay_outcome="already_succeeded",
                duplicate_suppressed=True,
                cached_external_result=_json_object_or_none(
                    record.external_result_json
                ),
                message="Remote reconciliation skipped; local record already succeeded.",
            )

        if record.status not in self.ELIGIBLE_STATUSES:
            self._append_audit(
                run_id=run_id,
                side_effect_id=side_effect_id,
                event_type=DurableAuditEventType.EXECUTION_BLOCKED,
                message="Remote reconciliation blocked by ineligible local status.",
                metadata={
                    "marker_status": "not_checked",
                    "repository": request.repository,
                    "issue_number": request.issue_number,
                    "validated_arguments_hash": validated_arguments_hash,
                    "side_effect_status": record.status.value,
                    "reconciliation_status": "blocked",
                },
            )
            return _blocked_result(
                tool_name=tool_name,
                request=request,
                side_effect_id=side_effect_id,
                validated_arguments_hash=validated_arguments_hash,
                status=record.status,
                error_type="side_effect_status_not_reconcilable",
                skip_reason=f"side_effect_{record.status.value}",
                message="Remote marker reconciliation does not authorize this state.",
            )

        self._append_audit(
            run_id=run_id,
            side_effect_id=side_effect_id,
            event_type=DurableAuditEventType.REMOTE_MARKER_CHECK_STARTED,
            message="Remote idempotency marker check started.",
            metadata={
                "repository": request.repository,
                "issue_number": request.issue_number,
                "validated_arguments_hash": validated_arguments_hash,
                "side_effect_status": record.status.value,
            },
        )

        lookup = self.lookup_service.lookup(
            request=request,
            side_effect_id=side_effect_id,
            validated_arguments_hash=validated_arguments_hash,
        )
        self._append_lookup_audit(
            run_id=run_id,
            side_effect_id=side_effect_id,
            request=request,
            validated_arguments_hash=validated_arguments_hash,
            lookup=lookup,
        )

        if lookup.status != RemoteMarkerLookupStatus.MARKER_FOUND:
            self._append_audit(
                run_id=run_id,
                side_effect_id=side_effect_id,
                event_type=DurableAuditEventType.EXECUTION_BLOCKED,
                message="Remote reconciliation blocked by marker lookup outcome.",
                metadata={
                    "marker_status": lookup.status.value,
                    "repository": request.repository,
                    "issue_number": request.issue_number,
                    "validated_arguments_hash": validated_arguments_hash,
                    "reconciliation_status": "blocked",
                },
            )
            return _blocked_result(
                tool_name=tool_name,
                request=request,
                side_effect_id=side_effect_id,
                validated_arguments_hash=validated_arguments_hash,
                status=record.status,
                error_type=lookup.status.value,
                skip_reason=lookup.status.value,
                message="Remote marker lookup did not produce a safe reconciliation.",
            )

        external_result = {
            "comment_id": lookup.comment_id,
            "comment_url": lookup.comment_url,
            "remote_reconciled": True,
            "client_called": False,
            "source": "remote_marker",
            "reconciliation_status": "remote_reconciled",
        }
        self.durable_ledger.mark_remote_reconciled(
            side_effect_id,
            external_result=external_result,
        )
        self._append_audit(
            run_id=run_id,
            side_effect_id=side_effect_id,
            event_type=DurableAuditEventType.REMOTE_RECONCILED,
            message="Remote marker reconciled local durable state.",
            metadata={
                "marker_status": lookup.status.value,
                "repository": request.repository,
                "issue_number": request.issue_number,
                "validated_arguments_hash": validated_arguments_hash,
                "comment_id": lookup.comment_id,
                "comment_url": lookup.comment_url,
                "reconciliation_status": "remote_reconciled",
            },
        )
        refreshed = self.durable_ledger.get(side_effect_id)

        return durable_result(
            tool_name=tool_name,
            request=request,
            side_effect_id=side_effect_id,
            argument_hash=validated_arguments_hash,
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
        )

    def _append_lookup_audit(
        self,
        *,
        run_id: str,
        side_effect_id: str,
        request: GitHubIssueCommentRequest,
        validated_arguments_hash: str,
        lookup: RemoteMarkerLookupResult,
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
        }[lookup.status]
        self._append_audit(
            run_id=run_id,
            side_effect_id=side_effect_id,
            event_type=event_type,
            message=f"Remote marker lookup outcome: {lookup.status.value}.",
            metadata={
                "marker_status": lookup.status.value,
                "repository": request.repository,
                "issue_number": request.issue_number,
                "validated_arguments_hash": validated_arguments_hash,
                "comment_id": lookup.comment_id,
                "comment_url": lookup.comment_url,
            },
        )

    def _append_audit(
        self,
        *,
        run_id: str,
        side_effect_id: str,
        event_type: DurableAuditEventType,
        message: str,
        metadata: dict[str, Any],
    ) -> None:
        if self.audit_store is None:
            return

        self.audit_store.append_event(
            run_id=run_id,
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
    validated_arguments_hash: str,
    status: DurableSideEffectStatus | None,
    error_type: str,
    skip_reason: str,
    message: str,
) -> ToolExecutionResult:
    return durable_result(
        tool_name=tool_name,
        request=request,
        side_effect_id=side_effect_id,
        argument_hash=validated_arguments_hash,
        status=status,
        success=False,
        client_called=False,
        skipped=True,
        ledger_hit=status is not None,
        error_type=error_type,
        skip_reason=skip_reason,
        replay_outcome="remote_reconciliation_blocked",
        message=message,
    )


def _record_mismatch(
    *,
    record: DurableSideEffectRecord,
    request: GitHubIssueCommentRequest,
    tool_name: str,
    validated_arguments_hash: str,
) -> str | None:
    if record.validated_arguments_hash != validated_arguments_hash:
        return "validated_arguments_hash"
    if record.repository != request.repository:
        return "repository"
    if record.issue_number != request.issue_number:
        return "issue_number"
    if record.tool_name != tool_name:
        return "tool_name"

    return None


def _json_object_or_none(raw_json: str | None) -> dict[str, Any] | None:
    if raw_json is None:
        return None

    import json

    value = json.loads(raw_json)
    return value if isinstance(value, dict) else None
