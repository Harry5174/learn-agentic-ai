import json
from pathlib import Path

from app.audit.durable_schemas import DurableAuditEventType
from app.audit.durable_store import DurableAuditStore
from app.github.fake_client import FakeGitHubIssueCommentClient
from app.github.remote_comments import (
    FakeRemoteIssueCommentLister,
    RemoteIssueComment,
)
from app.github.remote_marker import build_remote_idempotency_marker
from app.github.remote_reconciliation import (
    RemoteMarkerLookupService,
    RemoteMarkerLookupStatus,
    RemoteReconciliationService,
)
from app.github.schemas import GitHubIssueCommentRequest
from app.side_effects.durable_schemas import DurableSideEffectStatus
from app.tools.github_comment import GITHUB_COMMENT_TOOL_NAME
from restart_replay_helpers import (
    VALID_ARGUMENTS,
    argument_hash,
    persist_action_with_status,
    persist_approved_action,
    persist_planned_action,
    stores,
)


def request() -> GitHubIssueCommentRequest:
    return GitHubIssueCommentRequest.model_validate(VALID_ARGUMENTS)


def marker(side_effect_id: str, arguments_hash: str | None = None) -> str:
    return build_remote_idempotency_marker(
        side_effect_id=side_effect_id,
        validated_arguments_hash=arguments_hash or argument_hash(),
    )


def lookup_service(
    comments: list[RemoteIssueComment],
    *,
    should_fail: bool = False,
) -> RemoteMarkerLookupService:
    return RemoteMarkerLookupService(
        FakeRemoteIssueCommentLister(
            comments=comments,
            should_fail=should_fail,
        )
    )


def reconciliation_service(
    *,
    db_path: Path,
    comments: list[RemoteIssueComment],
) -> tuple[RemoteReconciliationService, FakeGitHubIssueCommentClient]:
    manager, ledger, _ = stores(db_path)
    audit_store = DurableAuditStore(manager)
    audit_store.initialize()
    fake_post_client = FakeGitHubIssueCommentClient()
    service = RemoteReconciliationService(
        durable_ledger=ledger,
        audit_store=audit_store,
        lookup_service=lookup_service(comments),
    )
    return service, fake_post_client


def remote_comment(body: str, comment_id: str = "remote-comment-1") -> RemoteIssueComment:
    return RemoteIssueComment(
        comment_id=comment_id,
        comment_url=f"https://example.invalid/issuecomment/{comment_id}",
        body=body,
    )


def test_exact_marker_match_returns_marker_found() -> None:
    side_effect_id = "side-effect-lookup"
    result = lookup_service(
        [remote_comment(f"Body\n{marker(side_effect_id)}")]
    ).lookup(
        request=request(),
        side_effect_id=side_effect_id,
        validated_arguments_hash=argument_hash(),
    )

    assert result.status == RemoteMarkerLookupStatus.MARKER_FOUND
    assert result.comment_id == "remote-comment-1"


def test_marker_absent_returns_marker_absent() -> None:
    result = lookup_service([remote_comment("No marker here.")]).lookup(
        request=request(),
        side_effect_id="side-effect-absent",
        validated_arguments_hash=argument_hash(),
    )

    assert result.status == RemoteMarkerLookupStatus.MARKER_ABSENT


def test_wrong_side_effect_id_does_not_match() -> None:
    result = lookup_service(
        [remote_comment(marker("other-side-effect"))]
    ).lookup(
        request=request(),
        side_effect_id="target-side-effect",
        validated_arguments_hash=argument_hash(),
    )

    assert result.status == RemoteMarkerLookupStatus.MARKER_ABSENT


def test_same_side_effect_id_with_wrong_hash_fails_closed() -> None:
    side_effect_id = "side-effect-mismatch"
    result = lookup_service(
        [remote_comment(marker(side_effect_id, "wrong-hash"))]
    ).lookup(
        request=request(),
        side_effect_id=side_effect_id,
        validated_arguments_hash=argument_hash(),
    )

    assert result.status == RemoteMarkerLookupStatus.MARKER_MISMATCH


def test_malformed_relevant_marker_fails_closed() -> None:
    side_effect_id = "side-effect-malformed"
    result = lookup_service(
        [
            remote_comment(
                f"<!-- agent_factory:v1 side_effect_id={side_effect_id} -->"
            )
        ]
    ).lookup(
        request=request(),
        side_effect_id=side_effect_id,
        validated_arguments_hash=argument_hash(),
    )

    assert result.status == RemoteMarkerLookupStatus.MARKER_MISMATCH


