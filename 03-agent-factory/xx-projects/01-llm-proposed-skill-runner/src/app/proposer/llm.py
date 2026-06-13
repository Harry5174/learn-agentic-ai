import json
from collections.abc import Mapping
from typing import Any, Protocol

from pydantic import ValidationError

from app.identity.schemas import IdentityContext
from app.proposer.base import SkillProposer
from app.proposer.config import LLMProposerConfig
from app.proposer.prompts import LLMProposalPrompt, build_llm_proposal_prompt
from app.skills.registry import SkillRegistry, build_default_skill_registry
from app.skills.schemas import SkillProposal


LLMRawOutput = str | Mapping[str, Any]


class LLMClient(Protocol):
    """Minimal provider-neutral boundary for model calls."""

    def __call__(self, prompt: LLMProposalPrompt) -> LLMRawOutput:
        """Return raw model output for the proposer to parse."""


class LLMProposer(SkillProposer):
    """Optional proposer that converts injected LLM output into SkillProposal."""

    def __init__(
        self,
        client: LLMClient,
        skill_registry: SkillRegistry | None = None,
        config: LLMProposerConfig | None = None,
    ) -> None:
        self._client = client
        self._skill_registry = skill_registry or build_default_skill_registry()
        self._config = config or LLMProposerConfig()

    def propose(self, task: str, identity: IdentityContext) -> SkillProposal:
        prompt = build_llm_proposal_prompt(
            task=task,
            identity=identity,
            registry=self._skill_registry,
        )

        try:
            raw_output = self._client(prompt)
        except Exception as exc:
            return self._malformed_proposal(
                f"LLM client failed: {exc.__class__.__name__}: {exc}"
            )

        return self._parse_output(raw_output)

    def _parse_output(self, raw_output: LLMRawOutput) -> SkillProposal:
        if isinstance(raw_output, str):
            try:
                raw_value = json.loads(raw_output)
            except json.JSONDecodeError as exc:
                return self._malformed_proposal(
                    "invalid JSON: "
                    f"{exc.msg} at line {exc.lineno} column {exc.colno}"
                )
        elif isinstance(raw_output, Mapping):
            raw_value = dict(raw_output)
        else:
            return self._malformed_proposal(
                f"unsupported response type: {type(raw_output).__name__}"
            )

        try:
            return SkillProposal.model_validate(raw_value)
        except ValidationError as exc:
            return self._malformed_proposal(
                "SkillProposal schema validation failed: "
                f"{_first_validation_error(exc)}"
            )

    def _malformed_proposal(self, reason: str) -> SkillProposal:
        return SkillProposal(
            proposed_skill_id=self._config.malformed_skill_id,
            proposed_skill_version=self._config.malformed_skill_version,
            rationale=(
                f"{self._config.malformed_rationale_prefix}: "
                f"{_truncate(reason, self._config.max_error_detail_chars)}"
            ),
            steps=[],
        )


def _first_validation_error(exc: ValidationError) -> str:
    errors = exc.errors()

    if not errors:
        return str(exc)

    first_error = errors[0]
    location = ".".join(str(part) for part in first_error.get("loc", ()))
    message = first_error.get("msg", str(exc))

    return f"{location or 'root'}: {message}"


def _truncate(value: str, max_chars: int) -> str:
    if max_chars <= 0 or len(value) <= max_chars:
        return value

    return f"{value[: max_chars - 3]}..."
