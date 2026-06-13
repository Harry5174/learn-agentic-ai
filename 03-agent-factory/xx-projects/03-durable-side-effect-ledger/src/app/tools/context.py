from dataclasses import dataclass

from app.github.client import GitHubIssueCommentClient
from app.side_effects.ledger import SideEffectLedger


@dataclass(frozen=True)
class ToolExecutionContext:
    """Graph-owned execution context for tools that need side-effect boundaries."""

    run_id: str
    step_id: str
    side_effect_ledger: SideEffectLedger | None = None
    github_issue_comment_client: GitHubIssueCommentClient | None = None
