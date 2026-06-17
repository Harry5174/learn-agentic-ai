from typing import Any

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
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
)
from app.audit.durable_store import DurableAuditStore
from app.audit.schemas import AuditEvent, AuditEventType
from app.github.client import GitHubIssueCommentClient, GitHubIssueCommentRemoteClient
from app.github.fake_client import FakeGitHubIssueCommentClient
from app.github.real_mode import GitHubRealModeConfig
from app.github.token_provider import GitHubTokenProvider
from app.identity.schemas import IdentityContext
from app.policy.guard import evaluate_tool_permission
from app.policy.schemas import PolicyDecision
from app.proposer.base import SkillProposer
from app.side_effects.approval_binding import DurableApprovalBindingStore
from app.side_effects.durable_ledger import DurableSideEffectLedger
from app.side_effects.ledger import InMemorySideEffectLedger, SideEffectLedger
from app.proposer.fake import FakeProposer
from app.skills.registry import SkillRegistry, build_default_skill_registry
from app.skills.schemas import (
    ProposalValidationStatus,
    SkillRunResult,
    SkillRunStatus,
)
from app.skills.validator import ProposalValidator
from app.skill_graph.metadata import (
    create_proposal_event,
    create_validation_event,
    github_comment_approval_metadata,
    github_comment_execution_metadata,
)
from app.skill_graph.execution_context import github_comment_execution_context
from app.skill_graph.github_policy import apply_github_comment_repository_policy
from app.skill_graph.routing import (
    route_after_approval_decision,
    route_after_execution,
    route_after_policy,
    route_after_validation,
    status_from_policy_decisions,
)
from app.skill_graph.state import SkillGraphState
from app.skill_graph.validation_helpers import (
    execution_allowed,
    first_approval_policy_decision,
    tool_arguments_for_decision,
    validation_accepted,
    validated_step_arguments_by_id,
    validated_steps,
)
from app.state.schemas import TaskStatus
from app.tools.github_comment import (
    DEFAULT_ALLOWED_GITHUB_COMMENT_REPOSITORIES,
    GITHUB_COMMENT_TOOL_NAME,
)
from app.tools.registry import ToolRegistry, build_default_tool_registry
from app.tools.schemas import ToolExecutionResult


