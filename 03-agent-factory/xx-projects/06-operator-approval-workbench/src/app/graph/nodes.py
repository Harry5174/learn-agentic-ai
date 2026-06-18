from typing import Any

from langgraph.types import interrupt

from app.approval.schemas import ApprovalDecision, ApprovalRequest, ApprovalStatus
from app.audit.logger import (
    append_audit_event,
    create_approval_granted_event,
    create_approval_rejected_event,
    create_approval_requested_event,
    create_audit_event,
    create_permission_checked_event,
    create_task_created_event,
    create_tool_executed_event,
    create_tool_selected_event,
)
from app.audit.schemas import AuditEvent, AuditEventType
from app.graph.state import HarnessGraphState
from app.identity.schemas import IdentityContext
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


def _has_scope(identity: IdentityContext, scope: str) -> bool:
    """Return whether an identity has a required scope."""

    return scope in identity.scopes


def _coerce_approval_decision(value: Any) -> ApprovalDecision | None:
    """Convert interrupt resume value into an ApprovalDecision if possible."""

    if isinstance(value, ApprovalDecision):
        return value

    if isinstance(value, dict):
        return ApprovalDecision.model_validate(value.get("approval_decision", value))

    return None


def _coerce_approval_actor(value: Any) -> IdentityContext | None:
    """Convert interrupt resume value into an IdentityContext if possible."""

    if isinstance(value, dict):
        actor_value = value.get("approval_actor")
        if isinstance(actor_value, IdentityContext):
            return actor_value
        if isinstance(actor_value, dict):
            return IdentityContext.model_validate(actor_value)

    return None


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


def handle_approval_decision(state: HarnessGraphState) -> HarnessGraphState:
    """Interrupt graph execution and handle an external approval decision."""

    task_id = state["task_id"]
    selected_tool_name = state["selected_tool_name"]
    approval_request = state.get("approval_request")

    if approval_request is None:
        return {
            **state,
            "status": TaskStatus.FAILED,
            "resume_error": "Cannot resume approval flow without an approval request.",
            "error_message": "Cannot resume approval flow without an approval request.",
        }

    resume_value = interrupt(
        {
            "kind": "approval_required",
            "task_id": task_id,
            "tool_name": selected_tool_name,
            "approval_request": approval_request.model_dump(mode="json"),
            "message": "Approval decision required before high-risk execution.",
        }
    )

    approval_decision = _coerce_approval_decision(resume_value)
    approval_actor = _coerce_approval_actor(resume_value)

    if approval_decision is None:
        return {
            **state,
            "status": TaskStatus.FAILED,
            "resume_error": "Missing or invalid approval decision.",
            "error_message": "Missing or invalid approval decision.",
        }

    if approval_actor is None:
        return {
            **state,
            "status": TaskStatus.FAILED,
            "approval_decision": approval_decision,
            "resume_error": "Missing or invalid approval actor.",
            "error_message": "Missing or invalid approval actor.",
        }

    if approval_decision.status == ApprovalStatus.APPROVED:
        required_scope = "approval:approve"
        event_factory = create_approval_granted_event
        next_status = TaskStatus.RUNNING
    elif approval_decision.status == ApprovalStatus.REJECTED:
        required_scope = "approval:reject"
        event_factory = create_approval_rejected_event
        next_status = TaskStatus.REJECTED
    else:
        return {
            **state,
            "status": TaskStatus.FAILED,
            "approval_decision": approval_decision,
            "approval_actor": approval_actor,
            "resume_error": f"Unsupported approval decision: {approval_decision.status.value}",
            "error_message": f"Unsupported approval decision: {approval_decision.status.value}",
        }

    if not _has_scope(approval_actor, required_scope):
        return {
            **state,
            "status": TaskStatus.FAILED,
            "approval_decision": approval_decision,
            "approval_actor": approval_actor,
            "resume_error": f"Approval actor lacks required scope: {required_scope}",
            "error_message": f"Approval actor lacks required scope: {required_scope}",
            "tool_result": None,
        }

    audit_trail = append_audit_event(
        _audit_trail(state),
        event_factory(
            task_id=task_id,
            actor_id=approval_actor.user_id,
            tool_name=selected_tool_name,
            reason=approval_decision.reason,
        ),
    )

    return {
        **state,
        "status": next_status,
        "approval_decision": approval_decision,
        "approval_actor": approval_actor,
        "resume_error": None,
        "error_message": None,
        "audit_trail": audit_trail,
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


def finalize_rejection(state: HarnessGraphState) -> HarnessGraphState:
    """Finalize a rejected approval flow without executing a tool."""

    approval_decision = state.get("approval_decision")
    reason = approval_decision.reason if approval_decision else "Approval was rejected."

    return {
        **state,
        "status": TaskStatus.REJECTED,
        "tool_result": None,
        "final_report": f"Task rejected: {reason}",
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