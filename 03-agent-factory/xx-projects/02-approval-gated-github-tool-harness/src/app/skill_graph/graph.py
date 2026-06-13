from typing import Any, Literal

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
from app.audit.schemas import AuditEvent, AuditEventType
from app.github.client import GitHubIssueCommentClient
from app.github.fake_client import FakeGitHubIssueCommentClient
from app.identity.schemas import IdentityContext
from app.policy.guard import evaluate_tool_permission
from app.policy.schemas import PolicyDecision, PolicyDecisionType
from app.proposer.base import SkillProposer
from app.side_effects.ledger import InMemorySideEffectLedger, SideEffectLedger
from app.proposer.fake import FakeProposer
from app.skills.argument_schemas import ArgumentValidationStatus, ValidatedSkillPlan
from app.skills.registry import SkillRegistry, build_default_skill_registry
from app.skills.schemas import (
    ProposalValidationResult,
    ProposalValidationStatus,
    SkillRunResult,
    SkillRunStatus,
    SkillStep,
)
from app.skills.validator import ProposalValidator
from app.skill_graph.state import SkillGraphState
from app.state.schemas import TaskStatus
from app.tools.context import ToolExecutionContext
from app.tools.github_comment import (
    DEFAULT_ALLOWED_GITHUB_COMMENT_REPOSITORIES,
    GITHUB_COMMENT_TOOL_NAME,
    repository_is_allowed,
)
from app.tools.registry import ToolRegistry, build_default_tool_registry
from app.tools.schemas import ToolExecutionResult


GraphRoute = Literal[
    "evaluate_policy",
    "execute_validated_steps",
    "finalize_denial",
    "finalize_failure",
    "finalize_rejection",
    "finalize_success",
    "finalize_validation_failure",
    "pause_for_approval",
]


