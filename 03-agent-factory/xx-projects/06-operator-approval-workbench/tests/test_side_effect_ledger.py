import pytest

from app.side_effects.idempotency import (
    build_side_effect_id,
    validated_arguments_hash,
)
from app.side_effects.ledger import InMemorySideEffectLedger
from app.side_effects.schemas import SideEffectStatus


def _metadata() -> dict[str, str]:
    argument_hash = validated_arguments_hash(
        {
            "repository": "Harry5174/learn-agentic-ai",
            "issue_number": 1,
            "comment_body": "A deterministic fake comment.",
        }
    )
    side_effect_id = build_side_effect_id(
        skill_run_id="run-123",
        step_id="post_comment",
        tool_name="github_issue_comment_boundary",
        validated_arguments_hash=argument_hash,
    )

    return {
        "side_effect_id": side_effect_id,
        "skill_run_id": "run-123",
        "step_id": "post_comment",
        "tool_name": "github_issue_comment_boundary",
        "validated_arguments_hash": argument_hash,
    }


def test_empty_ledger_returns_no_record() -> None:
    ledger = InMemorySideEffectLedger()

    assert ledger.get("missing") is None
    assert ledger.has_succeeded("missing") is False


def test_record_started_can_be_retrieved_with_metadata() -> None:
    ledger = InMemorySideEffectLedger()
    metadata = _metadata()

    record = ledger.record_started(**metadata)

    assert ledger.get(metadata["side_effect_id"]) == record
    assert record.status == SideEffectStatus.STARTED
    assert record.skill_run_id == "run-123"
    assert record.step_id == "post_comment"
    assert record.tool_name == "github_issue_comment_boundary"
    assert record.validated_arguments_hash == metadata["validated_arguments_hash"]
    assert record.created_at.tzinfo is not None
    assert record.updated_at.tzinfo is not None


def test_duplicate_side_effect_id_returns_existing_record() -> None:
    ledger = InMemorySideEffectLedger()
    metadata = _metadata()

    first = ledger.record_started(**metadata)
    second = ledger.record_started(**metadata)

    assert second == first
    assert len({first.side_effect_id, second.side_effect_id}) == 1


def test_record_success_can_be_retrieved_and_suppresses_duplicate_execution() -> None:
    ledger = InMemorySideEffectLedger()
    metadata = _metadata()
    ledger.record_started(**metadata)

    succeeded = ledger.record_succeeded(
        metadata["side_effect_id"],
        external_result={"comment_id": "fake-comment-1"},
    )

    assert succeeded.status == SideEffectStatus.SUCCEEDED
    assert succeeded.external_result == {"comment_id": "fake-comment-1"}
    assert succeeded.failure is None
    assert ledger.get(metadata["side_effect_id"]) == succeeded
    assert ledger.has_succeeded(metadata["side_effect_id"]) is True


def test_record_failure_can_be_retrieved() -> None:
    ledger = InMemorySideEffectLedger()
    metadata = _metadata()
    ledger.record_started(**metadata)

    failed = ledger.record_failed(
        metadata["side_effect_id"],
        failure={"error_type": "rate_limited", "retryable": True},
    )

    assert failed.status == SideEffectStatus.FAILED
    assert failed.failure == {"error_type": "rate_limited", "retryable": True}
    assert ledger.get(metadata["side_effect_id"]) == failed
    assert ledger.has_succeeded(metadata["side_effect_id"]) is False


def test_success_or_failure_requires_existing_started_record() -> None:
    ledger = InMemorySideEffectLedger()

    with pytest.raises(KeyError, match="Unknown side effect"):
        ledger.record_succeeded("missing")

    with pytest.raises(KeyError, match="Unknown side effect"):
        ledger.record_failed("missing", failure={"error_type": "missing"})
