import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

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
)


VALID_ARGUMENTS = {
    "repository": "Harry5174/learn-agentic-ai",
    "issue_number": 1,
    "comment_body": "A deterministic durable fake GitHub comment.",
}


def stores(
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


def context(
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


def context_for_identity_only() -> ToolExecutionContext:
    return ToolExecutionContext(
        run_id="run-durable-1",
        step_id=GITHUB_COMMENT_STEP_ID,
    )


def persist_approved_action(
    ledger: DurableSideEffectLedger,
    approval_store: DurableApprovalBindingStore,
    *,
    run_id: str = "run-durable-1",
    approval_id: str = "approval-durable-1",
    arguments: dict[str, Any] | None = None,
) -> tuple[str, str]:
    active_arguments = arguments or VALID_ARGUMENTS
    side_effect_id = persist_planned_action(
        ledger,
        run_id=run_id,
        arguments=active_arguments,
    )
    argument_hash = validated_arguments_hash(active_arguments)
    approval_store.create_pending(
        binding(
            approval_id=approval_id,
            side_effect_id=side_effect_id,
            argument_hash=argument_hash,
            run_id=run_id,
        )
    )
    approval_store.approve(approval_id, decided_by="admin_1")

    return side_effect_id, argument_hash


def persist_planned_action(
    ledger: DurableSideEffectLedger,
    *,
    run_id: str = "run-durable-1",
    arguments: dict[str, Any] | None = None,
) -> str:
    active_arguments = arguments or VALID_ARGUMENTS
    argument_hash = validated_arguments_hash(active_arguments)
    side_effect_id = side_effect_id_for(run_id, active_arguments)
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
            comment_body_hash=comment_body_hash(
                str(active_arguments["comment_body"])
            ),
            comment_body_preview=str(active_arguments["comment_body"])[:80],
            created_at=now(),
            updated_at=now(),
        )
    )

    return side_effect_id


def persist_action_with_status(
    ledger: DurableSideEffectLedger,
    approval_store: DurableApprovalBindingStore,
    status: DurableSideEffectStatus,
) -> str:
    if status in {
        DurableSideEffectStatus.BLOCKED,
        DurableSideEffectStatus.REJECTED,
    }:
        side_effect_id = persist_planned_action(ledger)
        if status == DurableSideEffectStatus.BLOCKED:
            ledger.mark_blocked(side_effect_id, reason="Blocked for status test.")
        else:
            ledger.mark_rejected(side_effect_id, reason="Rejected for status test.")
        return side_effect_id

    side_effect_id, _ = persist_approved_action(ledger, approval_store)
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


def binding(
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
        created_at=now(),
    )


def side_effect_id_for(
    run_id: str = "run-durable-1",
    arguments: dict[str, Any] | None = None,
) -> str:
    return build_side_effect_id(
        skill_run_id=run_id,
        step_id=GITHUB_COMMENT_STEP_ID,
        tool_name=GITHUB_COMMENT_TOOL_NAME,
        validated_arguments_hash=validated_arguments_hash(arguments or VALID_ARGUMENTS),
    )


def argument_hash() -> str:
    return validated_arguments_hash(VALID_ARGUMENTS)


def comment_body_hash(comment_body: str) -> str:
    return hashlib.sha256(comment_body.encode("utf-8")).hexdigest()


def now() -> str:
    return datetime.now(timezone.utc).isoformat()
