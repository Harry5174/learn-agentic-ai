from app.identity.schemas import IdentityContext
from app.policy.schemas import PolicyDecision, PolicyDecisionType
from app.tools.schemas import RiskLevel, ToolSpec


APPROVAL_REQUEST_SCOPE = "approval:request"


def evaluate_tool_permission(
    identity: IdentityContext,
    tool: ToolSpec,
) -> PolicyDecision:
    """Evaluate whether an identity may use a tool.

    This function is pure and deterministic.

    It does not execute tools.
    It does not call an LLM.
    It does not perform approval workflow behavior.
    """

    required_scopes = list(tool.required_scopes)
    missing_scopes = [
        scope for scope in required_scopes if scope not in identity.scopes
    ]

    if tool.risk_level == RiskLevel.HIGH:
        return _evaluate_high_risk_tool(
            identity=identity,
            tool=tool,
            required_scopes=required_scopes,
            missing_scopes=missing_scopes,
        )

    if missing_scopes:
        return PolicyDecision(
            decision=PolicyDecisionType.DENY,
            tool_name=tool.name,
            reason="Identity is missing required tool scope(s).",
            required_scopes=required_scopes,
            missing_scopes=missing_scopes,
        )

    return PolicyDecision(
        decision=PolicyDecisionType.ALLOW,
        tool_name=tool.name,
        reason="Identity has required tool scope(s).",
        required_scopes=required_scopes,
        missing_scopes=[],
    )


def _evaluate_high_risk_tool(
    identity: IdentityContext,
    tool: ToolSpec,
    required_scopes: list[str],
    missing_scopes: list[str],
) -> PolicyDecision:
    has_required_tool_scope = not missing_scopes
    can_request_approval = APPROVAL_REQUEST_SCOPE in identity.scopes

    if has_required_tool_scope or can_request_approval:
        return PolicyDecision(
            decision=PolicyDecisionType.REQUIRE_APPROVAL,
            tool_name=tool.name,
            reason="High-risk tool requires approval before execution.",
            required_scopes=required_scopes,
            missing_scopes=missing_scopes,
        )

    return PolicyDecision(
        decision=PolicyDecisionType.DENY,
        tool_name=tool.name,
        reason=(
            "Identity is not eligible to request or execute this high-risk tool."
        ),
        required_scopes=required_scopes,
        missing_scopes=missing_scopes,
    )