def build_skill_execution_graph(
    proposer: SkillProposer | None = None,
    skill_registry: SkillRegistry | None = None,
    tool_registry: ToolRegistry | None = None,
    github_issue_comment_client: GitHubIssueCommentClient | None = None,
    side_effect_ledger: SideEffectLedger | None = None,
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
            _create_proposal_event(
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
            _create_validation_event(
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

        if not _validation_accepted(validation_result):
            return {
                **state,
                "status": TaskStatus.FAILED,
                "error_message": "Cannot evaluate policy before validation succeeds.",
            }

        audit_trail = _audit_trail(state)
        policy_decisions: list[PolicyDecision] = []
        step_arguments: dict[str, dict[str, Any]] = {}
        validated_steps = _validated_steps(validation_result)
        validated_arguments_by_step_id = _validated_step_arguments_by_id(
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
            for step in validated_steps
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

        for step in validated_steps:
            tool = active_tool_registry.get_tool(step.tool_name)
            validated_arguments = dict(validated_arguments_by_step_id[step.step_id])
            decision = evaluate_tool_permission(identity=identity, tool=tool)
            policy_metadata: dict[str, Any] | None = None

            if step.tool_name == GITHUB_COMMENT_TOOL_NAME:
                decision, policy_metadata = _apply_github_comment_repository_policy(
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

        status = _status_from_policy_decisions(policy_decisions)

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
        policy_decision = _first_approval_policy_decision(
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
            tool_arguments=_tool_arguments_for_decision(
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
                    metadata=_github_comment_approval_metadata(
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
                metadata=_github_comment_approval_metadata(
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

        if not _execution_allowed(state):
            return {
                **state,
                "status": TaskStatus.FAILED,
                "error_message": "Skill execution was not authorized.",
                "tool_results": [],
            }

        audit_trail = _audit_trail(state)
        tool_results: list[ToolExecutionResult] = []
        validated_steps = _validated_steps(validation_result)
        validated_arguments_by_step_id = _validated_step_arguments_by_id(
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
            for step in validated_steps
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

        for step in validated_steps:
            execution_context = None
            if step.tool_name == GITHUB_COMMENT_TOOL_NAME:
                execution_context = ToolExecutionContext(
                    run_id=state["run_id"],
                    step_id=step.step_id,
                    side_effect_ledger=active_side_effect_ledger,
                    github_issue_comment_client=active_github_issue_comment_client,
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
                    metadata=_github_comment_execution_metadata(
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
        _route_after_validation,
        {
            "evaluate_policy": "evaluate_policy",
            "finalize_validation_failure": "finalize_validation_failure",
        },
    )
    builder.add_conditional_edges(
        "evaluate_policy",
        _route_after_policy,
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
        _route_after_approval_decision,
        {
            "execute_validated_steps": "execute_validated_steps",
            "finalize_rejection": "finalize_rejection",
            "finalize_failure": "finalize_failure",
        },
    )
    builder.add_conditional_edges(
        "execute_validated_steps",
        _route_after_execution,
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


def _create_proposal_event(
    run_id: str,
    actor_id: str,
    proposal,
) -> AuditEvent:
    return create_audit_event(
        task_id=run_id,
        event_type=AuditEventType.TOOL_SELECTED,
        actor_id=actor_id,
        message="Skill proposal was produced.",
        tool_name=proposal.steps[0].tool_name if proposal.steps else None,
        metadata={
            "kind": "skill_proposal",
            "skill_id": proposal.proposed_skill_id,
            "skill_version": proposal.proposed_skill_version,
            "step_ids": [step.step_id for step in proposal.steps],
            "tool_names": [step.tool_name for step in proposal.steps],
            "rationale": proposal.rationale,
        },
    )


def _create_validation_event(
    run_id: str,
    actor_id: str,
    validation_result: ProposalValidationResult,
) -> AuditEvent:
    risk_level = validation_result.risk_level

    return create_audit_event(
        task_id=run_id,
        event_type=AuditEventType.PERMISSION_CHECKED,
        actor_id=actor_id,
        message="Proposal validation completed.",
        metadata={
            "kind": "proposal_validation",
            "status": validation_result.status.value,
            "rejection_reasons": [
                reason.value for reason in validation_result.rejection_reasons
            ],
            "required_scopes": list(validation_result.required_scopes),
            "risk_level": None if risk_level is None else risk_level.value,
            "approval_required": validation_result.approval_required,
            **_argument_validation_metadata(validation_result),
            **_github_comment_validation_metadata(validation_result),
        },
    )


def _route_after_validation(state: SkillGraphState) -> GraphRoute:
    validation_result = state.get("validation_result")

    if _validation_accepted(validation_result):
        return "evaluate_policy"

    return "finalize_validation_failure"


def _route_after_policy(state: SkillGraphState) -> GraphRoute:
    status = state.get("status")

    if status == TaskStatus.RUNNING:
        return "execute_validated_steps"

    if status == TaskStatus.PAUSED_FOR_APPROVAL:
        return "pause_for_approval"

    if status == TaskStatus.DENIED:
        return "finalize_denial"

    return "finalize_failure"


def _route_after_execution(state: SkillGraphState) -> GraphRoute:
    if state.get("status") == TaskStatus.RUNNING:
        return "finalize_success"

    return "finalize_failure"


def _route_after_approval_decision(state: SkillGraphState) -> GraphRoute:
    status = state.get("status")

    if status == TaskStatus.RUNNING:
        return "execute_validated_steps"

    if status == TaskStatus.REJECTED:
        return "finalize_rejection"

    return "finalize_failure"


def _status_from_policy_decisions(
    policy_decisions: list[PolicyDecision],
) -> TaskStatus:
    if not policy_decisions:
        return TaskStatus.FAILED

    if any(
        decision.decision == PolicyDecisionType.DENY
        for decision in policy_decisions
    ):
        return TaskStatus.DENIED

    if any(
        decision.decision == PolicyDecisionType.REQUIRE_APPROVAL
        for decision in policy_decisions
    ):
        return TaskStatus.PAUSED_FOR_APPROVAL

    return TaskStatus.RUNNING


def _apply_github_comment_repository_policy(
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


def _github_comment_approval_metadata(
    *,
    tool_name: str,
    concept: str,
) -> dict[str, Any] | None:
    if tool_name != GITHUB_COMMENT_TOOL_NAME:
        return None

    return {
        "kind": "github_comment_approval",
        "github_comment_audit_concept": concept,
        "approval_binding": "validated_tool_arguments_in_current_graph_state",
        "approval_binding_limitation": (
            "ApprovalDecision does not persist validated_arguments_hash or "
            "side_effect_id in A3.3."
        ),
        "client_called": False,
    }


def _github_comment_execution_metadata(
    *,
    tool_name: str,
    result: ToolExecutionResult,
) -> dict[str, Any] | None:
    if tool_name != GITHUB_COMMENT_TOOL_NAME:
        return None

    result_payload = dict(result.result)
    ledger_hit = bool(result_payload.get("ledger_hit"))
    client_called = bool(result_payload.get("client_called"))
    skipped = bool(result_payload.get("skipped"))
    concepts = ["github_comment_side_effect_id_computed"]

    concepts.append(
        "github_comment_ledger_hit"
        if ledger_hit
        else "github_comment_ledger_miss"
    )
    concepts.append(
        "github_comment_client_called"
        if client_called
        else "github_comment_client_not_called"
    )

    if result.success and skipped:
        concepts.append("github_comment_skipped")
    elif result.success:
        concepts.append("github_comment_executed")
    else:
        concepts.append("github_comment_failed")

    return {
        "kind": "github_comment_side_effect",
        "github_comment_audit_concepts": concepts,
        "mode": result_payload.get("mode"),
        "repository": result_payload.get("repository"),
        "issue_number": result_payload.get("issue_number"),
        "validated_arguments_hash": result_payload.get("validated_arguments_hash"),
        "side_effect_id": result_payload.get("side_effect_id"),
        "side_effect_status": result_payload.get("side_effect_status"),
        "ledger_hit": ledger_hit,
        "ledger_miss": bool(result_payload.get("ledger_miss")),
        "client_called": client_called,
        "skipped": skipped,
        "error_type": result_payload.get("error_type"),
        "real_github_network_call": False,
    }


def _validation_accepted(
    validation_result: ProposalValidationResult | None,
) -> bool:
    return _accepted_validated_skill_plan(validation_result) is not None


def _accepted_validated_skill_plan(
    validation_result: ProposalValidationResult | None,
) -> ValidatedSkillPlan | None:
    if (
        validation_result is None
        or validation_result.status != ProposalValidationStatus.ACCEPTED
        or validation_result.skill is None
        or validation_result.proposal is None
    ):
        return None

    validated_skill_plan = validation_result.validated_skill_plan

    if (
        validated_skill_plan is None
        or validated_skill_plan.status != ArgumentValidationStatus.ACCEPTED
        or validated_skill_plan.skill_id != validation_result.skill.skill_id
        or validated_skill_plan.skill_version != validation_result.skill.version
    ):
        return None

    return validated_skill_plan


def _validated_step_arguments_by_id(
    validation_result: ProposalValidationResult | None,
) -> dict[str, dict[str, Any]] | None:
    validated_skill_plan = _accepted_validated_skill_plan(validation_result)

    if validated_skill_plan is None:
        return None

    arguments_by_step_id: dict[str, dict[str, Any]] = {}

    for step_arguments in validated_skill_plan.step_arguments:
        if step_arguments.step_id in arguments_by_step_id:
            return None

        arguments_by_step_id[step_arguments.step_id] = dict(step_arguments.arguments)

    return arguments_by_step_id


def _argument_validation_metadata(
    validation_result: ProposalValidationResult,
) -> dict[str, Any]:
    validated_skill_plan = validation_result.validated_skill_plan

    if validated_skill_plan is None:
        return {
            "argument_validation_status": None,
            "validated_argument_names": {},
            "redacted_argument_names": {},
            "argument_validation_issue_codes": [],
        }

    return {
        "argument_validation_status": validated_skill_plan.status.value,
        "validated_argument_names": {
            step_arguments.step_id: list(step_arguments.arguments)
            for step_arguments in validated_skill_plan.step_arguments
        },
        "redacted_argument_names": {
            step_arguments.step_id: list(step_arguments.redacted_argument_names)
            for step_arguments in validated_skill_plan.step_arguments
        },
        "argument_validation_issue_codes": [
            issue.reason_code for issue in validated_skill_plan.issues
        ],
    }


def _github_comment_validation_metadata(
    validation_result: ProposalValidationResult,
) -> dict[str, Any]:
    proposal = validation_result.proposal
    skill = validation_result.skill
    skill_id = skill.skill_id if skill is not None else None

    if skill_id is None and proposal is not None:
        skill_id = proposal.proposed_skill_id

    if skill_id != GITHUB_COMMENT_TOOL_NAME:
        return {}

    validation_passed = validation_result.status == ProposalValidationStatus.ACCEPTED

    return {
        "github_comment_audit_concept": (
            "github_comment_validation_passed"
            if validation_passed
            else "github_comment_validation_failed"
        ),
    }


def _validated_steps(
    validation_result: ProposalValidationResult | None,
) -> list[SkillStep]:
    if not _validation_accepted(validation_result):
        return []

    step_by_id = {step.step_id: step for step in validation_result.skill.steps}

    return [
        step_by_id[proposed_step.step_id]
        for proposed_step in validation_result.proposal.steps
        if proposed_step.step_id in step_by_id
    ]


def _first_approval_policy_decision(
    policy_decisions: list[PolicyDecision],
) -> PolicyDecision | None:
    for policy_decision in policy_decisions:
        if policy_decision.decision == PolicyDecisionType.REQUIRE_APPROVAL:
            return policy_decision

    return None


def _tool_arguments_for_decision(
    state: SkillGraphState,
    policy_decision: PolicyDecision,
) -> dict[str, Any]:
    validation_result = state.get("validation_result")
    validated_arguments_by_step_id = _validated_step_arguments_by_id(validation_result)

    if validated_arguments_by_step_id is None:
        return {}

    for step in _validated_steps(validation_result):
        if step.tool_name == policy_decision.tool_name:
            return dict(validated_arguments_by_step_id.get(step.step_id, {}))

    return {}


def _execution_allowed(state: SkillGraphState) -> bool:
    validation_result = state.get("validation_result")

    if not _validation_accepted(validation_result):
        return False

    policy_decisions = state.get("policy_decisions", [])

    if not policy_decisions:
        return False

    if any(
        decision.decision == PolicyDecisionType.DENY
        for decision in policy_decisions
    ):
        return False

    approval_required = any(
        decision.decision == PolicyDecisionType.REQUIRE_APPROVAL
        for decision in policy_decisions
    )

    if not approval_required:
        return all(
            decision.decision == PolicyDecisionType.ALLOW
            for decision in policy_decisions
        )

    approval_decision = state.get("approval_decision")

    return (
        approval_decision is not None
        and approval_decision.status == ApprovalStatus.APPROVED
    )

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
