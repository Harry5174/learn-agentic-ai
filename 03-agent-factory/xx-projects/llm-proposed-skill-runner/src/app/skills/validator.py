from app.identity.schemas import IdentityContext
from app.skills.registry import SkillRegistry
from app.skills.schemas import (
    ProposalValidationReason,
    ProposalValidationResult,
    ProposalValidationStatus,
    SkillProposal,
    SkillSpec,
    SkillStep,
)
from app.tools.schemas import RiskLevel


_RISK_RANK = {
    RiskLevel.LOW: 1,
    RiskLevel.MEDIUM: 2,
    RiskLevel.HIGH: 3,
}


class ProposalValidator:
    """Deterministically validate untrusted skill proposals."""

    def __init__(self, registry: SkillRegistry) -> None:
        self._registry = registry

    def validate(
        self,
        proposal: SkillProposal,
        identity: IdentityContext,
    ) -> ProposalValidationResult:
        if not self._registry.has_skill(proposal.proposed_skill_id):
            return self._rejected(
                proposal=proposal,
                skill=None,
                rejection_reasons=[ProposalValidationReason.UNKNOWN_SKILL],
                required_scopes=[],
                risk_level=None,
            )

        if not self._registry.has_skill(
            proposal.proposed_skill_id,
            version=proposal.proposed_skill_version,
        ):
            return self._rejected(
                proposal=proposal,
                skill=None,
                rejection_reasons=[
                    ProposalValidationReason.UNSUPPORTED_SKILL_VERSION
                ],
                required_scopes=[],
                risk_level=None,
            )

        skill = self._registry.get_skill(
            proposal.proposed_skill_id,
            version=proposal.proposed_skill_version,
        )
        step_by_id = {step.step_id: step for step in skill.steps}
        valid_registered_steps = self._valid_registered_steps(
            proposed_steps=proposal.steps,
            step_by_id=step_by_id,
        )
        required_scopes = self._required_scopes(
            skill=skill,
            steps=valid_registered_steps,
        )
        risk_level = self._risk_level(skill=skill, steps=valid_registered_steps)

        rejection_reasons = self._validation_reasons(
            proposal=proposal,
            identity=identity,
            required_scopes=required_scopes,
            step_by_id=step_by_id,
        )

        if rejection_reasons:
            return self._rejected(
                proposal=proposal,
                skill=skill,
                rejection_reasons=rejection_reasons,
                required_scopes=required_scopes,
                risk_level=risk_level,
            )

        return ProposalValidationResult(
            status=ProposalValidationStatus.ACCEPTED,
            proposal=proposal,
            skill=skill,
            rejection_reasons=[],
            required_scopes=required_scopes,
            risk_level=risk_level,
            approval_required=self._approval_required(
                skill=skill,
                steps=valid_registered_steps,
            ),
        )

    def _validation_reasons(
        self,
        proposal: SkillProposal,
        identity: IdentityContext,
        required_scopes: list[str],
        step_by_id: dict[str, SkillStep],
    ) -> list[ProposalValidationReason]:
        reasons: list[ProposalValidationReason] = []

        if not proposal.steps:
            self._add_reason(reasons, ProposalValidationReason.EMPTY_STEPS)

        seen_step_ids: set[str] = set()
        duplicate_step_ids: set[str] = set()
        for proposed_step in proposal.steps:
            if proposed_step.step_id in seen_step_ids:
                duplicate_step_ids.add(proposed_step.step_id)
            seen_step_ids.add(proposed_step.step_id)

            registered_step = step_by_id.get(proposed_step.step_id)
            if registered_step is None:
                self._add_reason(reasons, ProposalValidationReason.UNKNOWN_STEP)
                continue

            if proposed_step.tool_name != registered_step.tool_name:
                self._add_reason(reasons, ProposalValidationReason.TOOL_NOT_ALLOWED)

            if self._risk_rank(proposed_step.risk_level) < self._risk_rank(
                registered_step.risk_level
            ):
                self._add_reason(reasons, ProposalValidationReason.RISK_MISMATCH)

        if duplicate_step_ids:
            self._add_reason(reasons, ProposalValidationReason.DUPLICATE_STEP_ID)

        if not set(required_scopes).issubset(identity.scopes):
            self._add_reason(reasons, ProposalValidationReason.MISSING_REQUIRED_SCOPE)

        return reasons

    def _valid_registered_steps(
        self,
        proposed_steps: list[SkillStep],
        step_by_id: dict[str, SkillStep],
    ) -> list[SkillStep]:
        valid_steps: list[SkillStep] = []
        seen_step_ids: set[str] = set()

        for proposed_step in proposed_steps:
            if proposed_step.step_id in seen_step_ids:
                continue

            registered_step = step_by_id.get(proposed_step.step_id)
            if registered_step is not None:
                valid_steps.append(registered_step)

            seen_step_ids.add(proposed_step.step_id)

        return valid_steps

    def _required_scopes(
        self,
        skill: SkillSpec,
        steps: list[SkillStep],
    ) -> list[str]:
        scopes: list[str] = []

        for scope in skill.required_scopes:
            self._append_unique(scopes, scope)

        for step in steps:
            for scope in step.required_scopes:
                self._append_unique(scopes, scope)

        return scopes

    def _risk_level(self, skill: SkillSpec, steps: list[SkillStep]) -> RiskLevel:
        risk_level = skill.risk_level

        for step in steps:
            if self._risk_rank(step.risk_level) > self._risk_rank(risk_level):
                risk_level = step.risk_level

        return risk_level

    def _approval_required(self, skill: SkillSpec, steps: list[SkillStep]) -> bool:
        return skill.risk_level == RiskLevel.HIGH or any(
            step.risk_level == RiskLevel.HIGH for step in steps
        )

    def _rejected(
        self,
        proposal: SkillProposal,
        skill: SkillSpec | None,
        rejection_reasons: list[ProposalValidationReason],
        required_scopes: list[str],
        risk_level: RiskLevel | None,
    ) -> ProposalValidationResult:
        return ProposalValidationResult(
            status=ProposalValidationStatus.REJECTED,
            proposal=proposal,
            skill=skill,
            rejection_reasons=rejection_reasons,
            required_scopes=required_scopes,
            risk_level=risk_level,
            approval_required=(
                False
                if skill is None
                else self._approval_required(
                    skill=skill,
                    steps=self._valid_registered_steps(
                        proposed_steps=proposal.steps,
                        step_by_id={step.step_id: step for step in skill.steps},
                    ),
                )
            ),
        )

    def _risk_rank(self, risk_level: RiskLevel) -> int:
        return _RISK_RANK[risk_level]

    def _add_reason(
        self,
        reasons: list[ProposalValidationReason],
        reason: ProposalValidationReason,
    ) -> None:
        if reason not in reasons:
            reasons.append(reason)

    def _append_unique(self, values: list[str], value: str) -> None:
        if value not in values:
            values.append(value)
