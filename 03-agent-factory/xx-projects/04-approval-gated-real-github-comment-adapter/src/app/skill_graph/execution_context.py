from app.audit.durable_store import DurableAuditStore
from app.github.client import GitHubIssueCommentClient, GitHubIssueCommentRemoteClient
from app.github.real_mode import GitHubRealModeConfig
from app.github.token_provider import GitHubTokenProvider
from app.side_effects.approval_binding import DurableApprovalBindingStore
from app.side_effects.durable_ledger import DurableSideEffectLedger
from app.side_effects.ledger import SideEffectLedger
from app.tools.context import ToolExecutionContext
from app.tools.github_comment import GITHUB_COMMENT_TOOL_NAME


def github_comment_execution_context(
    *,
    run_id: str,
    step_id: str,
    tool_name: str,
    side_effect_ledger: SideEffectLedger,
    github_issue_comment_client: GitHubIssueCommentClient,
    durable_side_effect_ledger: DurableSideEffectLedger | None,
    durable_approval_binding_store: DurableApprovalBindingStore | None,
    durable_audit_store: DurableAuditStore | None = None,
    real_github_issue_comment_client: GitHubIssueCommentRemoteClient | None = None,
    github_real_mode_config: GitHubRealModeConfig | None = None,
    github_token_provider: GitHubTokenProvider | None = None,
) -> ToolExecutionContext | None:
    if tool_name != GITHUB_COMMENT_TOOL_NAME:
        return None

    return ToolExecutionContext(
        run_id=run_id,
        step_id=step_id,
        side_effect_ledger=side_effect_ledger,
        github_issue_comment_client=github_issue_comment_client,
        real_github_issue_comment_client=real_github_issue_comment_client,
        github_real_mode_config=github_real_mode_config,
        github_token_provider=github_token_provider,
        durable_side_effect_ledger=durable_side_effect_ledger,
        durable_approval_binding_store=durable_approval_binding_store,
        durable_audit_store=durable_audit_store,
    )
