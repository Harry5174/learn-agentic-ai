from enum import StrEnum

from app.identity.schemas import IdentityContext
from app.proposer.base import SkillProposer
from app.skills.registry import build_default_skill_registry
from app.skills.schemas import SkillProposal, SkillProposalStep, SkillStep
from app.tools.github_comment import GITHUB_COMMENT_SKILL_ID, GITHUB_COMMENT_STEP_ID


class UnknownFakeRequestedSkillError(ValueError):
    """Raised when an API request names no supported fake demo skill."""


class FakeProposalScenario(StrEnum):
    """Deterministic fake proposer scenarios for tests and local demos."""

    VALID_LOW_RISK = "valid_low_risk"
    VALID_HIGH_RISK = "valid_high_risk"
    VALID_GITHUB_COMMENT = "valid_github_comment"
    INVALID_PROPOSAL = "invalid_proposal"
    UNKNOWN_SKILL = "unknown_skill"


FAKE_REQUESTED_SKILL_SCENARIOS: dict[str, FakeProposalScenario] = {
    "inspect_sandbox_health": FakeProposalScenario.VALID_LOW_RISK,
    "simulate_sandbox_workflow": FakeProposalScenario.VALID_HIGH_RISK,
    GITHUB_COMMENT_SKILL_ID: FakeProposalScenario.VALID_GITHUB_COMMENT,
}


def fake_scenario_for_requested_skill(skill_id: str) -> FakeProposalScenario:
    """Return the server-owned fake scenario for a requested demo skill."""

    try:
        return FAKE_REQUESTED_SKILL_SCENARIOS[skill_id]
    except KeyError as exc:
        raise UnknownFakeRequestedSkillError(
            f"Unsupported fake requested_skill_id: {skill_id}"
        ) from exc


class FakeProposer(SkillProposer):
    """Deterministic proposer that simulates model output without an LLM."""

    def __init__(
        self,
        scenario: FakeProposalScenario = FakeProposalScenario.VALID_LOW_RISK,
    ) -> None:
        self._scenario = scenario

    def propose(self, task: str, identity: IdentityContext) -> SkillProposal:
        rationale = (
            f"Fake proposer scenario {self._scenario.value} for "
            f"{identity.user_id}: {task}"
        )

        if self._scenario == FakeProposalScenario.VALID_LOW_RISK:
            return self._proposal_from_registered_skill(
                skill_id="inspect_sandbox_health",
                rationale=rationale,
                step_arguments={
                    "inspect_issues": {"repository": "sandbox/demo-repo"}
                },
            )

        if self._scenario == FakeProposalScenario.VALID_HIGH_RISK:
            return self._proposal_from_registered_skill(
                skill_id="simulate_sandbox_workflow",
                rationale=rationale,
                step_arguments={
                    "simulate_workflow": {
                        "workflow_name": "ci.yml",
                        "ref": "main",
                    }
                },
            )

        if self._scenario == FakeProposalScenario.VALID_GITHUB_COMMENT:
            return self._proposal_from_registered_skill(
                skill_id=GITHUB_COMMENT_SKILL_ID,
                rationale=rationale,
                step_arguments={
                    GITHUB_COMMENT_STEP_ID: {
                        "repository": "Harry5174/learn-agentic-ai",
                        "issue_number": 1,
                        "comment_body": "A deterministic fake GitHub comment.",
                    }
                },
            )

        if self._scenario == FakeProposalScenario.INVALID_PROPOSAL:
            proposal = self._proposal_from_registered_skill(
                skill_id="inspect_sandbox_health",
                rationale=rationale,
            )
            invalid_step = proposal.steps[0].model_copy(
                update={"tool_name": "draft_issue_comment"}
            )
            return proposal.model_copy(update={"steps": [invalid_step]})

        return self._unknown_skill_proposal(rationale=rationale)

    def _proposal_from_registered_skill(
        self,
        skill_id: str,
        rationale: str,
        step_arguments: dict[str, dict[str, object]] | None = None,
    ) -> SkillProposal:
        skill = build_default_skill_registry().get_skill(skill_id)
        step_arguments = step_arguments or {}

        return SkillProposal(
            proposed_skill_id=skill.skill_id,
            proposed_skill_version=skill.version,
            rationale=rationale,
            steps=[
                self._proposal_step_from_registered_step(
                    step,
                    arguments=step_arguments.get(step.step_id, {}),
                )
                for step in skill.steps
            ],
        )

    def _unknown_skill_proposal(self, rationale: str) -> SkillProposal:
        skill = build_default_skill_registry().get_skill("inspect_sandbox_health")

        return SkillProposal(
            proposed_skill_id="unknown_fake_skill",
            proposed_skill_version="1.0",
            rationale=rationale,
            steps=[self._proposal_step_from_registered_step(step) for step in skill.steps],
        )

    def _proposal_step_from_registered_step(
        self,
        step: SkillStep,
        arguments: dict[str, object] | None = None,
    ) -> SkillProposalStep:
        return SkillProposalStep(
            step_id=step.step_id,
            description=step.description,
            tool_name=step.tool_name,
            allowed_args_schema=step.allowed_args_schema,
            required_scopes=step.required_scopes,
            risk_level=step.risk_level,
            arguments=arguments or {},
        )
