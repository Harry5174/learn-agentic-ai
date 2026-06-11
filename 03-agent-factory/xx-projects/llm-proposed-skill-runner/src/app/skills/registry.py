from app.skills.errors import UnknownSkillError
from app.skills.schemas import SkillSpec, SkillStep
from app.tools.schemas import RiskLevel


class SkillRegistry:
    """Controlled registry for static skill specifications."""

    def __init__(self) -> None:
        self._skills: dict[tuple[str, str], SkillSpec] = {}

    def register(self, spec: SkillSpec) -> None:
        self._skills[(spec.skill_id, spec.version)] = spec

    def list_skills(self) -> list[SkillSpec]:
        return list(self._skills.values())

    def get_skill(self, skill_id: str, version: str | None = None) -> SkillSpec:
        skill = self._find_skill(skill_id=skill_id, version=version)

        if skill is None:
            raise UnknownSkillError(f"Unknown skill: {skill_id}")

        return skill

    def has_skill(self, skill_id: str, version: str | None = None) -> bool:
        return self._find_skill(skill_id=skill_id, version=version) is not None

    def _find_skill(self, skill_id: str, version: str | None) -> SkillSpec | None:
        if version is not None:
            return self._skills.get((skill_id, version))

        for (registered_skill_id, _), spec in self._skills.items():
            if registered_skill_id == skill_id:
                return spec

        return None


def build_default_skill_registry() -> SkillRegistry:
    """Build the default Sprint 1 static skill registry."""

    registry = SkillRegistry()

    registry.register(
        SkillSpec(
            skill_id="inspect_sandbox_health",
            version="1.0",
            name="Inspect sandbox health",
            description="Inspect predictable sandbox issue status data.",
            steps=[
                SkillStep(
                    step_id="inspect_issues",
                    description="Inspect sandbox issues using dry-run data.",
                    tool_name="inspect_sandbox_issues",
                    allowed_args_schema={
                        "type": "object",
                        "properties": {"repository": {"type": "string"}},
                    },
                    required_scopes=["tools:inspect"],
                    risk_level=RiskLevel.LOW,
                )
            ],
            required_scopes=["tools:inspect"],
            risk_level=RiskLevel.LOW,
            input_schema={
                "type": "object",
                "properties": {"repository": {"type": "string"}},
            },
            tags=["inspection", "dry-run"],
        )
    )

    registry.register(
        SkillSpec(
            skill_id="draft_sandbox_issue_comment",
            version="1.0",
            name="Draft sandbox issue comment",
            description="Draft an issue comment payload without posting it.",
            steps=[
                SkillStep(
                    step_id="draft_comment",
                    description="Create a dry-run issue comment draft.",
                    tool_name="draft_issue_comment",
                    allowed_args_schema={
                        "type": "object",
                        "properties": {
                            "issue_id": {"type": "integer"},
                            "comment_body": {"type": "string"},
                        },
                    },
                    required_scopes=["tools:draft"],
                    risk_level=RiskLevel.MEDIUM,
                )
            ],
            required_scopes=["tools:draft"],
            risk_level=RiskLevel.MEDIUM,
            input_schema={
                "type": "object",
                "properties": {
                    "issue_id": {"type": "integer"},
                    "comment_body": {"type": "string"},
                },
            },
            tags=["draft", "dry-run"],
        )
    )

    registry.register(
        SkillSpec(
            skill_id="simulate_sandbox_workflow",
            version="1.0",
            name="Simulate sandbox workflow",
            description="Simulate a workflow trigger without executing it.",
            steps=[
                SkillStep(
                    step_id="simulate_workflow",
                    description="Simulate a high-risk workflow trigger.",
                    tool_name="trigger_workflow_dry_run",
                    allowed_args_schema={
                        "type": "object",
                        "properties": {
                            "workflow_name": {"type": "string"},
                            "ref": {"type": "string"},
                        },
                    },
                    required_scopes=["tools:trigger_workflow"],
                    risk_level=RiskLevel.HIGH,
                )
            ],
            required_scopes=["tools:trigger_workflow"],
            risk_level=RiskLevel.HIGH,
            input_schema={
                "type": "object",
                "properties": {
                    "workflow_name": {"type": "string"},
                    "ref": {"type": "string"},
                },
            },
            tags=["workflow", "dry-run"],
        )
    )

    return registry
