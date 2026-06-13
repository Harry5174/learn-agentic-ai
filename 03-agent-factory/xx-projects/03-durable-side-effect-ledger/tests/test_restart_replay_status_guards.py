from pathlib import Path

import pytest

from app.github.fake_client import FakeGitHubIssueCommentClient
from app.side_effects.durable_schemas import DurableSideEffectStatus
from app.tools.github_comment import post_github_issue_comment
from restart_replay_helpers import (
    VALID_ARGUMENTS,
    context,
    persist_action_with_status,
    stores,
)


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
    _, ledger, approval_store = stores(db_path)
    side_effect_id = persist_action_with_status(ledger, approval_store, status)
    fake_client = FakeGitHubIssueCommentClient()

    result = post_github_issue_comment(
        VALID_ARGUMENTS,
        context=context(ledger, approval_store, fake_client),
    )

    assert result.success is False
    assert result.result["error_type"] == expected_error_type
    assert result.result["replay_outcome"] == expected_outcome
    assert fake_client.calls == []
    assert ledger.get(side_effect_id).status == status
