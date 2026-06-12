from uuid import uuid4

from langgraph.types import Command

from app.approval.schemas import ApprovalDecision, ApprovalStatus
from app.audit.schemas import AuditEvent
from app.identity.schemas import IdentityContext
from app.proposer.base import SkillProposer
from app.skill_graph.graph import build_skill_execution_graph
from app.skill_graph.state import SkillGraphState
from app.state.schemas import TaskStatus


class SkillRunNotFoundError(Exception):
    """Raised when a skill-run checkpoint cannot be found."""


class SkillRunNotPausedError(Exception):
    """Raised when approval/rejection is requested for a non-paused run."""


class SkillGraphService:
    """Thin service wrapper around the checkpointed skill execution graph."""

    def __init__(self, proposer: SkillProposer | None = None) -> None:
        self._graph = build_skill_execution_graph(proposer=proposer)

    @staticmethod
    def _config(run_id: str) -> dict:
        return {"configurable": {"thread_id": run_id}}

    @staticmethod
    def _values_to_state(values: dict) -> SkillGraphState:
        return SkillGraphState(**values)

    def start_run(self, task: str, identity: IdentityContext) -> SkillGraphState:
        """Start a new proposed skill run and return its current graph state."""

        run_id = str(uuid4())
        initial_state: SkillGraphState = {
            "run_id": run_id,
            "task": task,
            "identity": identity,
            "status": TaskStatus.CREATED,
            "policy_decisions": [],
            "step_arguments": {},
            "tool_results": [],
            "audit_trail": [],
        }

        self._graph.invoke(initial_state, config=self._config(run_id))
        return self.get_run(run_id)

    def get_run(self, run_id: str) -> SkillGraphState:
        """Return the current checkpointed state for a skill run."""

        state_snapshot = self._graph.get_state(self._config(run_id))

        if not state_snapshot.values:
            raise SkillRunNotFoundError(f"Skill run not found: {run_id}")

        return self._values_to_state(state_snapshot.values)

    def approve_run(
        self,
        run_id: str,
        approver: IdentityContext,
        reason: str = "Approved via skill graph service.",
    ) -> SkillGraphState:
        """Resume a paused skill run with an approval decision."""

        return self._resume_with_status(
            run_id=run_id,
            actor=approver,
            status=ApprovalStatus.APPROVED,
            reason=reason,
        )

    def reject_run(
        self,
        run_id: str,
        rejector: IdentityContext,
        reason: str = "Rejected via skill graph service.",
    ) -> SkillGraphState:
        """Resume a paused skill run with a rejection decision."""

        return self._resume_with_status(
            run_id=run_id,
            actor=rejector,
            status=ApprovalStatus.REJECTED,
            reason=reason,
        )

    def get_audit(self, run_id: str) -> list[AuditEvent]:
        """Return the audit trail for a skill run."""

        state = self.get_run(run_id)
        return list(state.get("audit_trail", []))

    def _resume_with_status(
        self,
        run_id: str,
        actor: IdentityContext,
        status: ApprovalStatus,
        reason: str,
    ) -> SkillGraphState:
        current_state = self.get_run(run_id)

        if current_state.get("status") != TaskStatus.PAUSED_FOR_APPROVAL:
            raise SkillRunNotPausedError(
                f"Skill run is not paused for approval: {run_id}"
            )

        approval_request = current_state.get("approval_request")

        if approval_request is None:
            raise SkillRunNotPausedError(
                f"Skill run is missing approval context: {run_id}"
            )

        decision = ApprovalDecision(
            task_id=run_id,
            tool_name=approval_request.tool_name,
            status=status,
            decided_by=actor.user_id,
            decider_role=actor.role,
            reason=reason,
        )

        self._graph.invoke(
            Command(
                resume={
                    "approval_decision": decision.model_dump(mode="json"),
                    "approval_actor": actor.model_dump(mode="json"),
                }
            ),
            config=self._config(run_id),
        )

        return self.get_run(run_id)
