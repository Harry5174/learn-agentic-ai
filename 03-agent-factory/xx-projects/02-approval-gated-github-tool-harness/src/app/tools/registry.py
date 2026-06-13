from collections.abc import Callable
from inspect import signature
from typing import Any

from app.tools.dry_run_tools import (
    draft_issue_comment,
    inspect_sandbox_issues,
    trigger_workflow_dry_run,
)
from app.tools.context import ToolExecutionContext
from app.tools.errors import UnknownToolError
from app.tools.github_comment import (
    GITHUB_COMMENT_REQUIRED_SCOPE,
    GITHUB_COMMENT_TOOL_NAME,
    post_github_issue_comment,
)
from app.tools.schemas import RiskLevel, ToolExecutionResult, ToolSpec

ToolFunction = Callable[
    [dict[str, Any], ToolExecutionContext | None],
    ToolExecutionResult,
]
LegacyToolFunction = Callable[[dict[str, Any]], ToolExecutionResult]


class RegisteredTool:
    """Registered dry-run tool with metadata and executable function."""

    def __init__(self, spec: ToolSpec, function: ToolFunction) -> None:
        self.spec = spec
        self.function = function


class ToolRegistry:
    """Controlled registry for approved dry-run tools."""

    def __init__(self) -> None:
        self._tools: dict[str, RegisteredTool] = {}

    def register(
        self,
        spec: ToolSpec,
        function: ToolFunction | LegacyToolFunction,
    ) -> None:
        self._tools[spec.name] = RegisteredTool(
            spec=spec,
            function=_coerce_tool_function(function),
        )

    def list_tools(self) -> list[ToolSpec]:
        return [registered_tool.spec for registered_tool in self._tools.values()]

    def get_tool(self, tool_name: str) -> ToolSpec:
        registered_tool = self._tools.get(tool_name)

        if registered_tool is None:
            raise UnknownToolError(f"Unknown tool: {tool_name}")

        return registered_tool.spec

    def execute(
        self,
        tool_name: str,
        arguments: dict[str, Any] | None = None,
        context: ToolExecutionContext | None = None,
    ) -> ToolExecutionResult:
        registered_tool = self._tools.get(tool_name)

        if registered_tool is None:
            raise UnknownToolError(f"Unknown tool: {tool_name}")

        return registered_tool.function(arguments or {}, context)


def build_default_tool_registry() -> ToolRegistry:
    """Build the default V1 dry-run tool registry."""

    registry = ToolRegistry()

    registry.register(
        ToolSpec(
            name="inspect_sandbox_issues",
            description="Return predictable sandbox issue status data.",
            required_scopes=["tools:inspect"],
            risk_level=RiskLevel.LOW,
        ),
        inspect_sandbox_issues,
    )

    registry.register(
        ToolSpec(
            name="draft_issue_comment",
            description="Produce a dry-run issue comment draft without posting.",
            required_scopes=["tools:draft"],
            risk_level=RiskLevel.MEDIUM,
        ),
        draft_issue_comment,
    )

    registry.register(
        ToolSpec(
            name="trigger_workflow_dry_run",
            description="Simulate a high-risk workflow trigger without executing it.",
            required_scopes=["tools:trigger_workflow"],
            risk_level=RiskLevel.HIGH,
        ),
        trigger_workflow_dry_run,
    )

    registry.register(
        ToolSpec(
            name=GITHUB_COMMENT_TOOL_NAME,
            description=(
                "Simulate an approval-gated GitHub issue comment through the "
                "local fake client."
            ),
            required_scopes=[GITHUB_COMMENT_REQUIRED_SCOPE],
            risk_level=RiskLevel.HIGH,
        ),
        post_github_issue_comment,
    )

    return registry


def _coerce_tool_function(
    function: ToolFunction | LegacyToolFunction,
) -> ToolFunction:
    if len(signature(function).parameters) == 1:

        def wrapped(
            arguments: dict[str, Any],
            context: ToolExecutionContext | None,
        ) -> ToolExecutionResult:
            del context
            return function(arguments)

        return wrapped

    return function
