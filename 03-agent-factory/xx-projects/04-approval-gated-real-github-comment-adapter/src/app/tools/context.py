from dataclasses import dataclass

from app.audit.durable_store import DurableAuditStore
from app.github.client import GitHubIssueCommentClient
from app.side_effects.approval_binding import DurableApprovalBindingStore
from app.side_effects.durable_ledger import DurableSideEffectLedger
from app.side_effects.ledger import SideEffectLedger


@dataclass(frozen=True)
class ToolExecutionContext:
    """Graph-owned execution context for tools that need side-effect boundaries."""

    run_id: str
    step_id: str
    side_effect_ledger: SideEffectLedger | None = None
    github_issue_comment_client: GitHubIssueCommentClient | None = None
    durable_side_effect_ledger: DurableSideEffectLedger | None = None
    durable_approval_binding_store: DurableApprovalBindingStore | None = None
    durable_audit_store: DurableAuditStore | None = None
