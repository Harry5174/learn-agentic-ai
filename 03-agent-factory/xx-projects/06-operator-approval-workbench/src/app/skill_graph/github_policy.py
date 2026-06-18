from typing import Any

from app.policy.schemas import PolicyDecision, PolicyDecisionType
from app.tools.github_comment import repository_is_allowed


def apply_github_comment_repository_policy(
    *,
    decision: PolicyDecision,
    tool_name: str,
    required_scopes: list[str],
    arguments: dict[str, Any],
    allowed_repositories: tuple[str, ...],
) -> tuple[PolicyDecision, dict[str, Any]]:
    repository = arguments.get("repository")
    repository_allowed = (
        isinstance(repository, str)
        and repository_is_allowed(repository, allowed_repositories)
    )
    metadata = {
        "kind": "github_comment_policy",
        "github_comment_audit_concept": (
            "github_comment_policy_allowed"
            if repository_allowed
            else "github_comment_policy_denied"
        ),
        "repository": repository,
        "allowed_repositories": list(allowed_repositories),
        "repository_allowed": repository_allowed,
        "client_called": False,
    }

    if decision.decision == PolicyDecisionType.DENY:
        metadata["github_comment_audit_concept"] = "github_comment_policy_denied"
        return decision, metadata

    if not repository_allowed:
        return (
            PolicyDecision(
                decision=PolicyDecisionType.DENY,
                tool_name=tool_name,
                reason="Repository is not allowed for GitHub issue comments.",
                required_scopes=list(required_scopes),
                missing_scopes=[],
            ),
            metadata,
        )

    return decision, metadata
