from pathlib import Path

import pytest

from app.github.fake_client import FakeGitHubIssueCommentClient
from app.side_effects.approval_schemas import ApprovalBindingStatus
from app.side_effects.durable_schemas import DurableSideEffectStatus
from app.tools.github_comment import post_github_issue_comment
from restart_replay_helpers import (
    VALID_ARGUMENTS,
    argument_hash,
    binding,
    context,
    persist_approved_action,
    persist_planned_action,
    stores,
)


def test_missing_approval_binding_blocks_fake_client_call(tmp_path: Path) -> None:
    db_path = tmp_path / "durable.sqlite"
    _, ledger, approval_store = stores(db_path)
    side_effect_id = persist_planned_action(ledger)
    fake_client = FakeGitHubIssueCommentClient()

    result = post_github_issue_comment(
        VALID_ARGUMENTS,
        context=context(ledger, approval_store, fake_client),
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
    _, ledger, approval_store = stores(db_path)
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

    fake_client = FakeGitHubIssueCommentClient()
    result = post_github_issue_comment(
        VALID_ARGUMENTS,
        context=context(ledger, approval_store, fake_client),
    )

    assert result.success is False
    assert fake_client.calls == []
    assert ledger.get(side_effect_id).status == expected_record_status


def test_approval_hash_mismatch_blocks_fake_client_call(tmp_path: Path) -> None:
    db_path = tmp_path / "durable.sqlite"
    manager, ledger, approval_store = stores(db_path)
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
    fake_client = FakeGitHubIssueCommentClient()

    result = post_github_issue_comment(
        VALID_ARGUMENTS,
        context=context(ledger, approval_store, fake_client),
    )

    assert result.success is False
    assert result.result["error_type"] == "approval_not_authorized"
    assert fake_client.calls == []
    assert ledger.get(side_effect_id).status == DurableSideEffectStatus.APPROVED


def test_approval_for_different_side_effect_id_does_not_authorize_execution(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "durable.sqlite"
    _, ledger, approval_store = stores(db_path)
    side_effect_id = persist_planned_action(ledger)
    ledger.mark_approved(side_effect_id)
    persist_approved_action(
        ledger,
        approval_store,
        run_id="run-other",
        approval_id="approval-other",
    )
    fake_client = FakeGitHubIssueCommentClient()

    result = post_github_issue_comment(
        VALID_ARGUMENTS,
        context=context(ledger, approval_store, fake_client),
    )

    assert result.success is False
    assert result.result["error_type"] == "approval_not_authorized"
    assert fake_client.calls == []
    assert ledger.get(side_effect_id).status == DurableSideEffectStatus.APPROVED