def build_skill_execution_graph(
    proposer: SkillProposer | None = None,
    skill_registry: SkillRegistry | None = None,
    tool_registry: ToolRegistry | None = None,
    github_issue_comment_client: GitHubIssueCommentClient | None = None,
    real_github_issue_comment_client: GitHubIssueCommentRemoteClient | None = None,
    github_real_mode_config: GitHubRealModeConfig | None = None,
    github_token_provider: GitHubTokenProvider | None = None,
    side_effect_ledger: SideEffectLedger | None = None,
    durable_side_effect_ledger: DurableSideEffectLedger | None = None,
    durable_approval_binding_store: DurableApprovalBindingStore | None = None,
    durable_audit_store: DurableAuditStore | None = None,
    allowed_github_comment_repositories: tuple[str, ...] | None = None,
):
    """Build the local skill execution graph with checkpointed approval resume."""

    active_proposer = proposer or FakeProposer()
    active_skill_registry = skill_registry or build_default_skill_registry()
    active_tool_registry = tool_registry or build_default_tool_registry()
    active_github_issue_comment_client = (
        github_issue_comment_client or FakeGitHubIssueCommentClient()
    )
    active_side_effect_ledger = side_effect_ledger or InMemorySideEffectLedger()
    active_allowed_github_comment_repositories = (
        allowed_github_comment_repositories
        or DEFAULT_ALLOWED_GITHUB_COMMENT_REPOSITORIES
    )
    validator = ProposalValidator(active_skill_registry)

    def propose_skill(state: SkillGraphState) -> SkillGraphState:
        run_id = state["run_id"]
        identity = state["identity"]
        task = state["task"]
        audit_trail = _audit_trail(state)

        if not audit_trail:
            audit_trail = append_audit_event(
                audit_trail,
                create_task_created_event(
                    task_id=run_id,
                    actor_id=identity.user_id,
                    user_query=task,
                ),
            )

        proposal = active_proposer.propose(task=task, identity=identity)
        audit_trail = append_audit_event(
            audit_trail,
            create_proposal_event(
                run_id=run_id,
                actor_id=identity.user_id,
                proposal=proposal,
            ),
        )

        return {
            **state,
            "status": TaskStatus.RUNNING,
            "proposal": proposal,
            "audit_trail": audit_trail,
        }

    def validate_proposal(state: SkillGraphState) -> SkillGraphState:
        proposal = state.get("proposal")
        identity = state["identity"]
        run_id = state["run_id"]

        if proposal is None:
            return {
                **state,
                "status": TaskStatus.FAILED,
                "error_message": "No skill proposal was produced.",
            }

        validation_result = validator.validate(proposal=proposal, identity=identity)
        accepted = validation_result.status == ProposalValidationStatus.ACCEPTED
        status = TaskStatus.RUNNING if accepted else TaskStatus.FAILED
        error_message = None if accepted else "Proposal validation rejected."

        audit_trail = append_audit_event(
            _audit_trail(state),
            create_validation_event(
                run_id=run_id,
                actor_id=identity.user_id,
                validation_result=validation_result,
            ),
        )

        return {
            **state,
            "status": status,
            "validation_result": validation_result,
            "audit_trail": audit_trail,
            "error_message": error_message,
        }

    def evaluate_policy(state: SkillGraphState) -> SkillGraphState:
        validation_result = state.get("validation_result")
        identity = state["identity"]
        run_id = state["run_id"]

        if not validation_accepted(validation_result):
            return {
                **state,
                "status": TaskStatus.FAILED,
                "error_message": "Cannot evaluate policy before validation succeeds.",
            }

        audit_trail = _audit_trail(state)
        policy_decisions: list[PolicyDecision] = []
        step_arguments: dict[str, dict[str, Any]] = {}
        current_validated_steps = validated_steps(validation_result)
        validated_arguments_by_step_id = validated_step_arguments_by_id(
            validation_result
        )

        if validated_arguments_by_step_id is None:
            return {
                **state,
                "status": TaskStatus.FAILED,
                "error_message": (
                    "Cannot evaluate policy without accepted validated arguments."
                ),
            }

        missing_step_ids = [
            step.step_id
            for step in current_validated_steps
            if step.step_id not in validated_arguments_by_step_id
        ]

        if missing_step_ids:
            return {
                **state,
                "status": TaskStatus.FAILED,
                "error_message": (
                    "Validated arguments are missing for step(s): "
                    f"{', '.join(missing_step_ids)}"
                ),
            }

        for step in current_validated_steps:
            tool = active_tool_registry.get_tool(step.tool_name)
            validated_arguments = dict(validated_arguments_by_step_id[step.step_id])
            decision = evaluate_tool_permission(identity=identity, tool=tool)
            policy_metadata: dict[str, Any] | None = None

            if step.tool_name == GITHUB_COMMENT_TOOL_NAME:
                decision, policy_metadata = apply_github_comment_repository_policy(
                    decision=decision,
                    tool_name=tool.name,
                    required_scopes=tool.required_scopes,
                    arguments=validated_arguments,
                    allowed_repositories=active_allowed_github_comment_repositories,
                )

            policy_decisions.append(decision)
            step_arguments[step.step_id] = validated_arguments
            audit_trail = append_audit_event(
                audit_trail,
                create_permission_checked_event(
                    task_id=run_id,
                    actor_id=identity.user_id,
                    tool_name=tool.name,
                    decision=decision.decision.value,
                    reason=decision.reason,
                    required_scopes=decision.required_scopes,
                    missing_scopes=decision.missing_scopes,
                    metadata=policy_metadata,
                ),
            )

        status = status_from_policy_decisions(policy_decisions)

        return {
            **state,
            "status": status,
            "policy_decisions": policy_decisions,
            "step_arguments": step_arguments,
            "audit_trail": audit_trail,
        }

    def pause_for_approval(state: SkillGraphState) -> SkillGraphState:
        run_id = state["run_id"]
        identity = state["identity"]
        policy_decision = first_approval_policy_decision(
            state.get("policy_decisions", [])
        )

        if policy_decision is None:
            return {
                **state,
                "status": TaskStatus.FAILED,
                "error_message": "Cannot request approval without a policy decision.",
            }

        approval_request = ApprovalRequest(
            task_id=run_id,
            tool_name=policy_decision.tool_name,
            tool_arguments=tool_arguments_for_decision(
                state=state,
                policy_decision=policy_decision,
            ),
            risk_level=active_tool_registry.get_tool(
                policy_decision.tool_name
            ).risk_level,
            requested_by=identity.user_id,
            reason=policy_decision.reason,
        )

        audit_trail = append_audit_event(
            _audit_trail(state),
                create_approval_requested_event(
                    task_id=run_id,
                    actor_id=identity.user_id,
                    tool_name=policy_decision.tool_name,
                    reason=policy_decision.reason,
                    metadata=github_comment_approval_metadata(
                        tool_name=policy_decision.tool_name,
                        concept="github_comment_approval_required",
                    ),
                ),
            )

        return {
            **state,
            "status": TaskStatus.PAUSED_FOR_APPROVAL,
            "approval_request": approval_request,
            "tool_results": [],
            "audit_trail": audit_trail,
            "final_report": "Skill run paused for approval before execution.",
        }

    def handle_approval_decision(state: SkillGraphState) -> SkillGraphState:
        run_id = state["run_id"]
        approval_request = state.get("approval_request")

        if approval_request is None:
            return {
                **state,
                "status": TaskStatus.FAILED,
                "resume_error": "Cannot resume without an approval request.",
                "error_message": "Cannot resume without an approval request.",
            }

        resume_value = interrupt(
            {
                "kind": "skill_approval_required",
                "run_id": run_id,
                "tool_name": approval_request.tool_name,
                "approval_request": approval_request.model_dump(mode="json"),
                "message": "Approval decision required before skill execution.",
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
            fallback_reason = "Approved."
        elif approval_decision.status == ApprovalStatus.REJECTED:
            required_scope = "approval:reject"
            event_factory = create_approval_rejected_event
            next_status = TaskStatus.REJECTED
            fallback_reason = "Rejected."
        else:
            return {
                **state,
                "status": TaskStatus.FAILED,
                "approval_decision": approval_decision,
                "approval_actor": approval_actor,
                "resume_error": (
                    "Unsupported approval decision: "
                    f"{approval_decision.status.value}"
                ),
                "error_message": (
                    "Unsupported approval decision: "
                    f"{approval_decision.status.value}"
                ),
            }

        if required_scope not in approval_actor.scopes:
            return {
                **state,
                "status": TaskStatus.FAILED,
                "approval_decision": approval_decision,
                "approval_actor": approval_actor,
                "resume_error": f"Approval actor lacks required scope: {required_scope}",
                "error_message": f"Approval actor lacks required scope: {required_scope}",
                "tool_results": [],
            }

        audit_trail = append_audit_event(
            _audit_trail(state),
            event_factory(
                task_id=run_id,
                actor_id=approval_actor.user_id,
                tool_name=approval_request.tool_name,
                reason=approval_decision.reason or fallback_reason,
                metadata=github_comment_approval_metadata(
                    tool_name=approval_request.tool_name,
                    concept=(
                        "github_comment_approval_granted"
                        if approval_decision.status == ApprovalStatus.APPROVED
                        else "github_comment_approval_rejected"
                    ),
                ),
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

    def execute_validated_steps(state: SkillGraphState) -> SkillGraphState:
        validation_result = state.get("validation_result")

        if not execution_allowed(state):
            return {
                **state,
                "status": TaskStatus.FAILED,
                "error_message": "Skill execution was not authorized.",
                "tool_results": [],
            }

        audit_trail = _audit_trail(state)
        tool_results: list[ToolExecutionResult] = []
        current_validated_steps = validated_steps(validation_result)
        validated_arguments_by_step_id = validated_step_arguments_by_id(
            validation_result
        )

        if validated_arguments_by_step_id is None:
            return {
                **state,
                "status": TaskStatus.FAILED,
                "error_message": "Skill execution was missing validated arguments.",
                "tool_results": [],
            }

        missing_step_ids = [
            step.step_id
            for step in current_validated_steps
            if step.step_id not in validated_arguments_by_step_id
        ]

        if missing_step_ids:
            return {
                **state,
                "status": TaskStatus.FAILED,
                "error_message": (
                    "Validated arguments are missing for step(s): "
                    f"{', '.join(missing_step_ids)}"
                ),
                "tool_results": [],
            }

        for step in current_validated_steps:
            execution_context = github_comment_execution_context(
                run_id=state["run_id"],
                step_id=step.step_id,
                tool_name=step.tool_name,
                side_effect_ledger=active_side_effect_ledger,
                github_issue_comment_client=active_github_issue_comment_client,
                durable_side_effect_ledger=durable_side_effect_ledger,
                durable_approval_binding_store=durable_approval_binding_store,
                durable_audit_store=durable_audit_store,
                real_github_issue_comment_client=real_github_issue_comment_client,
                github_real_mode_config=github_real_mode_config,
                github_token_provider=github_token_provider,
            )

            result = active_tool_registry.execute(
                step.tool_name,
                dict(validated_arguments_by_step_id[step.step_id]),
                context=execution_context,
            )
            tool_results.append(result)
            audit_trail = append_audit_event(
                audit_trail,
                create_tool_executed_event(
                    task_id=state["run_id"],
                    actor_id=state["identity"].user_id,
                    tool_name=step.tool_name,
                    dry_run=result.dry_run,
                    success=result.success,
                    metadata=github_comment_execution_metadata(
                        tool_name=step.tool_name,
                        result=result,
                    ),
                ),
            )

        execution_succeeded = all(result.success for result in tool_results)

        return {
            **state,
            "status": TaskStatus.RUNNING if execution_succeeded else TaskStatus.FAILED,
            "tool_results": tool_results,
            "audit_trail": audit_trail,
            "error_message": (
                None if execution_succeeded else "One or more skill steps failed."
            ),
        }

    def finalize_success(state: SkillGraphState) -> SkillGraphState:
        validation_result = state["validation_result"]
        skill = validation_result.skill
        run_id = state["run_id"]
        identity = state["identity"]

        final_result = SkillRunResult(
            run_id=run_id,
            status=SkillRunStatus.COMPLETED,
            skill_id=skill.skill_id,
            skill_version=skill.version,
            step_results=state.get("tool_results", []),
            message="Skill completed successfully using dry-run execution.",
        )
        audit_trail = append_audit_event(
            _audit_trail(state),
            create_audit_event(
                task_id=run_id,
                event_type=AuditEventType.TASK_COMPLETED,
                actor_id=identity.user_id,
                message="Skill run completed.",
                metadata={
                    "skill_id": skill.skill_id,
                    "skill_version": skill.version,
                },
            ),
        )

        return {
            **state,
            "status": TaskStatus.COMPLETED,
            "final_result": final_result,
            "final_report": "Skill run completed successfully.",
            "audit_trail": audit_trail,
        }

    def finalize_validation_failure(state: SkillGraphState) -> SkillGraphState:
        return _finalize_failed_run(
            state=state,
            status=TaskStatus.FAILED,
            message=state.get("error_message") or "Proposal validation failed.",
        )

    def finalize_denial(state: SkillGraphState) -> SkillGraphState:
        return _finalize_failed_run(
            state=state,
            status=TaskStatus.DENIED,
            message="Skill run denied by policy.",
        )

    def finalize_rejection(state: SkillGraphState) -> SkillGraphState:
        approval_decision = state.get("approval_decision")
        reason = approval_decision.reason if approval_decision else "Approval rejected."

        return _finalize_failed_run(
            state=state,
            status=TaskStatus.REJECTED,
            message=f"Skill run rejected: {reason}",
        )

    def finalize_failure(state: SkillGraphState) -> SkillGraphState:
        return _finalize_failed_run(
            state=state,
            status=TaskStatus.FAILED,
            message=state.get("error_message") or "Skill run failed.",
        )

    builder = StateGraph(SkillGraphState)

    builder.add_node("propose_skill", propose_skill)
    builder.add_node("validate_proposal", validate_proposal)
    builder.add_node("evaluate_policy", evaluate_policy)
    builder.add_node("pause_for_approval", pause_for_approval)
    builder.add_node("handle_approval_decision", handle_approval_decision)
    builder.add_node("execute_validated_steps", execute_validated_steps)
    builder.add_node("finalize_success", finalize_success)
    builder.add_node("finalize_validation_failure", finalize_validation_failure)
    builder.add_node("finalize_denial", finalize_denial)
    builder.add_node("finalize_rejection", finalize_rejection)
    builder.add_node("finalize_failure", finalize_failure)

    builder.add_edge(START, "propose_skill")
    builder.add_edge("propose_skill", "validate_proposal")
    builder.add_conditional_edges(
        "validate_proposal",
        route_after_validation,
        {
            "evaluate_policy": "evaluate_policy",
            "finalize_validation_failure": "finalize_validation_failure",
        },
    )
    builder.add_conditional_edges(
        "evaluate_policy",
        route_after_policy,
        {
            "execute_validated_steps": "execute_validated_steps",
            "pause_for_approval": "pause_for_approval",
            "finalize_denial": "finalize_denial",
            "finalize_failure": "finalize_failure",
        },
    )
    builder.add_edge("pause_for_approval", "handle_approval_decision")
    builder.add_conditional_edges(
        "handle_approval_decision",
        route_after_approval_decision,
        {
            "execute_validated_steps": "execute_validated_steps",
            "finalize_rejection": "finalize_rejection",
            "finalize_failure": "finalize_failure",
        },
    )
    builder.add_conditional_edges(
        "execute_validated_steps",
        route_after_execution,
        {
            "finalize_success": "finalize_success",
            "finalize_failure": "finalize_failure",
        },
    )
    builder.add_edge("finalize_success", END)
    builder.add_edge("finalize_validation_failure", END)
    builder.add_edge("finalize_denial", END)
    builder.add_edge("finalize_rejection", END)
    builder.add_edge("finalize_failure", END)

    return builder.compile(checkpointer=InMemorySaver())


def _audit_trail(state: SkillGraphState) -> list[AuditEvent]:
    return list(state.get("audit_trail", []))


def _coerce_approval_decision(value: Any) -> ApprovalDecision | None:
    if isinstance(value, ApprovalDecision):
        return value

    if isinstance(value, dict):
        return ApprovalDecision.model_validate(value.get("approval_decision", value))

    return None


def _coerce_approval_actor(value: Any) -> IdentityContext | None:
    if isinstance(value, dict):
        actor_value = value.get("approval_actor")
        if isinstance(actor_value, IdentityContext):
            return actor_value
        if isinstance(actor_value, dict):
            return IdentityContext.model_validate(actor_value)

    return None


def _finalize_failed_run(
    state: SkillGraphState,
    status: TaskStatus,
    message: str,
) -> SkillGraphState:
    proposal = state.get("proposal")
    validation_result = state.get("validation_result")
    skill = validation_result.skill if validation_result is not None else None
    skill_id = (
        skill.skill_id
        if skill is not None
        else proposal.proposed_skill_id
        if proposal is not None
        else "unknown"
    )
    skill_version = (
        skill.version
        if skill is not None
        else proposal.proposed_skill_version
        if proposal is not None
        else "unknown"
    )
    final_result = SkillRunResult(
        run_id=state["run_id"],
        status=SkillRunStatus.FAILED,
        skill_id=skill_id,
        skill_version=skill_version,
        step_results=list(state.get("tool_results", [])),
        message=message,
    )
    audit_trail = append_audit_event(
        _audit_trail(state),
        create_audit_event(
            task_id=state["run_id"],
            event_type=AuditEventType.TASK_FAILED,
            actor_id=state["identity"].user_id,
            message=message,
            metadata={"status": status.value},
        ),
    )

    return {
        **state,
        "status": status,
        "tool_results": list(state.get("tool_results", [])),
        "final_result": final_result,
        "final_report": message,
        "audit_trail": audit_trail,
    }
