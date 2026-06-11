from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import enforce_skill_run_create_rate_limit
from app.api.skill_schemas import (
    ProposerMode,
    SkillExecutionSummaryResponse,
    SkillProposalSummaryResponse,
    SkillRunApprovalStatusResponse,
    SkillRunCreateRequest,
    SkillRunStatusResponse,
    SkillRunSummaryResponse,
    SkillStepSummaryResponse,
    SkillSummaryResponse,
    SkillValidationStatusResponse,
    SkillValidationSummaryResponse,
)
from app.approval.schemas import ApprovalStatus
from app.identity.schemas import IdentityContext
from app.skill_graph.service import SkillGraphService
from app.skill_graph.state import SkillGraphState
from app.skills.registry import build_default_skill_registry
from app.skills.schemas import ProposalValidationResult, SkillProposal, SkillSpec
from app.state.schemas import TaskStatus

router = APIRouter(tags=["skills"])

# In-memory/local service state for the demo API.
# State does not survive process restart.
_skill_run_service = SkillGraphService()


@router.get("/skills", response_model=list[SkillSummaryResponse])
def list_skills() -> list[SkillSummaryResponse]:
    """List public metadata for registered skills."""

    registry = build_default_skill_registry()
    return [_skill_summary_from_spec(skill) for skill in registry.list_skills()]


@router.post(
    "/skill-runs",
    response_model=SkillRunSummaryResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
def create_skill_run(
    request: SkillRunCreateRequest,
    identity: Annotated[IdentityContext, Depends(enforce_skill_run_create_rate_limit)],
) -> SkillRunSummaryResponse:
    """Start a new skill run for the current server-derived identity."""

    proposer_mode = request.proposer_mode or ProposerMode.FAKE

    if proposer_mode == ProposerMode.LLM:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="LLM proposer mode is not enabled for this API.",
        )

    state = _skill_run_service.start_run(
        task=request.task,
        identity=identity,
    )

    return skill_run_summary_from_state(
        state=state,
        proposer_mode=proposer_mode,
    )


def _skill_summary_from_spec(skill: SkillSpec) -> SkillSummaryResponse:
    return SkillSummaryResponse(
        skill_id=skill.skill_id,
        version=skill.version,
        name=skill.name,
        description=skill.description,
        required_scopes=list(skill.required_scopes),
        risk_level=skill.risk_level,
        steps=[
            SkillStepSummaryResponse(
                step_id=step.step_id,
                description=step.description,
                tool_name=step.tool_name,
                risk_level=step.risk_level,
                required_scopes=list(step.required_scopes),
            )
            for step in skill.steps
        ],
    )


def skill_run_summary_from_state(
    *,
    state: SkillGraphState,
    proposer_mode: ProposerMode,
) -> SkillRunSummaryResponse:
    """Convert internal skill graph state into a safe public response."""

    validation_result = state.get("validation_result")

    return SkillRunSummaryResponse(
        run_id=state["run_id"],
        status=_status_response(state["status"]),
        task=state["task"],
        proposer_mode=proposer_mode,
        selected_skill_id=_selected_skill_id(validation_result),
        selected_skill_version=_selected_skill_version(validation_result),
        validation_status=_validation_status(validation_result),
        approval_required=_approval_required(state),
        approval_status=_approval_status(state),
        risk_level=None if validation_result is None else validation_result.risk_level,
        final_report=state.get("final_report"),
        error_message=state.get("error_message"),
        proposal=_proposal_summary(state.get("proposal")),
        validation=_validation_summary(validation_result),
        execution=_execution_summary(state),
    )


def _status_response(status_value: TaskStatus) -> SkillRunStatusResponse:
    return SkillRunStatusResponse(status_value.value)


def _validation_status(
    validation_result: ProposalValidationResult | None,
) -> SkillValidationStatusResponse:
    if validation_result is None:
        return SkillValidationStatusResponse.NOT_VALIDATED

    return SkillValidationStatusResponse(validation_result.status.value)


def _selected_skill_id(validation_result: ProposalValidationResult | None) -> str | None:
    if validation_result is None or validation_result.skill is None:
        return None

    return validation_result.skill.skill_id


def _selected_skill_version(
    validation_result: ProposalValidationResult | None,
) -> str | None:
    if validation_result is None or validation_result.skill is None:
        return None

    return validation_result.skill.version


def _approval_required(state: SkillGraphState) -> bool:
    validation_result = state.get("validation_result")

    if validation_result is not None:
        return validation_result.approval_required

    return state.get("approval_request") is not None


def _approval_status(state: SkillGraphState) -> SkillRunApprovalStatusResponse:
    approval_decision = state.get("approval_decision")

    if approval_decision is not None:
        if approval_decision.status == ApprovalStatus.APPROVED:
            return SkillRunApprovalStatusResponse.APPROVED

        if approval_decision.status == ApprovalStatus.REJECTED:
            return SkillRunApprovalStatusResponse.REJECTED

    if _approval_required(state) or state.get("approval_request") is not None:
        return SkillRunApprovalStatusResponse.PENDING

    return SkillRunApprovalStatusResponse.NOT_REQUIRED


def _proposal_summary(
    proposal: SkillProposal | None,
) -> SkillProposalSummaryResponse | None:
    if proposal is None:
        return None

    return SkillProposalSummaryResponse(
        proposed_skill_id=proposal.proposed_skill_id,
        proposed_skill_version=proposal.proposed_skill_version,
        rationale=proposal.rationale,
        proposed_tool_names=[step.tool_name for step in proposal.steps],
    )


def _validation_summary(
    validation_result: ProposalValidationResult | None,
) -> SkillValidationSummaryResponse | None:
    if validation_result is None:
        return None

    return SkillValidationSummaryResponse(
        status=_validation_status(validation_result),
        rejection_reasons=[
            reason.value for reason in validation_result.rejection_reasons
        ],
        required_scopes=list(validation_result.required_scopes),
        risk_level=validation_result.risk_level,
    )


def _execution_summary(state: SkillGraphState) -> SkillExecutionSummaryResponse:
    tool_results = list(state.get("tool_results", []))

    return SkillExecutionSummaryResponse(
        attempted_step_count=len(tool_results),
        completed_step_count=sum(1 for result in tool_results if result.success),
        tool_names=[result.tool_name for result in tool_results],
        dry_run=all(result.dry_run for result in tool_results),
    )
