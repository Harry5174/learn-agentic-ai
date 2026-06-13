from uuid import uuid4

from langgraph.types import Command

from app.approval.schemas import ApprovalDecision, ApprovalStatus
from app.audit.schemas import AuditEvent
from app.graph.builder import build_harness_graph
from app.graph.state import HarnessGraphState
from app.identity.schemas import IdentityContext
from app.state.schemas import TaskStatus


class TaskNotFoundError(Exception):
    """Raised when a task checkpoint cannot be found."""


class TaskNotPausedError(Exception):
    """Raised when approval/rejection is requested for a non-paused task."""


class HarnessGraphService:
    """Thin service wrapper around the checkpointed local graph."""

    def __init__(self) -> None:
        self._graph = build_harness_graph()

    @staticmethod
    def _config(task_id: str) -> dict:
        return {"configurable": {"thread_id": task_id}}

    @staticmethod
    def _values_to_state(values: dict) -> HarnessGraphState:
        return HarnessGraphState(**values)

    def start_task(self, user_query: str, identity: IdentityContext) -> HarnessGraphState:
        """Start a new task and return its current graph state."""

        task_id = str(uuid4())
        initial_state: HarnessGraphState = {
            "task_id": task_id,
            "user_query": user_query,
            "identity": identity,
            "audit_trail": [],
        }

        self._graph.invoke(initial_state, config=self._config(task_id))
        return self.get_task(task_id)

    def get_task(self, task_id: str) -> HarnessGraphState:
        """Return the current checkpointed state for a task."""

        state_snapshot = self._graph.get_state(self._config(task_id))

        if not state_snapshot.values:
            raise TaskNotFoundError(f"Task not found: {task_id}")

        return self._values_to_state(state_snapshot.values)

    def approve_task(
        self,
        task_id: str,
        approver: IdentityContext,
        reason: str = "Approved via API.",
    ) -> HarnessGraphState:
        """Resume a paused task with an approval decision."""

        return self._resume_with_status(
            task_id=task_id,
            actor=approver,
            status=ApprovalStatus.APPROVED,
            reason=reason,
        )

    def reject_task(
        self,
        task_id: str,
        rejector: IdentityContext,
        reason: str = "Rejected via API.",
    ) -> HarnessGraphState:
        """Resume a paused task with a rejection decision."""

        return self._resume_with_status(
            task_id=task_id,
            actor=rejector,
            status=ApprovalStatus.REJECTED,
            reason=reason,
        )

    def get_audit(self, task_id: str) -> list[AuditEvent]:
        """Return the audit trail for a task."""

        state = self.get_task(task_id)
        return list(state.get("audit_trail", []))

    def _resume_with_status(
        self,
        task_id: str,
        actor: IdentityContext,
        status: ApprovalStatus,
        reason: str,
    ) -> HarnessGraphState:
        """Resume a paused approval workflow with an external decision."""

        current_state = self.get_task(task_id)

        if current_state.get("status") != TaskStatus.PAUSED_FOR_APPROVAL:
            raise TaskNotPausedError(f"Task is not paused for approval: {task_id}")

        approval_request = current_state.get("approval_request")

        if approval_request is None:
            raise TaskNotPausedError(
                f"Task is missing approval context and cannot be resumed: {task_id}"
            )

        decision = ApprovalDecision(
            task_id=task_id,
            tool_name=approval_request.tool_name,
            decided_by=actor.user_id,
            decider_role=actor.role,
            status=status,
            reason=reason,
        )

        self._graph.invoke(
            Command(
                resume={
                    "approval_decision": decision.model_dump(mode="json"),
                    "approval_actor": actor.model_dump(mode="json"),
                }
            ),
            config=self._config(task_id),
        )

        return self.get_task(task_id)