def test_multiple_exact_markers_are_ambiguous() -> None:
    side_effect_id = "side-effect-ambiguous"
    result = lookup_service(
        [
            remote_comment(marker(side_effect_id), "remote-comment-1"),
            remote_comment(marker(side_effect_id), "remote-comment-2"),
        ]
    ).lookup(
        request=request(),
        side_effect_id=side_effect_id,
        validated_arguments_hash=argument_hash(),
    )

    assert result.status == RemoteMarkerLookupStatus.MARKER_AMBIGUOUS


def test_remote_list_comments_failure_fails_closed() -> None:
    result = lookup_service([], should_fail=True).lookup(
        request=request(),
        side_effect_id="side-effect-failing-list",
        validated_arguments_hash=argument_hash(),
    )

    assert result.status == RemoteMarkerLookupStatus.MARKER_LOOKUP_FAILED


def test_crash_window_reconciles_remote_marker_without_posting(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "durable.sqlite"
    _, ledger_1, approval_store_1 = stores(db_path)
    side_effect_id, arguments_hash = persist_approved_action(
        ledger_1,
        approval_store_1,
    )
    service, fake_post_client = reconciliation_service(
        db_path=db_path,
        comments=[remote_comment(f"Recovered body.\n{marker(side_effect_id)}")],
    )

    result = service.reconcile(
        tool_name=GITHUB_COMMENT_TOOL_NAME,
        run_id="run-durable-1",
        request=request(),
        side_effect_id=side_effect_id,
        validated_arguments_hash=arguments_hash,
    )

    _, ledger_2, _ = stores(db_path)
    record = ledger_2.get(side_effect_id)
    external_result = json.loads(record.external_result_json or "{}")
    audit_store = DurableAuditStore(ledger_2.db_manager)
    event_types = [
        event.event_type
        for event in audit_store.list_by_side_effect_id(side_effect_id)
    ]

    assert result.success is True
    assert result.result["client_called"] is False
    assert result.result["remote_reconciled"] is True
    assert result.result["replay_outcome"] == "remote_reconciled"
    assert fake_post_client.calls == []
    assert record.status == DurableSideEffectStatus.SUCCEEDED
    assert external_result["comment_id"] == "remote-comment-1"
    assert external_result["remote_reconciled"] is True
    assert DurableAuditEventType.REMOTE_MARKER_FOUND in event_types
    assert DurableAuditEventType.REMOTE_RECONCILED in event_types


def test_executing_record_can_be_remote_reconciled(tmp_path: Path) -> None:
    db_path = tmp_path / "durable.sqlite"
    _, ledger, approval_store = stores(db_path)
    side_effect_id = persist_action_with_status(
        ledger,
        approval_store,
        DurableSideEffectStatus.EXECUTING,
    )
    service, _ = reconciliation_service(
        db_path=db_path,
        comments=[remote_comment(marker(side_effect_id))],
    )

    result = service.reconcile(
        tool_name=GITHUB_COMMENT_TOOL_NAME,
        run_id="run-durable-1",
        request=request(),
        side_effect_id=side_effect_id,
        validated_arguments_hash=argument_hash(),
    )

    assert result.success is True
    assert result.result["remote_reconciled"] is True


def test_planned_unapproved_record_does_not_become_succeeded_from_marker(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "durable.sqlite"
    _, ledger, _ = stores(db_path)
    side_effect_id = persist_planned_action(ledger)
    service, fake_post_client = reconciliation_service(
        db_path=db_path,
        comments=[remote_comment(marker(side_effect_id))],
    )

    result = service.reconcile(
        tool_name=GITHUB_COMMENT_TOOL_NAME,
        run_id="run-durable-1",
        request=request(),
        side_effect_id=side_effect_id,
        validated_arguments_hash=argument_hash(),
    )

    assert result.success is False
    assert result.result["error_type"] == "side_effect_status_not_reconcilable"
    assert fake_post_client.calls == []
    assert ledger.get(side_effect_id).status == DurableSideEffectStatus.PLANNED


def test_marker_lookup_failure_does_not_mark_succeeded(tmp_path: Path) -> None:
    db_path = tmp_path / "durable.sqlite"
    _, ledger, approval_store = stores(db_path)
    side_effect_id, arguments_hash = persist_approved_action(
        ledger,
        approval_store,
    )
    service = RemoteReconciliationService(
        durable_ledger=ledger,
        audit_store=None,
        lookup_service=lookup_service([], should_fail=True),
    )

    result = service.reconcile(
        tool_name=GITHUB_COMMENT_TOOL_NAME,
        run_id="run-durable-1",
        request=request(),
        side_effect_id=side_effect_id,
        validated_arguments_hash=arguments_hash,
    )

    assert result.success is False
    assert result.result["error_type"] == "marker_lookup_failed"
    assert ledger.get(side_effect_id).status == DurableSideEffectStatus.APPROVED
