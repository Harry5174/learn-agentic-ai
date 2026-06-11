from app.identity.schemas import IdentityContext, Role
from app.skills.registry import build_default_skill_registry
from app.skills.schemas import (
    ProposalValidationReason,
    ProposalValidationStatus,
    SkillProposal,
)
from app.skills.validator import ProposalValidator
from app.tools.schemas import RiskLevel


def _identity(scopes: list[str]) -> IdentityContext:
    return IdentityContext(
        user_id="user-123",
        api_key_id="key-123",
        role=Role.OPERATOR,
        scopes=scopes,
    )


def _proposal(skill_id: str, version: str = "1.0") -> SkillProposal:
    skill = build_default_skill_registry().get_skill(skill_id, version=version)

    return SkillProposal(
        proposed_skill_id=skill.skill_id,
        proposed_skill_version=skill.version,
        rationale="The user requested a known sandbox skill.",
        steps=[step.model_copy(deep=True) for step in skill.steps],
    )


def test_valid_low_risk_proposal_is_accepted() -> None:
    registry = build_default_skill_registry()
    validator = ProposalValidator(registry)
    proposal = _proposal("inspect_sandbox_health")

    result = validator.validate(proposal, _identity(["tools:inspect"]))

    assert result.status == ProposalValidationStatus.ACCEPTED
    assert result.proposal == proposal
    assert result.skill == registry.get_skill("inspect_sandbox_health", "1.0")
    assert result.rejection_reasons == []
    assert result.required_scopes == ["tools:inspect"]
    assert result.risk_level == RiskLevel.LOW
    assert result.approval_required is False


def test_valid_high_risk_proposal_requires_approval() -> None:
    validator = ProposalValidator(build_default_skill_registry())
    proposal = _proposal("simulate_sandbox_workflow")

    result = validator.validate(proposal, _identity(["tools:trigger_workflow"]))

    assert result.status == ProposalValidationStatus.ACCEPTED
    assert result.required_scopes == ["tools:trigger_workflow"]
    assert result.risk_level == RiskLevel.HIGH
    assert result.approval_required is True


def test_unknown_skill_is_rejected() -> None:
    validator = ProposalValidator(build_default_skill_registry())
    proposal = SkillProposal(
        proposed_skill_id="not_registered",
        proposed_skill_version="1.0",
        rationale="Try an unknown skill.",
        steps=[],
    )

    result = validator.validate(proposal, _identity(["tools:inspect"]))

    assert result.status == ProposalValidationStatus.REJECTED
    assert result.skill is None
    assert result.rejection_reasons == [ProposalValidationReason.UNKNOWN_SKILL]
    assert result.risk_level is None
    assert result.approval_required is False


def test_unsupported_version_is_rejected() -> None:
    validator = ProposalValidator(build_default_skill_registry())
    proposal = _proposal("inspect_sandbox_health").model_copy(
        update={"proposed_skill_version": "2.0"}
    )

    result = validator.validate(proposal, _identity(["tools:inspect"]))

    assert result.status == ProposalValidationStatus.REJECTED
    assert result.skill is None
    assert result.rejection_reasons == [
        ProposalValidationReason.UNSUPPORTED_SKILL_VERSION
    ]
    assert result.risk_level is None


def test_empty_steps_are_rejected() -> None:
    validator = ProposalValidator(build_default_skill_registry())
    proposal = _proposal("inspect_sandbox_health").model_copy(update={"steps": []})

    result = validator.validate(proposal, _identity(["tools:inspect"]))

    assert result.status == ProposalValidationStatus.REJECTED
    assert result.rejection_reasons == [ProposalValidationReason.EMPTY_STEPS]
    assert result.required_scopes == ["tools:inspect"]
    assert result.risk_level == RiskLevel.LOW


def test_duplicate_step_ids_are_rejected() -> None:
    validator = ProposalValidator(build_default_skill_registry())
    proposal = _proposal("inspect_sandbox_health")
    duplicate_step = proposal.steps[0].model_copy(deep=True)
    proposal = proposal.model_copy(update={"steps": [proposal.steps[0], duplicate_step]})

    result = validator.validate(proposal, _identity(["tools:inspect"]))

    assert result.status == ProposalValidationStatus.REJECTED
    assert result.rejection_reasons == [ProposalValidationReason.DUPLICATE_STEP_ID]


def test_unknown_step_is_rejected() -> None:
    validator = ProposalValidator(build_default_skill_registry())
    proposal = _proposal("inspect_sandbox_health")
    unknown_step = proposal.steps[0].model_copy(update={"step_id": "unknown_step"})
    proposal = proposal.model_copy(update={"steps": [unknown_step]})

    result = validator.validate(proposal, _identity(["tools:inspect"]))

    assert result.status == ProposalValidationStatus.REJECTED
    assert result.rejection_reasons == [ProposalValidationReason.UNKNOWN_STEP]


def test_tool_mismatch_is_rejected() -> None:
    validator = ProposalValidator(build_default_skill_registry())
    proposal = _proposal("inspect_sandbox_health")
    mismatched_step = proposal.steps[0].model_copy(
        update={"tool_name": "draft_issue_comment"}
    )
    proposal = proposal.model_copy(update={"steps": [mismatched_step]})

    result = validator.validate(proposal, _identity(["tools:inspect"]))

    assert result.status == ProposalValidationStatus.REJECTED
    assert result.rejection_reasons == [ProposalValidationReason.TOOL_NOT_ALLOWED]


def test_missing_required_scope_is_rejected() -> None:
    validator = ProposalValidator(build_default_skill_registry())
    proposal = _proposal("draft_sandbox_issue_comment")

    result = validator.validate(proposal, _identity(["tools:inspect"]))

    assert result.status == ProposalValidationStatus.REJECTED
    assert result.rejection_reasons == [
        ProposalValidationReason.MISSING_REQUIRED_SCOPE
    ]
    assert result.required_scopes == ["tools:draft"]
    assert result.risk_level == RiskLevel.MEDIUM


def test_risk_understatement_is_rejected() -> None:
    validator = ProposalValidator(build_default_skill_registry())
    proposal = _proposal("simulate_sandbox_workflow")
    understated_step = proposal.steps[0].model_copy(
        update={"risk_level": RiskLevel.LOW}
    )
    proposal = proposal.model_copy(update={"steps": [understated_step]})

    result = validator.validate(proposal, _identity(["tools:trigger_workflow"]))

    assert result.status == ProposalValidationStatus.REJECTED
    assert result.rejection_reasons == [ProposalValidationReason.RISK_MISMATCH]
    assert result.risk_level == RiskLevel.HIGH
    assert result.approval_required is True


def test_validator_uses_registry_defined_metadata() -> None:
    validator = ProposalValidator(build_default_skill_registry())
    proposal = _proposal("inspect_sandbox_health")
    proposal_step_without_scope = proposal.steps[0].model_copy(
        update={"required_scopes": [], "risk_level": RiskLevel.MEDIUM}
    )
    proposal = proposal.model_copy(update={"steps": [proposal_step_without_scope]})

    result = validator.validate(proposal, _identity(["tools:inspect"]))

    assert result.status == ProposalValidationStatus.ACCEPTED
    assert result.required_scopes == ["tools:inspect"]
    assert result.risk_level == RiskLevel.LOW
    assert result.approval_required is False
