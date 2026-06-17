from dataclasses import dataclass

from app.audit.durable_store import DurableAuditStore
from app.github.client import (
    GitHubIssueCommentClient,
    GitHubIssueCommentRemoteClient,
)
from app.github.real_mode import GitHubRealModeConfig
from app.github.token_provider import GitHubTokenProvider
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
    real_github_issue_comment_client: GitHubIssueCommentRemoteClient | None = None
    github_real_mode_config: GitHubRealModeConfig | None = None
    github_token_provider: GitHubTokenProvider | None = None
    durable_side_effect_ledger: DurableSideEffectLedger | None = None
    durable_approval_binding_store: DurableApprovalBindingStore | None = None
    durable_audit_store: DurableAuditStore | None = None
