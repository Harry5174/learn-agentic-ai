import json
from typing import Any

from app.identity.schemas import IdentityContext, Role
from app.proposer.config import MALFORMED_LLM_OUTPUT_SKILL_ID
from app.proposer.llm import LLMProposer
from app.proposer.prompts import LLMProposalPrompt
from app.skills.registry import build_default_skill_registry
from app.skills.schemas import (
    ProposalValidationReason,
    ProposalValidationStatus,
)
from app.skills.validator import ProposalValidator
from app.tools.schemas import RiskLevel


class CapturingClient:
    def __init__(self, output: str | dict[str, Any]) -> None:
        self.output = output
        self.prompt: LLMProposalPrompt | None = None

    def __call__(self, prompt: LLMProposalPrompt) -> str | dict[str, Any]:
        self.prompt = prompt
        return self.output


def _identity(scopes: list[str] | None = None) -> IdentityContext:
    return IdentityContext(
        user_id="user-123",
        api_key_id="key-123",
        role=Role.OPERATOR,
        scopes=scopes or ["tools:inspect"],
    )


def _valid_low_risk_output() -> dict[str, Any]:
    skill = build_default_skill_registry().get_skill("inspect_sandbox_health")

    return {
        "proposed_skill_id": skill.skill_id,
        "proposed_skill_version": skill.version,
        "rationale": "The user asked to inspect sandbox issue health.",
        "steps": [step.model_dump(mode="json") for step in skill.steps],
    }


def _validator_result_for(output: str | dict[str, Any], scopes: list[str] | None = None):
    proposer = LLMProposer(client=CapturingClient(output))
    proposal = proposer.propose("Inspect sandbox issues.", _identity(scopes))
    validator = ProposalValidator(build_default_skill_registry())

    return proposal, validator.validate(proposal, _identity(scopes))


def test_llm_proposer_builds_prompt_and_parses_valid_json_string() -> None:
    client = CapturingClient(json.dumps(_valid_low_risk_output()))
    proposer = LLMProposer(client=client)

    proposal = proposer.propose("Inspect sandbox issues.", _identity())

    assert proposal.proposed_skill_id == "inspect_sandbox_health"
    assert proposal.proposed_skill_version == "1.0"
    assert proposal.steps[0].step_id == "inspect_issues"
    assert proposal.steps[0].tool_name == "inspect_sandbox_issues"
    assert proposal.steps[0].risk_level == RiskLevel.LOW

    prompt = client.prompt
    assert prompt is not None
    assert "The harness validates, authorizes" in prompt.system_prompt
    assert "Inspect sandbox issues." in prompt.user_prompt
    assert "skill_id: inspect_sandbox_health" in prompt.user_prompt
    assert "version: 1.0" in prompt.user_prompt
    assert "step_id: inspect_issues" in prompt.user_prompt
    assert "allowed_tool_names: inspect_sandbox_issues" in prompt.user_prompt
    assert "SkillProposal shape" in prompt.user_prompt
    assert "Do not include authorization" in prompt.user_prompt


def test_llm_proposer_accepts_dict_output_without_model_credentials() -> None:
    proposer = LLMProposer(client=CapturingClient(_valid_low_risk_output()))

    proposal = proposer.propose("Inspect sandbox issues.", _identity())

    assert proposal.proposed_skill_id == "inspect_sandbox_health"
    assert proposal.steps[0].tool_name == "inspect_sandbox_issues"


def test_hallucinated_skill_still_flows_to_validator_rejection() -> None:
    output = _valid_low_risk_output()
    output["proposed_skill_id"] = "hallucinated_skill"

    proposal, result = _validator_result_for(output)

    assert proposal.proposed_skill_id == "hallucinated_skill"
    assert result.status == ProposalValidationStatus.REJECTED
    assert result.rejection_reasons == [ProposalValidationReason.UNKNOWN_SKILL]


def test_hallucinated_tool_still_flows_to_validator_rejection() -> None:
    output = _valid_low_risk_output()
    output["steps"][0]["tool_name"] = "invented_trusted_tool"

    proposal, result = _validator_result_for(output)

    assert proposal.steps[0].tool_name == "invented_trusted_tool"
    assert result.status == ProposalValidationStatus.REJECTED
    assert result.rejection_reasons == [ProposalValidationReason.TOOL_NOT_ALLOWED]


def test_risk_understatement_still_flows_to_validator_rejection() -> None:
    skill = build_default_skill_registry().get_skill("simulate_sandbox_workflow")
    output = {
        "proposed_skill_id": skill.skill_id,
        "proposed_skill_version": skill.version,
        "rationale": "The user asked to simulate a workflow.",
        "steps": [step.model_dump(mode="json") for step in skill.steps],
    }
    output["steps"][0]["risk_level"] = RiskLevel.LOW.value

    proposal, result = _validator_result_for(
        output,
        scopes=["tools:trigger_workflow"],
    )

    assert proposal.proposed_skill_id == "simulate_sandbox_workflow"
    assert result.status == ProposalValidationStatus.REJECTED
    assert result.rejection_reasons == [ProposalValidationReason.RISK_MISMATCH]


def test_non_json_text_returns_malformed_proposal_with_evidence() -> None:
    proposal, result = _validator_result_for("not JSON at all")

    assert proposal.proposed_skill_id == MALFORMED_LLM_OUTPUT_SKILL_ID
    assert "Malformed LLM output" in proposal.rationale
    assert "invalid JSON" in proposal.rationale
    assert result.status == ProposalValidationStatus.REJECTED
    assert result.rejection_reasons == [ProposalValidationReason.UNKNOWN_SKILL]


def test_missing_required_fields_returns_malformed_proposal_with_evidence() -> None:
    proposal, result = _validator_result_for({"rationale": "Missing fields."})

    assert proposal.proposed_skill_id == MALFORMED_LLM_OUTPUT_SKILL_ID
    assert "Malformed LLM output" in proposal.rationale
    assert "schema validation failed" in proposal.rationale
    assert "proposed_skill_id" in proposal.rationale
    assert result.status == ProposalValidationStatus.REJECTED
    assert result.rejection_reasons == [ProposalValidationReason.UNKNOWN_SKILL]


def test_schema_invalid_output_returns_malformed_proposal_with_evidence() -> None:
    output = _valid_low_risk_output()
    output["steps"][0]["risk_level"] = "not-a-risk-level"

    proposal, result = _validator_result_for(output)

    assert proposal.proposed_skill_id == MALFORMED_LLM_OUTPUT_SKILL_ID
    assert "Malformed LLM output" in proposal.rationale
    assert "risk_level" in proposal.rationale
    assert result.status == ProposalValidationStatus.REJECTED
    assert result.rejection_reasons == [ProposalValidationReason.UNKNOWN_SKILL]
