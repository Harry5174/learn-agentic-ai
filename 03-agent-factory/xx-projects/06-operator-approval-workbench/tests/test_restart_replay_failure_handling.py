import json
from pathlib import Path

from app.github.fake_client import FakeGitHubIssueCommentClient
from app.side_effects.durable_schemas import DurableSideEffectStatus
from app.tools.github_comment import post_github_issue_comment
from restart_replay_helpers import (
    VALID_ARGUMENTS,
    context,
    persist_approved_action,
    stores,
)


def test_fake_client_failure_marks_failed_and_replay_does_not_retry(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "durable.sqlite"
    _, ledger_1, approval_store_1 = stores(db_path)
    side_effect_id, _ = persist_approved_action(ledger_1, approval_store_1)
    failing_client = FakeGitHubIssueCommentClient(
        should_fail=True,
        failure_error_type="rate_limited",
        failure_message="Simulated durable fake-client failure.",
        failure_retryable=True,
    )

    failed = post_github_issue_comment(
        VALID_ARGUMENTS,
        context=context(ledger_1, approval_store_1, failing_client),
    )
    failed_record = ledger_1.get(side_effect_id)
    failure_payload = json.loads(failed_record.failure_json or "{}")

    _, ledger_2, approval_store_2 = stores(db_path)
    replay_client = FakeGitHubIssueCommentClient()
    replay = post_github_issue_comment(
        VALID_ARGUMENTS,
        context=context(ledger_2, approval_store_2, replay_client),
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
