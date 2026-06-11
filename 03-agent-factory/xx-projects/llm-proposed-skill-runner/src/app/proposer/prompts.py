from dataclasses import dataclass

from app.identity.schemas import IdentityContext
from app.skills.argument_schemas import ToolArgumentSpec
from app.skills.registry import SkillRegistry
from app.skills.schemas import SkillSpec


SYSTEM_PROMPT = """You propose skill runs for a local harness.

You only propose a SkillProposal. The harness validates, authorizes,
approval-gates, executes, and audits. Do not approve, authorize, execute tools,
invent tools, invent scopes, define policy, or decide final risk.
"""


@dataclass(frozen=True)
class LLMProposalPrompt:
    """Provider-neutral prompt bundle passed to an injected LLM client."""

    system_prompt: str
    user_prompt: str


def build_llm_proposal_prompt(
    task: str,
    identity: IdentityContext,
    registry: SkillRegistry,
) -> LLMProposalPrompt:
    """Build the provider-neutral prompt for a skill proposal request."""

    return LLMProposalPrompt(
        system_prompt=SYSTEM_PROMPT,
        user_prompt="\n\n".join(
            [
                "User task:",
                task,
                "Identity context:",
                _identity_summary(identity),
                build_registered_skill_summary(registry),
                build_skill_proposal_output_instructions(),
            ]
        ),
    )


def build_registered_skill_summary(registry: SkillRegistry) -> str:
    """Summarize only harness-registered skills and allowed steps/tools."""

    lines = ["Registered skills available for proposal:"]

    for skill in _sorted_skills(registry):
        lines.extend(
            [
                f"- skill_id: {skill.skill_id}",
                f"  version: {skill.version}",
                f"  allowed_tool_names: {', '.join(skill.allowed_tool_names)}",
                "  steps:",
            ]
        )

        for step in skill.steps:
            lines.extend(
                [
                    f"    - step_id: {step.step_id}",
                    f"      tool_name: {step.tool_name}",
                    f"      risk_level: {step.risk_level.value}",
                    f"      arguments: {_argument_summary(step.argument_specs)}",
                ]
            )

    return "\n".join(lines)


def build_skill_proposal_output_instructions() -> str:
    """Return the structured output instructions for SkillProposal JSON."""

    return """Return only one JSON object matching this SkillProposal shape:
{
  "proposed_skill_id": "registered skill_id",
  "proposed_skill_version": "registered version",
  "rationale": "brief reason for proposing this skill",
  "steps": [
    {
      "step_id": "registered step_id",
      "description": "step description",
      "tool_name": "registered tool_name for this step",
      "allowed_args_schema": {},
      "required_scopes": [],
      "risk_level": "low | medium | high",
      "arguments": {
        "argument_name": "proposed scalar value"
      }
    }
  ]
}

Rules:
- Use only registered skill IDs and versions from the context.
- Use only registered step IDs and tool names for the selected skill.
- Include only registered argument names for the selected step.
- Argument values may only be strings, integers, or booleans.
- Do not include identity, scope, approval, policy, risk, tool, or skill-control fields as arguments.
- Do not include authorization, approval, policy, execution, or audit decisions.
- Do not define new trusted tools, scopes, risk semantics, or credentials.
- Do not wrap the JSON in markdown or explanatory text."""


def _identity_summary(identity: IdentityContext) -> str:
    return "\n".join(
        [
            f"- user_id: {identity.user_id}",
            f"- role: {identity.role.value}",
            f"- scopes: {', '.join(identity.scopes)}",
            f"- tenant_id: {identity.tenant_id or 'none'}",
        ]
    )


def _sorted_skills(registry: SkillRegistry) -> list[SkillSpec]:
    return sorted(
        registry.list_skills(),
        key=lambda skill: (skill.skill_id, skill.version),
    )


def _argument_summary(argument_specs: list[ToolArgumentSpec]) -> str:
    if not argument_specs:
        return "none"

    return ", ".join(
        f"{spec.name} ({spec.value_type.value}, "
        f"{'required' if spec.required else 'optional'})"
        for spec in argument_specs
    )
