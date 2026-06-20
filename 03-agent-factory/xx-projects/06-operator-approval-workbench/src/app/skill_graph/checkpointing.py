from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer

from app.approval.schemas import ApprovalDecision, ApprovalRequest, ApprovalStatus
from app.audit.schemas import AuditEvent, AuditEventType
from app.identity.schemas import IdentityContext, Role
from app.policy.schemas import PolicyDecision, PolicyDecisionType
from app.skills.argument_schemas import ArgumentValidationStatus, ArgumentValueType
from app.skills.schemas import (
    ProposalValidationResult,
    ProposalValidationStatus,
    SkillProposal,
    SkillRunResult,
    SkillRunStatus,
)
from app.state.schemas import TaskStatus
from app.tools.schemas import RiskLevel, ToolExecutionResult

_SKILL_GRAPH_MSGPACK_ALLOWLIST = (
    Role,
    IdentityContext,
    TaskStatus,
    PolicyDecisionType,
    PolicyDecision,
    AuditEventType,
    AuditEvent,
    RiskLevel,
    SkillProposal,
    ProposalValidationStatus,
    ArgumentValueType,
    ArgumentValidationStatus,
    ProposalValidationResult,
    ApprovalRequest,
    ToolExecutionResult,
    ApprovalStatus,
    ApprovalDecision,
    SkillRunStatus,
    SkillRunResult,
)


def build_skill_graph_checkpointer() -> InMemorySaver:
    """Build the local/demo skill graph checkpointer with explicit state types.

    This allowlist is scoped to project-owned graph-state objects. It does not
    enable live GitHub, change approval semantics, or change identity semantics.
    """

    serde = JsonPlusSerializer(
        allowed_msgpack_modules=_SKILL_GRAPH_MSGPACK_ALLOWLIST,
    )
    return InMemorySaver(serde=serde)
