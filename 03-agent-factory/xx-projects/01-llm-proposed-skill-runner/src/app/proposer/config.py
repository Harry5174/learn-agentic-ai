from dataclasses import dataclass


MALFORMED_LLM_OUTPUT_SKILL_ID = "__malformed_llm_output__"
MALFORMED_LLM_OUTPUT_VERSION = "malformed"
MALFORMED_LLM_OUTPUT_RATIONALE_PREFIX = (
    "Malformed LLM output rejected before validation"
)


@dataclass(frozen=True)
class LLMProposerConfig:
    """Local configuration for the optional LLM proposer adapter."""

    malformed_skill_id: str = MALFORMED_LLM_OUTPUT_SKILL_ID
    malformed_skill_version: str = MALFORMED_LLM_OUTPUT_VERSION
    malformed_rationale_prefix: str = MALFORMED_LLM_OUTPUT_RATIONALE_PREFIX
    max_error_detail_chars: int = 240
