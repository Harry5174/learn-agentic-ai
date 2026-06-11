from enum import StrEnum

from app.identity.schemas import IdentityContext
from app.proposer.base import SkillProposer
from app.skills.registry import build_default_skill_registry
from app.skills.schemas import SkillProposal


class FakeProposalScenario(StrEnum):
    """Deterministic fake proposer scenarios for tests and local demos."""

    VALID_LOW_RISK = "valid_low_risk"
    VALID_HIGH_RISK = "valid_high_risk"
    INVALID_PROPOSAL = "invalid_proposal"
    UNKNOWN_SKILL = "unknown_skill"


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
            )

        if self._scenario == FakeProposalScenario.VALID_HIGH_RISK:
            return self._proposal_from_registered_skill(
                skill_id="simulate_sandbox_workflow",
                rationale=rationale,
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
    ) -> SkillProposal:
        skill = build_default_skill_registry().get_skill(skill_id)

        return SkillProposal(
            proposed_skill_id=skill.skill_id,
            proposed_skill_version=skill.version,
            rationale=rationale,
            steps=[step.model_copy(deep=True) for step in skill.steps],
        )

    def _unknown_skill_proposal(self, rationale: str) -> SkillProposal:
        skill = build_default_skill_registry().get_skill("inspect_sandbox_health")

        return SkillProposal(
            proposed_skill_id="unknown_fake_skill",
            proposed_skill_version="1.0",
            rationale=rationale,
            steps=[step.model_copy(deep=True) for step in skill.steps],
        )
