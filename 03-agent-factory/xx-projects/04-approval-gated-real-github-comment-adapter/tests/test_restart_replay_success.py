import json
from pathlib import Path

from app.github.fake_client import FakeGitHubIssueCommentClient
from app.side_effects.durable_schemas import DurableSideEffectStatus
from app.tools.github_comment import post_github_issue_comment
from restart_replay_helpers import (
    VALID_ARGUMENTS,
    context,
    persist_action_with_status,
    persist_approved_action,
    stores,
)


def test_approved_record_and_binding_survive_fresh_store_objects(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "durable.sqlite"
    _, ledger_1, approval_store_1 = stores(db_path)
    side_effect_id, argument_hash = persist_approved_action(
        ledger_1,
        approval_store_1,
    )

    _, ledger_2, approval_store_2 = stores(db_path)
    record = ledger_2.get(side_effect_id)

    assert record.status == DurableSideEffectStatus.APPROVED
    assert record.validated_arguments_hash == argument_hash
    approval_store_2.assert_approved_for_action(side_effect_id, argument_hash)


def test_first_approved_execution_calls_fake_client_once_and_persists_success(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "durable.sqlite"
    _, ledger, approval_store = stores(db_path)
    side_effect_id, _ = persist_approved_action(ledger, approval_store)
    fake_client = FakeGitHubIssueCommentClient()

    result = post_github_issue_comment(
        VALID_ARGUMENTS,
        context=context(ledger, approval_store, fake_client),
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
    _, ledger_1, approval_store_1 = stores(db_path)
    side_effect_id, _ = persist_approved_action(ledger_1, approval_store_1)
    fake_client_1 = FakeGitHubIssueCommentClient()

    first = post_github_issue_comment(
        VALID_ARGUMENTS,
        context=context(ledger_1, approval_store_1, fake_client_1),
    )

    _, ledger_2, approval_store_2 = stores(db_path)
    fake_client_2 = FakeGitHubIssueCommentClient()
    replay = post_github_issue_comment(
        VALID_ARGUMENTS,
        context=context(ledger_2, approval_store_2, fake_client_2),
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


def test_succeeded_status_returns_duplicate_suppressed_without_mutation(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "durable.sqlite"
    _, ledger, approval_store = stores(db_path)
    side_effect_id = persist_action_with_status(
        ledger,
        approval_store,
        DurableSideEffectStatus.SUCCEEDED,
    )
    fake_client = FakeGitHubIssueCommentClient()

    result = post_github_issue_comment(
        VALID_ARGUMENTS,
        context=context(ledger, approval_store, fake_client),
    )

    assert result.success is True
    assert result.result["replay_outcome"] == "already_succeeded"
    assert result.result["duplicate_suppressed"] is True
    assert fake_client.calls == []
    assert ledger.get(side_effect_id).status == DurableSideEffectStatus.SUCCEEDED
