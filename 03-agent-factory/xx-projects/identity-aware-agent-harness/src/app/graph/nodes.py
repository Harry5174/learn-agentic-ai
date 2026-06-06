from typing import Any

from app.approval.schemas import ApprovalRequest
from app.audit.logger import (
    append_audit_event,
    create_approval_requested_event,
    create_audit_event,
    create_permission_checked_event,
    create_task_created_event,
    create_tool_executed_event,
    create_tool_selected_event,
)
from app.audit.schemas import AuditEvent, AuditEventType
from app.graph.state import HarnessGraphState
from app.policy.guard import evaluate_tool_permission
from app.policy.schemas import PolicyDecisionType
from app.state.schemas import TaskStatus
from app.tools.registry import build_default_tool_registry


def _audit_trail(state: HarnessGraphState) -> list[AuditEvent]:
    return list(state.get("audit_trail", []))


def _select_tool_from_query(user_query: str) -> tuple[str | None, dict[str, Any], str | None]:
    query = user_query.lower()

    if "draft" in query or "comment" in query:
        return (
            "draft_issue_comment",
            {
                "issue_id": 1,
                "comment_body": "Draft response generated from local task interpreter.",
            },
            "Query requested drafting or commenting on an issue.",
        )

    if "trigger" in query or "workflow" in query:
        return (
            "trigger_workflow_dry_run",
            {
                "workflow_name": "ci.yml",
                "ref": "main",
            },
            "Query requested triggering a workflow.",
        )

    if "inspect" in query or "issue" in query or "issues" in query:
        return (
            "inspect_sandbox_issues",
            {
                "repository": "sandbox/demo-repo",
            },
            "Query requested issue inspection.",
        )

    return None, {}, None


def interpret_task(state: HarnessGraphState) -> HarnessGraphState:
    """Deterministically select a supported tool from the user query."""

    task_id = state["task_id"]
    identity = state["identity"]
    user_query = state["user_query"]

    audit_trail = _audit_trail(state)

    if not audit_trail:
        audit_trail = append_audit_event(
            audit_trail,
            create_task_created_event(
                task_id=task_id,
                actor_id=identity.user_id,
                user_query=user_query,
            ),
        )

    selected_tool_name, tool_arguments, reason = _select_tool_from_query(user_query)

    if selected_tool_name is None:
        return {
            **state,
            "status": TaskStatus.FAILED,
            "selected_tool_name": None,
            "tool_arguments": {},
            "tool_result": None,
            "error_message": "Unable to select a supported tool.",
            "audit_trail": audit_trail,
        }

    audit_trail = append_audit_event(
        audit_trail,
        create_tool_selected_event(
            task_id=task_id,
            actor_id=identity.user_id,
            tool_name=selected_tool_name,
            reason=reason or "Tool selected by deterministic interpreter.",
        ),
    )

    return {
        **state,
        "status": TaskStatus.RUNNING,
        "selected_tool_name": selected_tool_name,
        "tool_arguments": tool_arguments,
        "audit_trail": audit_trail,
    }


def policy_guard(state: HarnessGraphState) -> HarnessGraphState:
    """Evaluate deterministic policy for the selected tool."""

    selected_tool_name = state.get("selected_tool_name")
    identity = state["identity"]
    task_id = state["task_id"]

    if selected_tool_name is None:
        return {
            **state,
            "status": TaskStatus.FAILED,
            "error_message": "No tool selected for policy evaluation.",
        }

    registry = build_default_tool_registry()
    tool = registry.get_tool(selected_tool_name)
    decision = evaluate_tool_permission(identity, tool)

    if decision.decision == PolicyDecisionType.ALLOW:
        status = TaskStatus.RUNNING
    elif decision.decision == PolicyDecisionType.DENY:
        status = TaskStatus.DENIED
    else:
        status = TaskStatus.PAUSED_FOR_APPROVAL

    audit_trail = append_audit_event(
        _audit_trail(state),
        create_permission_checked_event(
            task_id=task_id,
            actor_id=identity.user_id,
            tool_name=tool.name,
            decision=decision.decision.value,
            reason=decision.reason,
            required_scopes=decision.required_scopes,
            missing_scopes=decision.missing_scopes,
        ),
    )

    return {
        **state,
        "status": status,
        "policy_decision": decision,
        "audit_trail": audit_trail,
    }


def pause_for_approval(state: HarnessGraphState) -> HarnessGraphState:
    """Create an approval request and pause before tool execution."""

    task_id = state["task_id"]
    identity = state["identity"]
    selected_tool_name = state["selected_tool_name"]
    tool_arguments = state.get("tool_arguments", {})
    policy_decision = state["policy_decision"]

    approval_request = ApprovalRequest(
        task_id=task_id,
        tool_name=selected_tool_name,
        tool_arguments=tool_arguments,
        risk_level=build_default_tool_registry().get_tool(selected_tool_name).risk_level,
        requested_by=identity.user_id,
        reason=policy_decision.reason,
    )

    audit_trail = append_audit_event(
        _audit_trail(state),
        create_approval_requested_event(
            task_id=task_id,
            actor_id=identity.user_id,
            tool_name=selected_tool_name,
            reason=policy_decision.reason,
        ),
    )

    return {
        **state,
        "status": TaskStatus.PAUSED_FOR_APPROVAL,
        "approval_request": approval_request,
        "tool_result": None,
        "audit_trail": audit_trail,
        "final_report": "Task paused for approval before high-risk execution.",
    }


def execute_tool(state: HarnessGraphState) -> HarnessGraphState:
    """Execute an allowed dry-run tool through the controlled registry."""

    selected_tool_name = state["selected_tool_name"]
    tool_arguments = state.get("tool_arguments", {})
    identity = state["identity"]
    task_id = state["task_id"]

    registry = build_default_tool_registry()
    result = registry.execute(selected_tool_name, tool_arguments)

    audit_trail = append_audit_event(
        _audit_trail(state),
        create_tool_executed_event(
            task_id=task_id,
            actor_id=identity.user_id,
            tool_name=selected_tool_name,
            dry_run=result.dry_run,
            success=result.success,
        ),
    )

    return {
        **state,
        "tool_result": result,
        "audit_trail": audit_trail,
    }


def finalize_denial(state: HarnessGraphState) -> HarnessGraphState:
    """Finalize a denied task without executing a tool."""

    decision = state["policy_decision"]

    return {
        **state,
        "status": TaskStatus.DENIED,
        "tool_result": None,
        "final_report": f"Task denied: {decision.reason}",
    }


def generate_report(state: HarnessGraphState) -> HarnessGraphState:
    """Generate a deterministic final report."""

    status = state.get("status")
    task_id = state["task_id"]
    identity = state["identity"]

    if status == TaskStatus.FAILED:
        return {
            **state,
            "final_report": f"Task failed: {state.get('error_message')}",
        }

    if status == TaskStatus.DENIED:
        return state

    audit_trail = append_audit_event(
        _audit_trail(state),
        create_audit_event(
            task_id=task_id,
            event_type=AuditEventType.TASK_COMPLETED,
            actor_id=identity.user_id,
            message="Task completed.",
        ),
    )

    return {
        **state,
        "status": TaskStatus.COMPLETED,
        "final_report": "Task completed successfully using dry-run execution.",
        "audit_trail": audit_trail,
    }