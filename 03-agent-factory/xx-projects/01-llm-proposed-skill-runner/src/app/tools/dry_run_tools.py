from typing import Any

from app.tools.schemas import ToolExecutionResult


def inspect_sandbox_issues(arguments: dict[str, Any]) -> ToolExecutionResult:
    """Return predictable sandbox issue data.

    No external calls are made.
    """

    return ToolExecutionResult(
        tool_name="inspect_sandbox_issues",
        success=True,
        dry_run=True,
        result={
            "repository": arguments.get("repository", "sandbox/demo-repo"),
            "issues": [
                {"id": 1, "title": "CI workflow failing", "status": "open"},
                {"id": 2, "title": "Dependency update needed", "status": "open"},
            ],
        },
        message="Returned sandbox issue data.",
    )


def draft_issue_comment(arguments: dict[str, Any]) -> ToolExecutionResult:
    """Return a dry-run issue comment payload.

    No comment is posted.
    """

    issue_id = arguments.get("issue_id")
    comment_body = arguments.get("comment_body", "")

    return ToolExecutionResult(
        tool_name="draft_issue_comment",
        success=True,
        dry_run=True,
        result={
            "issue_id": issue_id,
            "comment_body": comment_body,
            "would_post": False,
        },
        message="Generated dry-run issue comment payload.",
    )


def trigger_workflow_dry_run(arguments: dict[str, Any]) -> ToolExecutionResult:
    """Return a simulated workflow trigger response.

    No workflow is triggered.
    """

    workflow_name = arguments.get("workflow_name", "ci.yml")
    ref = arguments.get("ref", "main")

    return ToolExecutionResult(
        tool_name="trigger_workflow_dry_run",
        success=True,
        dry_run=True,
        result={
            "workflow_name": workflow_name,
            "ref": ref,
            "would_trigger": False,
            "simulated_status": "queued",
        },
        message="Simulated workflow trigger in dry-run mode.",
    )