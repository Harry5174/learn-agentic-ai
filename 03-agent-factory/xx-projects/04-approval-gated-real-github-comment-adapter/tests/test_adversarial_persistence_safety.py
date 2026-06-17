import sqlite3
from pathlib import Path

import pytest

from app.audit.durable_schemas import DurableAuditEventType
from app.audit.durable_store import DurableAuditStore
from app.github.fake_client import FakeGitHubIssueCommentClient
from app.side_effects.approval_schemas import ApprovalBindingStatus
from app.side_effects.durable_schemas import DurableSideEffectStatus
from app.tools.github_comment import post_github_issue_comment
from restart_replay_helpers import (
    VALID_ARGUMENTS,
    argument_hash,
    binding,
    context,
    persist_action_with_status,
    persist_approved_action,
    persist_planned_action,
    stores,
)


def durable_stores(db_path: Path):
    manager, ledger, approval_store = stores(db_path)
    audit_store = DurableAuditStore(manager)
    audit_store.initialize()
    return manager, ledger, approval_store, audit_store


def audit_event_types(
    audit_store: DurableAuditStore,
    side_effect_id: str,
) -> list[DurableAuditEventType]:
    return [
        event.event_type
        for event in audit_store.list_by_side_effect_id(side_effect_id)
    ]


def raw_metadata_json(db_path: Path) -> str:
    with sqlite3.connect(db_path) as conn:
        rows = conn.execute(
            "SELECT metadata_json FROM durable_audit_events"
        ).fetchall()
    return "\n".join(row[0] or "" for row in rows)


def assert_blocked_without_fake_client(
    *,
    db_path: Path,
    side_effect_id: str,
    ledger,
    approval_store,
    audit_store: DurableAuditStore,
) -> None:
    fake_client = FakeGitHubIssueCommentClient()

    result = post_github_issue_comment(
        VALID_ARGUMENTS,
        context(
            ledger,
            approval_store,
            fake_client,
            audit_store=audit_store,
        ),
    )

    assert result.success is False
    assert fake_client.calls == []
    assert DurableAuditEventType.EXECUTION_REQUESTED in audit_event_types(
        audit_store, side_effect_id
    )
    assert DurableAuditEventType.EXECUTION_BLOCKED in audit_event_types(
        audit_store, side_effect_id
    )
    lowered = raw_metadata_json(db_path).lower()
    for forbidden in (
        "github_token",
        "authorization",
        "api_base_url",
        "client_config",
        "transport",
    ):
        assert forbidden not in lowered


