import math
from typing import Any

from app.api.operator_schemas import (
    OperatorApprovalAuditResponse,
    OperatorAuditTimelineEventResponse,
    OperatorDecisionHistoryItemResponse,
)
from app.approval.schemas import ApprovalStatus
from app.audit.schemas import AuditEvent
from app.identity.schemas import Role
from app.skill_graph.service import SkillGraphService, SkillRunNotFoundError
from app.skill_graph.state import SkillGraphState

SENSITIVE_KEY_PARTS = (
    "authorization",
    "bearer",
    "token",
    "secret",
    "password",
    "credential",
    "api_key",
    "apikey",
    ".env",
)
SENSITIVE_VALUE_PARTS = (
    "ghp_",
    "github_pat_",
    "gho_",
    "ghu_",
    "ghs_",
    "ghr_",
    "bearer ",
    "github_access_token=",
    "agent_factory_github_token=",
)


class OperatorAuditViewNotFoundError(Exception):
    """Raised when local/demo audit visibility cannot find a run."""


class OperatorAuditView:
    """Build read-only local/demo audit views from skill-run state."""

    def __init__(self, skill_run_service: SkillGraphService) -> None:
        self._skill_run_service = skill_run_service

    def get_audit(self, approval_id: str) -> OperatorApprovalAuditResponse:
        try:
            state = self._skill_run_service.get_run(approval_id)
        except SkillRunNotFoundError as exc:
            raise OperatorAuditViewNotFoundError(
                f"Approval not found: {approval_id}"
            ) from exc

        audit_trail = list(state.get("audit_trail", []))
        return OperatorApprovalAuditResponse(
            approval_id=approval_id,
            run_id=state["run_id"],
            events=audit_timeline_events(audit_trail),
            decision_history=decision_history_from_state(state),
        )


def audit_timeline_events(
    audit_trail: list[AuditEvent],
) -> list[OperatorAuditTimelineEventResponse]:
    return [
        OperatorAuditTimelineEventResponse(
            sequence=index + 1,
            event_id=event.event_id,
            event_type=event.event_type.value,
            actor_id=safe_text(event.actor_id),
            timestamp=event.timestamp,
            tool_name=safe_text(event.tool_name),
            message=safe_text(event.message) or "",
            metadata=safe_mapping(event.metadata),
        )
        for index, event in enumerate(audit_trail)
    ]


def decision_history_from_state(
    state: SkillGraphState,
) -> list[OperatorDecisionHistoryItemResponse]:
    audit_trail = list(state.get("audit_trail", []))
    decisions = [
        OperatorDecisionHistoryItemResponse(
            decision=_decision_for_event(event),
            actor_id=safe_text(event.actor_id),
            reason=safe_text(_metadata_string(event.metadata, "reason")),
            timestamp=event.timestamp,
            event_id=event.event_id,
        )
        for event in audit_trail
        if event.event_type.value in {"approval_granted", "approval_rejected"}
    ]

    if decisions:
        return decisions

    approval_decision = state.get("approval_decision")
    if approval_decision is None:
        return []

    approval_actor = state.get("approval_actor")
    actor_role: Role | None = None
    actor_id = safe_text(approval_decision.decided_by)
    if approval_actor is not None:
        actor_role = approval_actor.role
        actor_id = safe_text(approval_actor.user_id)

    return [
        OperatorDecisionHistoryItemResponse(
            decision=approval_decision.status.value,
            actor_id=actor_id,
            actor_role=actor_role,
            reason=safe_text(approval_decision.reason),
        )
    ]


def approval_status_from_state(state: SkillGraphState) -> str:
    approval_decision = state.get("approval_decision")
    if approval_decision is not None:
        if approval_decision.status == ApprovalStatus.APPROVED:
            return "approved"
        if approval_decision.status == ApprovalStatus.REJECTED:
            return "rejected"

    if state.get("approval_request") is not None:
        return "pending"

    return "not_required"


def safe_mapping(metadata: dict[str, Any]) -> dict[str, Any]:
    safe: dict[str, Any] = {}

    for key, value in metadata.items():
        if not isinstance(key, str) or is_sensitive_key(key):
            continue

        safe[key] = safe_json_value(value)

    return safe


def safe_json_value(value: Any) -> Any:
    if isinstance(value, str):
        return safe_text(value)

    if isinstance(value, bool) or isinstance(value, int) or value is None:
        return value

    if isinstance(value, float):
        return value if math.isfinite(value) else None

    if isinstance(value, list):
        return [safe_json_value(item) for item in value]

    if isinstance(value, dict):
        return safe_mapping(value)

    return "[redacted]"


def safe_text(value: str | None) -> str | None:
    if value is None:
        return None

    if contains_sensitive_value(value):
        return "[redacted]"

    return value


def is_sensitive_key(key: str) -> bool:
    normalized = key.lower()
    return any(part in normalized for part in SENSITIVE_KEY_PARTS)


def contains_sensitive_value(value: str) -> bool:
    normalized = value.lower()
    return any(part in normalized for part in SENSITIVE_VALUE_PARTS)


def _decision_for_event(event: AuditEvent) -> str:
    if event.event_type.value == "approval_granted":
        return "approved"
    return "rejected"


def _metadata_string(metadata: dict[str, Any], key: str) -> str | None:
    value = metadata.get(key)
    return value if isinstance(value, str) else None
