import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pytest

from app.github.fake_client import FakeGitHubIssueCommentClient
from app.persistence.sqlite import SQLiteConnectionManager
from app.side_effects.approval_binding import DurableApprovalBindingStore
from app.side_effects.approval_schemas import (
    ApprovalBindingRecord,
    ApprovalBindingStatus,
)
from app.side_effects.durable_ledger import DurableSideEffectLedger
from app.side_effects.durable_schemas import (
    DurableSideEffectRecord,
    DurableSideEffectStatus,
)
from app.side_effects.idempotency import (
    build_side_effect_id,
    validated_arguments_hash,
)
from app.tools.context import ToolExecutionContext
from app.tools.github_comment import (
    GITHUB_COMMENT_SKILL_ID,
    GITHUB_COMMENT_STEP_ID,
    GITHUB_COMMENT_TOOL_NAME,
    post_github_issue_comment,
)


VALID_ARGUMENTS = {
    "repository": "Harry5174/learn-agentic-ai",
    "issue_number": 1,
    "comment_body": "A deterministic durable fake GitHub comment.",
}


def test_approved_record_and_binding_survive_fresh_store_objects(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "durable.sqlite"
    _, ledger_1, approval_store_1 = _stores(db_path)
    side_effect_id, argument_hash = _persist_approved_action(
        ledger_1,
        approval_store_1,
    )

    _, ledger_2, approval_store_2 = _stores(db_path)
    record = ledger_2.get(side_effect_id)

    assert record.status == DurableSideEffectStatus.APPROVED
    assert record.validated_arguments_hash == argument_hash
    approval_store_2.assert_approved_for_action(side_effect_id, argument_hash)


def test_first_approved_execution_calls_fake_client_once_and_persists_success(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "durable.sqlite"
    _, ledger, approval_store = _stores(db_path)
    side_effect_id, _ = _persist_approved_action(ledger, approval_store)
    fake_client = FakeGitHubIssueCommentClient()

    result = post_github_issue_comment(
        VALID_ARGUMENTS,
        context=_context(ledger, approval_store, fake_client),
    )
    record = ledger.get(side_effect_id)
    external_result = json.loads(record.external_result_json or "{}")

    assert result.success is True
    assert result.result["approval_checked"] is True
    assert result.result["client_called"] is True
    assert result.result["replay_outcome"] == "executed"
    assert [call.model_dump() for call in fake_client.calls] == [VALID_ARGUMENTS]
    assert record.status == DurableSideEffectStatus.SUCCEEDED
    assert record.started_at is not None
    assert record.executed_at is not None
    assert external_result["comment_id"] == "fake-comment-1"


def test_restart_replay_after_success_suppresses_duplicate_fake_client_call(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "durable.sqlite"
    _, ledger_1, approval_store_1 = _stores(db_path)
    side_effect_id, _ = _persist_approved_action(ledger_1, approval_store_1)
    fake_client_1 = FakeGitHubIssueCommentClient()

    first = post_github_issue_comment(
        VALID_ARGUMENTS,
        context=_context(ledger_1, approval_store_1, fake_client_1),
    )

    _, ledger_2, approval_store_2 = _stores(db_path)
    fake_client_2 = FakeGitHubIssueCommentClient()
    replay = post_github_issue_comment(
        VALID_ARGUMENTS,
        context=_context(ledger_2, approval_store_2, fake_client_2),
    )
    replayed_record = ledger_2.get(side_effect_id)
    external_result = json.loads(replayed_record.external_result_json or "{}")

    assert first.success is True
    assert len(fake_client_1.calls) == 1
    assert replay.success is True
    assert fake_client_2.calls == []
    assert replay.result["client_called"] is False
    assert replay.result["skipped"] is True
    assert replay.result["duplicate_suppressed"] is True
    assert replay.result["replay_outcome"] == "already_succeeded"
    assert replay.result["skip_reason"] == "already_succeeded"
    assert replay.result["side_effect_status"] == "succeeded"
    assert replayed_record.status == DurableSideEffectStatus.SUCCEEDED
    assert external_result["comment_id"] == "fake-comment-1"


def test_missing_approval_binding_blocks_fake_client_call(tmp_path: Path) -> None:
    db_path = tmp_path / "durable.sqlite"
    _, ledger, approval_store = _stores(db_path)
    side_effect_id = _persist_planned_action(ledger)
    fake_client = FakeGitHubIssueCommentClient()

    result = post_github_issue_comment(
        VALID_ARGUMENTS,
        context=_context(ledger, approval_store, fake_client),
    )

    assert result.success is False
    assert result.result["error_type"] == "approval_not_authorized"
    assert result.result["approval_checked"] is True
    assert fake_client.calls == []
    assert ledger.get(side_effect_id).status == DurableSideEffectStatus.PLANNED


@pytest.mark.parametrize(
    ("approval_status", "expected_record_status"),
    [
        (ApprovalBindingStatus.PENDING, DurableSideEffectStatus.PLANNED),
        (ApprovalBindingStatus.REJECTED, DurableSideEffectStatus.REJECTED),
        (ApprovalBindingStatus.EXPIRED, DurableSideEffectStatus.PLANNED),
    ],
)
def test_unapproved_bindings_do_not_execute_fake_client(
    tmp_path: Path,
    approval_status: ApprovalBindingStatus,
    expected_record_status: DurableSideEffectStatus,
) -> None:
    db_path = tmp_path / "durable.sqlite"
    _, ledger, approval_store = _stores(db_path)
    side_effect_id = _persist_planned_action(ledger)
    approval_id = "approval-unapproved"
    approval_store.create_pending(
        _binding(
            approval_id=approval_id,
            side_effect_id=side_effect_id,
            argument_hash=_argument_hash(),
        )
    )
    if approval_status == ApprovalBindingStatus.REJECTED:
        approval_store.reject(approval_id, decided_by="admin_1")
    elif approval_status == ApprovalBindingStatus.EXPIRED:
        approval_store.expire(approval_id)

    fake_client = FakeGitHubIssueCommentClient()
    result = post_github_issue_comment(
        VALID_ARGUMENTS,
        context=_context(ledger, approval_store, fake_client),
    )

    assert result.success is False
    assert fake_client.calls == []
    assert ledger.get(side_effect_id).status == expected_record_status


def test_approval_hash_mismatch_blocks_fake_client_call(tmp_path: Path) -> None:
    db_path = tmp_path / "durable.sqlite"
    manager, ledger, approval_store = _stores(db_path)
    side_effect_id, _ = _persist_approved_action(ledger, approval_store)
    with manager.get_connection() as conn:
        conn.execute(
            """
            UPDATE approval_bindings
            SET validated_arguments_hash = ?
            WHERE side_effect_id = ?
            """,
            ("wrong_hash", side_effect_id),
        )
        conn.commit()
    fake_client = FakeGitHubIssueCommentClient()

    result = post_github_issue_comment(
        VALID_ARGUMENTS,
        context=_context(ledger, approval_store, fake_client),
    )

    assert result.success is False
    assert result.result["error_type"] == "approval_not_authorized"
    assert fake_client.calls == []
    assert ledger.get(side_effect_id).status == DurableSideEffectStatus.APPROVED


def test_approval_for_different_side_effect_id_does_not_authorize_execution(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "durable.sqlite"
    _, ledger, approval_store = _stores(db_path)
    side_effect_id = _persist_planned_action(ledger)
    ledger.mark_approved(side_effect_id)
    _persist_approved_action(
        ledger,
        approval_store,
        run_id="run-other",
        approval_id="approval-other",
    )
    fake_client = FakeGitHubIssueCommentClient()

    result = post_github_issue_comment(
        VALID_ARGUMENTS,
        context=_context(ledger, approval_store, fake_client),
    )

    assert result.success is False
    assert result.result["error_type"] == "approval_not_authorized"
    assert fake_client.calls == []
    assert ledger.get(side_effect_id).status == DurableSideEffectStatus.APPROVED


@pytest.mark.parametrize(
    ("status", "expected_error_type", "expected_outcome"),
    [
        (
            DurableSideEffectStatus.BLOCKED,
            "side_effect_status_not_executable",
            "blocked_terminal",
        ),
        (
            DurableSideEffectStatus.REJECTED,
            "side_effect_status_not_executable",
            "rejected_terminal",
        ),
        (
            DurableSideEffectStatus.FAILED,
            "side_effect_status_not_executable",
            "failed_terminal",
        ),
        (
            DurableSideEffectStatus.SKIPPED_DUPLICATE,
            "side_effect_status_not_executable",
            "skipped_duplicate_terminal",
        ),
        (
            DurableSideEffectStatus.EXECUTING,
            "side_effect_already_executing",
            "unsafe_to_retry",
        ),
    ],
)
def test_non_executable_side_effect_statuses_do_not_call_fake_client(
    tmp_path: Path,
    status: DurableSideEffectStatus,
    expected_error_type: str,
    expected_outcome: str,
) -> None:
    db_path = tmp_path / "durable.sqlite"
    _, ledger, approval_store = _stores(db_path)
    side_effect_id = _persist_action_with_status(ledger, approval_store, status)
    fake_client = FakeGitHubIssueCommentClient()

    result = post_github_issue_comment(
        VALID_ARGUMENTS,
        context=_context(ledger, approval_store, fake_client),
    )

    assert result.success is False
    assert result.result["error_type"] == expected_error_type
    assert result.result["replay_outcome"] == expected_outcome
    assert fake_client.calls == []
    assert ledger.get(side_effect_id).status == status


def test_succeeded_status_returns_duplicate_suppressed_without_mutation(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "durable.sqlite"
    _, ledger, approval_store = _stores(db_path)
    side_effect_id = _persist_action_with_status(
        ledger,
        approval_store,
        DurableSideEffectStatus.SUCCEEDED,
    )
    fake_client = FakeGitHubIssueCommentClient()

    result = post_github_issue_comment(
        VALID_ARGUMENTS,
        context=_context(ledger, approval_store, fake_client),
    )

    assert result.success is True
    assert result.result["replay_outcome"] == "already_succeeded"
    assert result.result["duplicate_suppressed"] is True
    assert fake_client.calls == []
    assert ledger.get(side_effect_id).status == DurableSideEffectStatus.SUCCEEDED


def test_fake_client_failure_marks_failed_and_replay_does_not_retry(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "durable.sqlite"
    _, ledger_1, approval_store_1 = _stores(db_path)
    side_effect_id, _ = _persist_approved_action(ledger_1, approval_store_1)
    failing_client = FakeGitHubIssueCommentClient(
        should_fail=True,
        failure_error_type="rate_limited",
        failure_message="Simulated durable fake-client failure.",
        failure_retryable=True,
    )

    failed = post_github_issue_comment(
        VALID_ARGUMENTS,
        context=_context(ledger_1, approval_store_1, failing_client),
    )
    failed_record = ledger_1.get(side_effect_id)
    failure_payload = json.loads(failed_record.failure_json or "{}")

    _, ledger_2, approval_store_2 = _stores(db_path)
    replay_client = FakeGitHubIssueCommentClient()
    replay = post_github_issue_comment(
        VALID_ARGUMENTS,
        context=_context(ledger_2, approval_store_2, replay_client),
    )

    assert failed.success is False
    assert failed.result["client_called"] is True
    assert failing_client.calls
    assert failed_record.status == DurableSideEffectStatus.FAILED
    assert failure_payload["error_type"] == "rate_limited"
    assert replay.success is False
    assert replay.result["error_type"] == "side_effect_status_not_executable"
    assert replay.result["replay_outcome"] == "failed_terminal"
    assert replay_client.calls == []
    assert ledger_2.get(side_effect_id).status == DurableSideEffectStatus.FAILED


def test_validated_arguments_hash_and_side_effect_id_are_deterministic() -> None:
    reordered_arguments = {
        "comment_body": VALID_ARGUMENTS["comment_body"],
        "issue_number": VALID_ARGUMENTS["issue_number"],
        "repository": VALID_ARGUMENTS["repository"],
    }
    context_1 = _context_for_identity_only()
    context_2 = _context_for_identity_only()

    assert validated_arguments_hash(VALID_ARGUMENTS) == validated_arguments_hash(
        reordered_arguments
    )
    assert _side_effect_id(context_1.run_id) == _side_effect_id(context_2.run_id)


def _stores(
    db_path: Path,
) -> tuple[
    SQLiteConnectionManager,
    DurableSideEffectLedger,
    DurableApprovalBindingStore,
]:
    manager = SQLiteConnectionManager(db_path)
    manager.initialize_schema()
    ledger = DurableSideEffectLedger(manager)
    approval_store = DurableApprovalBindingStore(manager, ledger)

    return manager, ledger, approval_store


def _context(
    ledger: DurableSideEffectLedger,
    approval_store: DurableApprovalBindingStore,
    fake_client: FakeGitHubIssueCommentClient,
    *,
    run_id: str = "run-durable-1",
) -> ToolExecutionContext:
    return ToolExecutionContext(
        run_id=run_id,
        step_id=GITHUB_COMMENT_STEP_ID,
        github_issue_comment_client=fake_client,
        durable_side_effect_ledger=ledger,
        durable_approval_binding_store=approval_store,
    )


def _context_for_identity_only() -> ToolExecutionContext:
    return ToolExecutionContext(
        run_id="run-durable-1",
        step_id=GITHUB_COMMENT_STEP_ID,
    )


def _persist_approved_action(
    ledger: DurableSideEffectLedger,
    approval_store: DurableApprovalBindingStore,
    *,
    run_id: str = "run-durable-1",
    approval_id: str = "approval-durable-1",
    arguments: dict[str, Any] | None = None,
) -> tuple[str, str]:
    active_arguments = arguments or VALID_ARGUMENTS
    side_effect_id = _persist_planned_action(
        ledger,
        run_id=run_id,
        arguments=active_arguments,
    )
    argument_hash = validated_arguments_hash(active_arguments)
    approval_store.create_pending(
        _binding(
            approval_id=approval_id,
            side_effect_id=side_effect_id,
            argument_hash=argument_hash,
            run_id=run_id,
        )
    )
    approval_store.approve(approval_id, decided_by="admin_1")

    return side_effect_id, argument_hash


def _persist_planned_action(
    ledger: DurableSideEffectLedger,
    *,
    run_id: str = "run-durable-1",
    arguments: dict[str, Any] | None = None,
) -> str:
    active_arguments = arguments or VALID_ARGUMENTS
    argument_hash = validated_arguments_hash(active_arguments)
    side_effect_id = _side_effect_id(run_id, active_arguments)
    ledger.create_planned(
        DurableSideEffectRecord(
            side_effect_id=side_effect_id,
            run_id=run_id,
            skill_id=GITHUB_COMMENT_SKILL_ID,
            step_id=GITHUB_COMMENT_STEP_ID,
            tool_name=GITHUB_COMMENT_TOOL_NAME,
            validated_arguments_hash=argument_hash,
            status=DurableSideEffectStatus.PLANNED,
            repository=str(active_arguments["repository"]),
            issue_number=int(active_arguments["issue_number"]),
            comment_body_hash=_comment_body_hash(
                str(active_arguments["comment_body"])
            ),
            comment_body_preview=str(active_arguments["comment_body"])[:80],
            created_at=_now(),
            updated_at=_now(),
        )
    )

    return side_effect_id


def _persist_action_with_status(
    ledger: DurableSideEffectLedger,
    approval_store: DurableApprovalBindingStore,
    status: DurableSideEffectStatus,
) -> str:
    if status in {
        DurableSideEffectStatus.BLOCKED,
        DurableSideEffectStatus.REJECTED,
    }:
        side_effect_id = _persist_planned_action(ledger)
        if status == DurableSideEffectStatus.BLOCKED:
            ledger.mark_blocked(side_effect_id, reason="Blocked for status test.")
        else:
            ledger.mark_rejected(side_effect_id, reason="Rejected for status test.")
        return side_effect_id

    side_effect_id, _ = _persist_approved_action(ledger, approval_store)
    if status == DurableSideEffectStatus.APPROVED:
        return side_effect_id

    ledger.mark_executing(side_effect_id)
    if status == DurableSideEffectStatus.EXECUTING:
        return side_effect_id

    if status == DurableSideEffectStatus.FAILED:
        ledger.mark_failed(
            side_effect_id,
            failure={"error_type": "preexisting_failure"},
        )
        return side_effect_id

    ledger.mark_succeeded(
        side_effect_id,
        external_result={"comment_id": "preexisting-comment"},
    )
    if status == DurableSideEffectStatus.SUCCEEDED:
        return side_effect_id

    ledger.mark_skipped_duplicate(
        side_effect_id,
        external_result={"comment_id": "preexisting-comment"},
    )
    return side_effect_id


def _binding(
    *,
    approval_id: str,
    side_effect_id: str,
    argument_hash: str,
    run_id: str = "run-durable-1",
) -> ApprovalBindingRecord:
    return ApprovalBindingRecord(
        approval_id=approval_id,
        run_id=run_id,
        skill_id=GITHUB_COMMENT_SKILL_ID,
        step_id=GITHUB_COMMENT_STEP_ID,
        tool_name=GITHUB_COMMENT_TOOL_NAME,
        side_effect_id=side_effect_id,
        validated_arguments_hash=argument_hash,
        approval_status=ApprovalBindingStatus.PENDING,
        requested_by="admin_1",
        created_at=_now(),
    )


def _side_effect_id(
    run_id: str = "run-durable-1",
    arguments: dict[str, Any] | None = None,
) -> str:
    return build_side_effect_id(
        skill_run_id=run_id,
        step_id=GITHUB_COMMENT_STEP_ID,
        tool_name=GITHUB_COMMENT_TOOL_NAME,
        validated_arguments_hash=validated_arguments_hash(arguments or VALID_ARGUMENTS),
    )


def _argument_hash() -> str:
    return validated_arguments_hash(VALID_ARGUMENTS)


def _comment_body_hash(comment_body: str) -> str:
    return hashlib.sha256(comment_body.encode("utf-8")).hexdigest()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