def test_successful_fake_client_execution_records_required_audit_events(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "durable.sqlite"
    _, ledger, approval_store, audit_store = durable_stores(db_path)
    side_effect_id, _ = persist_approved_action(ledger, approval_store)
    fake_client = FakeGitHubIssueCommentClient()

    result = post_github_issue_comment(
        VALID_ARGUMENTS,
        context(
            ledger,
            approval_store,
            fake_client,
            audit_store=audit_store,
        ),
    )

    assert result.success is True
    assert [event_type.value for event_type in audit_event_types(audit_store, side_effect_id)] == [
        "execution_requested",
        "approval_authorized",
        "execution_started",
        "fake_client_called",
        "execution_succeeded",
    ]
    assert len(fake_client.calls) == 1


def test_duplicate_replay_records_duplicate_suppressed_after_restart(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "durable.sqlite"
    _, ledger_1, approval_store_1, audit_store_1 = durable_stores(db_path)
    side_effect_id, _ = persist_approved_action(ledger_1, approval_store_1)
    fake_client_1 = FakeGitHubIssueCommentClient()

    first = post_github_issue_comment(
        VALID_ARGUMENTS,
        context(
            ledger_1,
            approval_store_1,
            fake_client_1,
            audit_store=audit_store_1,
        ),
    )

    _, ledger_2, approval_store_2, audit_store_2 = durable_stores(db_path)
    fake_client_2 = FakeGitHubIssueCommentClient()
    replay = post_github_issue_comment(
        VALID_ARGUMENTS,
        context(
            ledger_2,
            approval_store_2,
            fake_client_2,
            audit_store=audit_store_2,
        ),
    )

    assert first.success is True
    assert replay.success is True
    assert fake_client_2.calls == []
    assert replay.result["duplicate_suppressed"] is True
    assert DurableAuditEventType.DUPLICATE_SUPPRESSED in audit_event_types(
        audit_store_2, side_effect_id
    )
    assert audit_store_2.list_by_side_effect_id(side_effect_id)[0].event_type == (
        DurableAuditEventType.EXECUTION_REQUESTED
    )


def test_missing_approval_binding_records_blocked_audit(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "durable.sqlite"
    _, ledger, approval_store, audit_store = durable_stores(db_path)
    side_effect_id = persist_planned_action(ledger)

    assert_blocked_without_fake_client(
        db_path=db_path,
        side_effect_id=side_effect_id,
        ledger=ledger,
        approval_store=approval_store,
        audit_store=audit_store,
    )
    assert ledger.get(side_effect_id).status == DurableSideEffectStatus.PLANNED


@pytest.mark.parametrize(
    ("approval_status", "expected_record_status"),
    [
        (ApprovalBindingStatus.PENDING, DurableSideEffectStatus.PLANNED),
        (ApprovalBindingStatus.REJECTED, DurableSideEffectStatus.REJECTED),
        (ApprovalBindingStatus.EXPIRED, DurableSideEffectStatus.PLANNED),
    ],
)
def test_unapproved_bindings_record_blocked_audit(
    tmp_path: Path,
    approval_status: ApprovalBindingStatus,
    expected_record_status: DurableSideEffectStatus,
) -> None:
    db_path = tmp_path / "durable.sqlite"
    _, ledger, approval_store, audit_store = durable_stores(db_path)
    side_effect_id = persist_planned_action(ledger)
    approval_id = "approval-unapproved"
    approval_store.create_pending(
        binding(
            approval_id=approval_id,
            side_effect_id=side_effect_id,
            argument_hash=argument_hash(),
        )
    )
    if approval_status == ApprovalBindingStatus.REJECTED:
        approval_store.reject(approval_id, decided_by="admin_1")
    elif approval_status == ApprovalBindingStatus.EXPIRED:
        approval_store.expire(approval_id)

    assert_blocked_without_fake_client(
        db_path=db_path,
        side_effect_id=side_effect_id,
        ledger=ledger,
        approval_store=approval_store,
        audit_store=audit_store,
    )
    assert ledger.get(side_effect_id).status == expected_record_status


def test_wrong_validated_arguments_hash_records_blocked_audit(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "durable.sqlite"
    manager, ledger, approval_store, audit_store = durable_stores(db_path)
    side_effect_id, _ = persist_approved_action(ledger, approval_store)
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

    assert_blocked_without_fake_client(
        db_path=db_path,
        side_effect_id=side_effect_id,
        ledger=ledger,
        approval_store=approval_store,
        audit_store=audit_store,
    )
    assert ledger.get(side_effect_id).status == DurableSideEffectStatus.APPROVED


def test_approval_for_wrong_side_effect_does_not_authorize_execution(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "durable.sqlite"
    _, ledger, approval_store, audit_store = durable_stores(db_path)
    side_effect_id = persist_planned_action(ledger)
    ledger.mark_approved(side_effect_id)
    persist_approved_action(
        ledger,
        approval_store,
        run_id="run-other",
        approval_id="approval-other",
    )

    assert_blocked_without_fake_client(
        db_path=db_path,
        side_effect_id=side_effect_id,
        ledger=ledger,
        approval_store=approval_store,
        audit_store=audit_store,
    )
    assert ledger.get(side_effect_id).status == DurableSideEffectStatus.APPROVED


def test_approval_for_action_b_cannot_be_used_for_action_a(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "durable.sqlite"
    _, ledger, approval_store, audit_store = durable_stores(db_path)
    action_b = {
        **VALID_ARGUMENTS,
        "issue_number": 2,
        "comment_body": "A different durable fake GitHub comment.",
    }
    persist_approved_action(
        ledger,
        approval_store,
        run_id="run-action-b",
        approval_id="approval-action-b",
        arguments=action_b,
    )
    side_effect_id = persist_planned_action(ledger)
    ledger.mark_approved(side_effect_id)

    assert_blocked_without_fake_client(
        db_path=db_path,
        side_effect_id=side_effect_id,
        ledger=ledger,
        approval_store=approval_store,
        audit_store=audit_store,
    )


@pytest.mark.parametrize(
    "status",
    [
        DurableSideEffectStatus.BLOCKED,
        DurableSideEffectStatus.REJECTED,
        DurableSideEffectStatus.FAILED,
        DurableSideEffectStatus.EXECUTING,
        DurableSideEffectStatus.SKIPPED_DUPLICATE,
    ],
)
def test_non_executable_side_effect_statuses_record_blocked_audit(
    tmp_path: Path,
    status: DurableSideEffectStatus,
) -> None:
    db_path = tmp_path / "durable.sqlite"
    _, ledger, approval_store, audit_store = durable_stores(db_path)
    side_effect_id = persist_action_with_status(ledger, approval_store, status)

    assert_blocked_without_fake_client(
        db_path=db_path,
        side_effect_id=side_effect_id,
        ledger=ledger,
        approval_store=approval_store,
        audit_store=audit_store,
    )
    assert ledger.get(side_effect_id).status == status


def test_succeeded_side_effect_records_duplicate_suppressed_audit(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "durable.sqlite"
    _, ledger, approval_store, audit_store = durable_stores(db_path)
    side_effect_id = persist_action_with_status(
        ledger,
        approval_store,
        DurableSideEffectStatus.SUCCEEDED,
    )
    fake_client = FakeGitHubIssueCommentClient()

    result = post_github_issue_comment(
        VALID_ARGUMENTS,
        context(
            ledger,
            approval_store,
            fake_client,
            audit_store=audit_store,
        ),
    )

    assert result.success is True
    assert fake_client.calls == []
    assert DurableAuditEventType.DUPLICATE_SUPPRESSED in audit_event_types(
        audit_store, side_effect_id
    )
    assert ledger.get(side_effect_id).status == DurableSideEffectStatus.SUCCEEDED


def test_fake_client_failure_records_failed_audit_and_is_terminal(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "durable.sqlite"
    _, ledger_1, approval_store_1, audit_store_1 = durable_stores(db_path)
    side_effect_id, _ = persist_approved_action(ledger_1, approval_store_1)
    failing_client = FakeGitHubIssueCommentClient(
        should_fail=True,
        failure_error_type="rate_limited",
        failure_message="Simulated durable fake-client failure.",
        failure_retryable=True,
    )

    failed = post_github_issue_comment(
        VALID_ARGUMENTS,
        context(
            ledger_1,
            approval_store_1,
            failing_client,
            audit_store=audit_store_1,
        ),
    )

    _, ledger_2, approval_store_2, audit_store_2 = durable_stores(db_path)
    replay_client = FakeGitHubIssueCommentClient()
    replay = post_github_issue_comment(
        VALID_ARGUMENTS,
        context(
            ledger_2,
            approval_store_2,
            replay_client,
            audit_store=audit_store_2,
        ),
    )
    event_types = audit_event_types(audit_store_2, side_effect_id)

    assert failed.success is False
    assert DurableAuditEventType.EXECUTION_FAILED in event_types
    assert DurableAuditEventType.EXECUTION_SUCCEEDED not in event_types
    assert ledger_2.get(side_effect_id).status == DurableSideEffectStatus.FAILED
    assert replay.success is False
    assert replay.result["replay_outcome"] == "failed_terminal"
    assert replay_client.calls == []


class FailingPreExecutionAuditStore:
    def append_event(self, **kwargs):  # noqa: ANN003, ANN201
        raise RuntimeError("simulated durable audit append failure")


def test_pre_execution_audit_failure_fails_closed_before_fake_client(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "durable.sqlite"
    _, ledger, approval_store = stores(db_path)
    side_effect_id, _ = persist_approved_action(ledger, approval_store)
    fake_client = FakeGitHubIssueCommentClient()

    result = post_github_issue_comment(
        VALID_ARGUMENTS,
        context(
            ledger,
            approval_store,
            fake_client,
            audit_store=FailingPreExecutionAuditStore(),
        ),
    )

    assert result.success is False
    assert result.result["error_type"] == "durable_audit_append_failed"
    assert fake_client.calls == []
    assert ledger.get(side_effect_id).status == DurableSideEffectStatus.APPROVED


def test_execution_audit_metadata_raw_sqlite_value_excludes_unsafe_terms(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "durable.sqlite"
    _, ledger, approval_store, audit_store = durable_stores(db_path)
    persist_approved_action(ledger, approval_store)

    result = post_github_issue_comment(
        VALID_ARGUMENTS,
        context(
            ledger,
            approval_store,
            FakeGitHubIssueCommentClient(),
            audit_store=audit_store,
        ),
    )

    assert result.success is True
    lowered = raw_metadata_json(db_path).lower()
    for forbidden in (
        "github_token",
        "authorization",
        "api_base_url",
        "client_config",
        "transport",
    ):
        assert forbidden not in lowered


def test_runtime_source_does_not_add_real_github_network_or_token_path() -> None:
    src_root = Path(__file__).resolve().parents[1] / "src" / "app"
    runtime_text = "\n".join(
        path.read_text()
        for path in [
            src_root / "tools" / "github_comment.py",
            src_root / "tools" / "github_comment_durable_execution.py",
            src_root / "github" / "client.py",
            src_root / "github" / "fake_client.py",
        ]
    )

    for forbidden in ("requests", "httpx", "PyGithub", "github.Github"):
        assert forbidden not in runtime_text
    assert "GITHUB_TOKEN" not in runtime_text
