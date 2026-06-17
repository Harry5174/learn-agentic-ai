from app.identity.schemas import IdentityContext
from app.skills.argument_schemas import (
    FORBIDDEN_ARGUMENT_NAMES,
    ArgumentValidationIssue,
    ArgumentValidationStatus,
    ArgumentValueType,
    ScalarArgumentValue,
    ToolArgumentSpec,
    ValidatedSkillPlan,
    ValidatedStepArguments,
)
from app.skills.registry import SkillRegistry
from app.skills.schemas import (
    ProposalValidationReason,
    ProposalValidationResult,
    ProposalValidationStatus,
    SkillProposal,
    SkillProposalStep,
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
                validated_skill_plan=None,
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
                validated_skill_plan=None,
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

        validated_skill_plan: ValidatedSkillPlan | None = None
        if not rejection_reasons:
            validated_skill_plan = self._validate_arguments(
                proposal=proposal,
                skill=skill,
                step_by_id=step_by_id,
            )
            if validated_skill_plan.status == ArgumentValidationStatus.REJECTED:
                self._add_reason(
                    rejection_reasons,
                    ProposalValidationReason.INVALID_ARGUMENTS,
                )

        if rejection_reasons:
            return self._rejected(
                proposal=proposal,
                skill=skill,
                rejection_reasons=rejection_reasons,
                required_scopes=required_scopes,
                risk_level=risk_level,
                validated_skill_plan=(
                    validated_skill_plan
                    if validated_skill_plan is not None
                    and validated_skill_plan.status == ArgumentValidationStatus.REJECTED
                    else None
                ),
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
            validated_skill_plan=validated_skill_plan,
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
        proposed_steps: list[SkillProposalStep],
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
        validated_skill_plan: ValidatedSkillPlan | None,
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
            validated_skill_plan=validated_skill_plan,
        )

    def _validate_arguments(
        self,
        proposal: SkillProposal,
        skill: SkillSpec,
        step_by_id: dict[str, SkillStep],
    ) -> ValidatedSkillPlan:
        issues: list[ArgumentValidationIssue] = []
        step_arguments: list[ValidatedStepArguments] = []

        for proposed_step in proposal.steps:
            registered_step = step_by_id[proposed_step.step_id]
            validated_arguments = self._validate_step_arguments(
                proposed_step=proposed_step,
                registered_step=registered_step,
                issues=issues,
            )

            if validated_arguments is not None:
                step_arguments.append(validated_arguments)

        if issues:
            return ValidatedSkillPlan(
                status=ArgumentValidationStatus.REJECTED,
                skill_id=skill.skill_id,
                skill_version=skill.version,
                step_arguments=[],
                issues=issues,
            )

        return ValidatedSkillPlan(
            status=ArgumentValidationStatus.ACCEPTED,
            skill_id=skill.skill_id,
            skill_version=skill.version,
            step_arguments=step_arguments,
            issues=[],
        )

    def _validate_step_arguments(
        self,
        proposed_step: SkillProposalStep,
        registered_step: SkillStep,
        issues: list[ArgumentValidationIssue],
    ) -> ValidatedStepArguments | None:
        spec_by_name = {
            argument_spec.name: argument_spec
            for argument_spec in registered_step.argument_specs
        }
        validated_arguments: dict[str, ScalarArgumentValue] = {}
        redacted_argument_names: list[str] = []

        if len(spec_by_name) != len(registered_step.argument_specs):
            self._add_argument_issue(
                issues=issues,
                step_id=registered_step.step_id,
                argument_name=None,
                reason_code="invalid_argument_schema",
                message="Trusted argument schema contains duplicate names.",
            )
            return None

        for argument_name in proposed_step.arguments:
            if argument_name in FORBIDDEN_ARGUMENT_NAMES:
                self._add_argument_issue(
                    issues=issues,
                    step_id=registered_step.step_id,
                    argument_name=argument_name,
                    reason_code="forbidden_argument_name",
                    message="Argument name is reserved for the harness.",
                )
            elif argument_name not in spec_by_name:
                self._add_argument_issue(
                    issues=issues,
                    step_id=registered_step.step_id,
                    argument_name=argument_name,
                    reason_code="unknown_argument",
                    message="Argument is not allowed for this registered step.",
                )

        for argument_spec in registered_step.argument_specs:
            if self._schema_invalid(
                argument_spec=argument_spec,
                step_id=registered_step.step_id,
                issues=issues,
            ):
                continue

            if argument_spec.name in proposed_step.arguments:
                argument_value = proposed_step.arguments[argument_spec.name]
            elif argument_spec.default is not None:
                argument_value = argument_spec.default
            elif argument_spec.required:
                self._add_argument_issue(
                    issues=issues,
                    step_id=registered_step.step_id,
                    argument_name=argument_spec.name,
                    reason_code="missing_required_argument",
                    message="Required argument is missing.",
                )
                continue
            else:
                continue

            if not self._value_matches_type(argument_value, argument_spec.value_type):
                self._add_argument_issue(
                    issues=issues,
                    step_id=registered_step.step_id,
                    argument_name=argument_spec.name,
                    reason_code="invalid_argument_type",
                    message="Argument value does not match the trusted scalar type.",
                )
                continue

            if (
                argument_spec.allowed_values
                and argument_value not in argument_spec.allowed_values
            ):
                self._add_argument_issue(
                    issues=issues,
                    step_id=registered_step.step_id,
                    argument_name=argument_spec.name,
                    reason_code="invalid_allowed_value",
                    message="Argument value is not in the trusted allowed set.",
                )
                continue

            if (
                argument_spec.max_length is not None
                and isinstance(argument_value, str)
                and len(argument_value) > argument_spec.max_length
            ):
                self._add_argument_issue(
                    issues=issues,
                    step_id=registered_step.step_id,
                    argument_name=argument_spec.name,
                    reason_code="string_too_long",
                    message="String argument exceeds the trusted maximum length.",
                )
                continue

            validated_arguments[argument_spec.name] = argument_value
            if argument_spec.sensitive:
                redacted_argument_names.append(argument_spec.name)

        return ValidatedStepArguments(
            step_id=registered_step.step_id,
            arguments=validated_arguments,
            redacted_argument_names=redacted_argument_names,
        )

    def _schema_invalid(
        self,
        argument_spec: ToolArgumentSpec,
        step_id: str,
        issues: list[ArgumentValidationIssue],
    ) -> bool:
        invalid = False

        if argument_spec.name in FORBIDDEN_ARGUMENT_NAMES:
            self._add_argument_issue(
                issues=issues,
                step_id=step_id,
                argument_name=argument_spec.name,
                reason_code="invalid_argument_schema",
                message="Trusted argument schema uses a reserved argument name.",
            )
            invalid = True

        if argument_spec.default is not None and not self._value_matches_type(
            argument_spec.default,
            argument_spec.value_type,
        ):
            self._add_argument_issue(
                issues=issues,
                step_id=step_id,
                argument_name=argument_spec.name,
                reason_code="invalid_argument_schema",
                message="Trusted argument schema default does not match its type.",
            )
            invalid = True

        for allowed_value in argument_spec.allowed_values:
            if not self._value_matches_type(allowed_value, argument_spec.value_type):
                self._add_argument_issue(
                    issues=issues,
                    step_id=step_id,
                    argument_name=argument_spec.name,
                    reason_code="invalid_argument_schema",
                    message="Trusted argument schema allowed value has the wrong type.",
                )
                invalid = True
                break

        if argument_spec.max_length is not None:
            if (
                argument_spec.value_type != ArgumentValueType.STRING
                or argument_spec.max_length < 1
            ):
                self._add_argument_issue(
                    issues=issues,
                    step_id=step_id,
                    argument_name=argument_spec.name,
                    reason_code="invalid_argument_schema",
                    message="Trusted argument schema has an invalid max_length.",
                )
                invalid = True

        return invalid

    def _value_matches_type(
        self,
        value: object,
        value_type: ArgumentValueType,
    ) -> bool:
        if value_type == ArgumentValueType.STRING:
            return isinstance(value, str)

        if value_type == ArgumentValueType.INTEGER:
            return isinstance(value, int) and not isinstance(value, bool)

        if value_type == ArgumentValueType.BOOLEAN:
            return isinstance(value, bool)

        return False

    def _add_argument_issue(
        self,
        issues: list[ArgumentValidationIssue],
        step_id: str | None,
        argument_name: str | None,
        reason_code: str,
        message: str,
    ) -> None:
        issue = ArgumentValidationIssue(
            step_id=step_id,
            argument_name=argument_name,
            reason_code=reason_code,
            message=message,
        )
        if issue not in issues:
            issues.append(issue)

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
