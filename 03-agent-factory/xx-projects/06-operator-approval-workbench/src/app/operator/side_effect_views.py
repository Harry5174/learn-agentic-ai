from typing import Any

from app.api.operator_schemas import (
    OperatorExecutionModeResponse,
    OperatorSideEffectLedgerResponse,
)
from app.operator.approval_actions import _args_hash, _side_effect_id
from app.operator.audit_views import safe_mapping, safe_text
from app.skill_graph.service import SkillGraphService
from app.skill_graph.state import SkillGraphState
from app.tools.schemas import ToolExecutionResult


class OperatorSideEffectViewNotFoundError(Exception):
    """Raised when local/demo side-effect visibility cannot find evidence."""


class OperatorSideEffectView:
    """Build read-only local/demo side-effect views from known run state."""

    def __init__(self, skill_run_service: SkillGraphService) -> None:
        self._skill_run_service = skill_run_service

    def get_side_effect(
        self,
        side_effect_id: str,
    ) -> OperatorSideEffectLedgerResponse:
        for state in self._skill_run_service.list_runs():
            response = _side_effect_from_state(state, side_effect_id)
            if response is not None:
                return response

        raise OperatorSideEffectViewNotFoundError(
            f"Side effect not found: {side_effect_id}"
        )


def _side_effect_from_state(
    state: SkillGraphState,
    side_effect_id: str,
) -> OperatorSideEffectLedgerResponse | None:
    for result in state.get("tool_results", []):
        result_side_effect_id = _result_string(result, "side_effect_id")
        if result_side_effect_id == side_effect_id:
            return _response_from_tool_result(state, result, side_effect_id)

    if _side_effect_id(state) == side_effect_id:
        return _response_from_known_run_without_record(state, side_effect_id)

    for event in state.get("audit_trail", []):
        event_side_effect_id = event.metadata.get("side_effect_id")
        if event_side_effect_id == side_effect_id:
            return _response_from_audit_metadata(state, side_effect_id, event.metadata)

    return None


def _response_from_tool_result(
    state: SkillGraphState,
    result: ToolExecutionResult,
    side_effect_id: str,
) -> OperatorSideEffectLedgerResponse:
    result_payload = safe_mapping(result.result)
    status = _string_value(result_payload.get("side_effect_status"))

    return OperatorSideEffectLedgerResponse(
        side_effect_id=safe_text(side_effect_id) or "[redacted]",
        run_id=state["run_id"],
        tool_name=result.tool_name,
        repository=_string_value(result_payload.get("repository")),
        issue_number=_int_value(result_payload.get("issue_number")),
        args_hash=_string_value(result_payload.get("validated_arguments_hash")),
        status=status,
        ledger_status=status,
        record_available=True,
        source="tool_result",
        external_result_summary=_external_result_summary(result_payload),
        error_summary=_error_summary(result_payload, result.message),
        duplicate_status=_duplicate_status(result_payload),
        execution_mode=OperatorExecutionModeResponse(),
        message="Local/demo side-effect evidence is available from run state.",
    )


def _response_from_known_run_without_record(
    state: SkillGraphState,
    side_effect_id: str,
) -> OperatorSideEffectLedgerResponse:
    target = _target_from_state(state)

    return OperatorSideEffectLedgerResponse(
        side_effect_id=safe_text(side_effect_id) or "[redacted]",
        run_id=state["run_id"],
        tool_name=_tool_name(state),
        repository=target.get("repository"),
        issue_number=_int_value(target.get("issue_number")),
        args_hash=safe_text(_args_hash(state)),
        status="not_executed",
        ledger_status="not_available",
        record_available=False,
        source="computed_local_demo_identity",
        external_result_summary=None,
        error_summary=None,
        duplicate_status=None,
        execution_mode=OperatorExecutionModeResponse(),
        message=(
            "Side-effect identity is known for this local/demo run, but no "
            "ledger record is available in the current visibility state."
        ),
    )


def _response_from_audit_metadata(
    state: SkillGraphState,
    side_effect_id: str,
    metadata: dict[str, Any],
) -> OperatorSideEffectLedgerResponse:
    safe_metadata = safe_mapping(metadata)
    status = _string_value(safe_metadata.get("side_effect_status"))

    return OperatorSideEffectLedgerResponse(
        side_effect_id=safe_text(side_effect_id) or "[redacted]",
        run_id=state["run_id"],
        tool_name=_string_value(safe_metadata.get("tool_name")) or _tool_name(state),
        repository=_string_value(safe_metadata.get("repository")),
        issue_number=_int_value(safe_metadata.get("issue_number")),
        args_hash=_string_value(safe_metadata.get("validated_arguments_hash")),
        status=status,
        ledger_status=status or "audit_metadata_only",
        record_available=False,
        source="audit_metadata",
        external_result_summary=_external_result_summary(safe_metadata),
        error_summary=_error_summary(safe_metadata, None),
        duplicate_status=_duplicate_status(safe_metadata),
        execution_mode=OperatorExecutionModeResponse(),
        message="Local/demo side-effect evidence is available from audit metadata.",
    )


def _external_result_summary(payload: dict[str, Any]) -> dict[str, Any] | None:
    allowed_keys = (
        "mode",
        "persistence",
        "repository",
        "issue_number",
        "comment_id",
        "status",
        "side_effect_status",
        "ledger_hit",
        "ledger_miss",
        "approval_checked",
        "client_called",
        "skipped",
        "duplicate_suppressed",
        "remote_reconciled",
        "replay_outcome",
    )
    summary = {key: payload[key] for key in allowed_keys if key in payload}
    cached = payload.get("cached_external_result")
    if isinstance(cached, dict):
        summary["cached_external_result"] = safe_mapping(cached)
    return summary or None


def _error_summary(
    payload: dict[str, Any],
    message: str | None,
) -> dict[str, Any] | None:
    allowed_keys = (
        "error_type",
        "retryable",
        "skip_reason",
        "failure_message",
    )
    summary = {key: payload[key] for key in allowed_keys if key in payload}
    cached = payload.get("cached_failure") or payload.get("failure")
    if isinstance(cached, dict):
        summary["failure"] = safe_mapping(cached)
    if message is not None and payload.get("error_type") is not None:
        summary["message"] = safe_text(message)
    return summary or None


def _duplicate_status(payload: dict[str, Any]) -> str | None:
    if payload.get("duplicate_suppressed") is True:
        return "duplicate_suppressed"
    if payload.get("skipped") is True:
        return _string_value(payload.get("skip_reason")) or "skipped"
    if payload.get("ledger_hit") is True:
        return "ledger_hit"
    if payload.get("ledger_miss") is True:
        return "ledger_miss"
    return None


def _target_from_state(state: SkillGraphState) -> dict[str, Any]:
    approval_request = state.get("approval_request")
    if approval_request is not None:
        return safe_mapping(approval_request.tool_arguments)

    for result in state.get("tool_results", []):
        result_payload = safe_mapping(result.result)
        if "repository" in result_payload or "issue_number" in result_payload:
            return result_payload

    return {}


def _tool_name(state: SkillGraphState) -> str | None:
    approval_request = state.get("approval_request")
    if approval_request is not None:
        return approval_request.tool_name

    tool_results = list(state.get("tool_results", []))
    if tool_results:
        return tool_results[0].tool_name

    return None


def _result_string(result: ToolExecutionResult, key: str) -> str | None:
    value = result.result.get(key)
    return value if isinstance(value, str) else None


def _string_value(value: Any) -> str | None:
    return value if isinstance(value, str) else None


def _int_value(value: Any) -> int | None:
    return value if isinstance(value, int) else None
