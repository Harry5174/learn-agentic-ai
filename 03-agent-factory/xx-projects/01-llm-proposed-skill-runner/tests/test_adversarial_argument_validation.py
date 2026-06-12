import json
from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.api import skill_routes
from app.api.main import create_app
from app.api.skill_routes import skill_run_summary_from_state
from app.api.skill_schemas import ProposerMode
from app.identity.config import ADMIN_API_KEY, VIEWER_API_KEY
from app.identity.resolver import resolve_identity_from_api_key
from app.identity.schemas import IdentityContext, Role
from app.skills.argument_schemas import (
    ArgumentValidationStatus,
    ArgumentValueType,
    ToolArgumentSpec,
    ValidatedSkillPlan,
)
from app.skills.registry import SkillRegistry, build_default_skill_registry
from app.skills.schemas import (
    ProposalValidationReason,
    ProposalValidationResult,
    ProposalValidationStatus,
    SkillProposal,
    SkillProposalStep,
    SkillSpec,
    SkillStep,
)
from app.skills.validator import ProposalValidator
from app.skill_graph import graph as skill_graph_module
from app.skill_graph.graph import build_skill_execution_graph
from app.skill_graph.service import SkillGraphService
from app.state.schemas import TaskStatus
from app.tools.registry import ToolRegistry
from app.tools.schemas import RiskLevel, ToolExecutionResult, ToolSpec


def _identity(scopes: list[str] | None = None) -> IdentityContext:
    return IdentityContext(
        user_id="adversarial-user",
        api_key_id="adversarial-key",
        role=Role.OPERATOR,
        scopes=scopes
        or ["tools:inspect", "tools:draft", "tools:trigger_workflow"],
    )


def _proposal(
    skill_id: str,
    arguments_by_step_id: dict[str, dict[str, Any]] | None = None,
    registry: SkillRegistry | None = None,
) -> SkillProposal:
    registry = registry or build_default_skill_registry()
    skill = registry.get_skill(skill_id, version="1.0")
    arguments_by_step_id = arguments_by_step_id or {}

    return SkillProposal(
        proposed_skill_id=skill.skill_id,
        proposed_skill_version=skill.version,
        rationale="Adversarial boundary test proposal.",
        steps=[
            SkillProposalStep(
                step_id=step.step_id,
                description=step.description,
                tool_name=step.tool_name,
                allowed_args_schema=step.allowed_args_schema,
                required_scopes=step.required_scopes,
                risk_level=step.risk_level,
                arguments=arguments_by_step_id.get(step.step_id, {}),
            )
            for step in skill.steps
        ],
    )


def _validate(
    proposal: SkillProposal,
    registry: SkillRegistry | None = None,
) -> ProposalValidationResult:
    validator = ProposalValidator(registry or build_default_skill_registry())

    return validator.validate(proposal, _identity())


def _issue_codes(result: ProposalValidationResult) -> list[str]:
    assert result.validated_skill_plan is not None

    return [issue.reason_code for issue in result.validated_skill_plan.issues]


def _issue_names(result: ProposalValidationResult) -> list[str | None]:
    assert result.validated_skill_plan is not None

    return [issue.argument_name for issue in result.validated_skill_plan.issues]


def _single_step_registry(argument_specs: list[ToolArgumentSpec]) -> SkillRegistry:
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
                    argument_specs=argument_specs,
                    required_scopes=["tools:inspect"],
                    risk_level=RiskLevel.LOW,
                )
            ],
            required_scopes=["tools:inspect"],
            risk_level=RiskLevel.LOW,
        )
    )

    return registry


class StaticProposalProposer:
    def __init__(
        self,
        skill_id: str,
        arguments_by_step_id: dict[str, dict[str, Any]],
        registry: SkillRegistry | None = None,
    ) -> None:
        self._skill_id = skill_id
        self._arguments_by_step_id = arguments_by_step_id
        self._registry = registry or build_default_skill_registry()

    def propose(self, task: str, identity: IdentityContext) -> SkillProposal:
        skill = self._registry.get_skill(self._skill_id, version="1.0")

        return SkillProposal(
            proposed_skill_id=skill.skill_id,
            proposed_skill_version=skill.version,
            rationale=f"Adversarial proposal for {identity.user_id}: {task}",
            steps=[
                SkillProposalStep(
                    step_id=step.step_id,
                    description=step.description,
                    tool_name=step.tool_name,
                    allowed_args_schema=step.allowed_args_schema,
                    required_scopes=step.required_scopes,
                    risk_level=step.risk_level,
                    arguments=self._arguments_by_step_id.get(step.step_id, {}),
                )
                for step in skill.steps
            ],
        )


def _recording_tool_registry(
    *,
    tool_name: str,
    required_scopes: list[str],
    risk_level: RiskLevel,
    calls: list[dict[str, Any]],
) -> ToolRegistry:
    registry = ToolRegistry()

    def record_execution(arguments: dict[str, Any]) -> ToolExecutionResult:
        calls.append(dict(arguments))
        return ToolExecutionResult(
            tool_name=tool_name,
            success=True,
            result=dict(arguments),
            dry_run=True,
            message="Recorded validated dry-run arguments.",
        )

    registry.register(
        ToolSpec(
            name=tool_name,
            description="Recording dry-run test tool.",
            required_scopes=required_scopes,
            risk_level=risk_level,
        ),
        record_execution,
    )

    return registry


def _invoke_graph(
    *,
    proposer: StaticProposalProposer,
    identity: IdentityContext,
    skill_registry: SkillRegistry | None = None,
    tool_registry: ToolRegistry | None = None,
    run_id: str = "adversarial-skill-run",
) -> dict[str, Any]:
    graph = build_skill_execution_graph(
        proposer=proposer,
        skill_registry=skill_registry,
        tool_registry=tool_registry,
    )

    return graph.invoke(
        {
            "run_id": run_id,
            "task": "Run an adversarial argument boundary test.",
            "identity": identity,
            "status": TaskStatus.CREATED,
            "policy_decisions": [],
            "step_arguments": {},
            "tool_results": [],
            "audit_trail": [],
        },
        config={"configurable": {"thread_id": run_id}},
    )


@pytest.mark.parametrize(
    ("skill_id", "arguments_by_step_id", "expected_issue_code"),
    [
        (
            "inspect_sandbox_health",
            {"inspect_issues": {"repository": "sandbox/demo-repo", "extra": "x"}},
            "unknown_argument",
        ),
        (
            "draft_sandbox_issue_comment",
            {"draft_comment": {"issue_id": 1}},
            "missing_required_argument",
        ),
        (
            "inspect_sandbox_health",
            {"inspect_issues": {"repository": 123}},
            "invalid_argument_type",
        ),
        (
            "draft_sandbox_issue_comment",
            {"draft_comment": {"issue_id": True, "comment_body": "safe draft"}},
            "invalid_argument_type",
        ),
        (
            "draft_sandbox_issue_comment",
            {"draft_comment": {"issue_id": "1", "comment_body": "safe draft"}},
            "invalid_argument_type",
        ),
        (
            "inspect_sandbox_health",
            {"inspect_issues": {"repository": {"name": "sandbox/demo-repo"}}},
            "invalid_argument_type",
        ),
        (
            "inspect_sandbox_health",
            {"inspect_issues": {"repository": ["sandbox/demo-repo"]}},
            "invalid_argument_type",
        ),
    ],
)
def test_argument_schema_attacks_are_rejected(
    skill_id: str,
    arguments_by_step_id: dict[str, dict[str, Any]],
    expected_issue_code: str,
) -> None:
    result = _validate(_proposal(skill_id, arguments_by_step_id))

    assert result.status == ProposalValidationStatus.REJECTED
    assert result.rejection_reasons == [ProposalValidationReason.INVALID_ARGUMENTS]
    assert result.validated_skill_plan is not None
    assert result.validated_skill_plan.status == ArgumentValidationStatus.REJECTED
    assert result.validated_skill_plan.step_arguments == []
    assert expected_issue_code in _issue_codes(result)


def test_overlong_string_argument_is_rejected() -> None:
    registry = _single_step_registry(
        [
            ToolArgumentSpec(
                name="repository",
                value_type=ArgumentValueType.STRING,
                max_length=8,
            )
        ]
    )

    result = _validate(
        _proposal(
            "inspect_sandbox_health",
            {"inspect_issues": {"repository": "sandbox/demo-repo"}},
            registry=registry,
        ),
        registry=registry,
    )

    assert result.status == ProposalValidationStatus.REJECTED
    assert _issue_codes(result) == ["string_too_long"]


def test_invalid_allowed_value_argument_is_rejected() -> None:
    registry = _single_step_registry(
        [
            ToolArgumentSpec(
                name="repository",
                value_type=ArgumentValueType.STRING,
                allowed_values=["sandbox/demo-repo"],
            )
        ]
    )

    result = _validate(
        _proposal(
            "inspect_sandbox_health",
            {"inspect_issues": {"repository": "sandbox/other-repo"}},
            registry=registry,
        ),
        registry=registry,
    )

    assert result.status == ProposalValidationStatus.REJECTED
    assert _issue_codes(result) == ["invalid_allowed_value"]


@pytest.mark.parametrize(
    "argument_name",
    [
        "user_id",
        "role",
        "roles",
        "scope",
        "scopes",
        "identity",
        "api_key",
        "api_token",
        "approval_authority",
        "approval_decision",
        "policy_decision",
        "policy_override",
        "risk_override",
        "risk_level",
        "requires_approval",
        "tool_name",
        "tool_id",
        "skill_id",
        "skill_version",
    ],
)
def test_control_plane_smuggling_argument_names_are_rejected(
    argument_name: str,
) -> None:
    result = _validate(
        _proposal(
            "inspect_sandbox_health",
            {
                "inspect_issues": {
                    "repository": "sandbox/demo-repo",
                    argument_name: "attacker-controlled",
                }
            },
        )
    )

    assert result.status == ProposalValidationStatus.REJECTED
    assert _issue_codes(result) == ["forbidden_argument_name"]
    assert _issue_names(result) == [argument_name]


def test_raw_proposed_arguments_do_not_execute_when_validated_plan_differs() -> None:
    calls: list[dict[str, Any]] = []
    viewer = resolve_identity_from_api_key(VIEWER_API_KEY)
    registry = _single_step_registry(
        [
            ToolArgumentSpec(
                name="repository",
                value_type=ArgumentValueType.STRING,
                required=False,
                default="sandbox/validator-default",
            )
        ]
    )

    state = _invoke_graph(
        proposer=StaticProposalProposer(
            "inspect_sandbox_health",
            {"inspect_issues": {}},
            registry=registry,
        ),
        identity=viewer,
        skill_registry=registry,
        tool_registry=_recording_tool_registry(
            tool_name="inspect_sandbox_issues",
            required_scopes=["tools:inspect"],
            risk_level=RiskLevel.LOW,
            calls=calls,
        ),
    )

    assert state["status"] == TaskStatus.COMPLETED
    assert state["proposal"].steps[0].arguments == {}
    assert calls == [{"repository": "sandbox/validator-default"}]


@pytest.mark.parametrize(
    ("invalid_argument_name", "expected_issue_code"),
    [
        ("api_token", "forbidden_argument_name"),
        ("extra", "unknown_argument"),
    ],
)
def test_invalid_arguments_never_reach_tool_registry_execute(
    invalid_argument_name: str,
    expected_issue_code: str,
) -> None:
    calls: list[dict[str, Any]] = []
    viewer = resolve_identity_from_api_key(VIEWER_API_KEY)

    state = _invoke_graph(
        proposer=StaticProposalProposer(
            "inspect_sandbox_health",
            {
                "inspect_issues": {
                    "repository": "sandbox/demo-repo",
                    invalid_argument_name: "RAW_SHOULD_NOT_EXECUTE",
                }
            },
        ),
        identity=viewer,
        tool_registry=_recording_tool_registry(
            tool_name="inspect_sandbox_issues",
            required_scopes=["tools:inspect"],
            risk_level=RiskLevel.LOW,
            calls=calls,
        ),
    )

    assert state["status"] == TaskStatus.FAILED
    assert state["validation_result"].status == ProposalValidationStatus.REJECTED
    assert state["validation_result"].rejection_reasons == [
        ProposalValidationReason.INVALID_ARGUMENTS
    ]
    assert _issue_codes(state["validation_result"]) == [expected_issue_code]
    assert state["policy_decisions"] == []
    assert state["tool_results"] == []
    assert calls == []


def test_missing_validated_step_fails_closed_without_execution(monkeypatch) -> None:
    calls: list[dict[str, Any]] = []
    viewer = resolve_identity_from_api_key(VIEWER_API_KEY)

    def validate_with_missing_step(self, proposal, identity):
        skill = build_default_skill_registry().get_skill(
            "inspect_sandbox_health",
            version="1.0",
        )
        return ProposalValidationResult(
            status=ProposalValidationStatus.ACCEPTED,
            proposal=proposal,
            skill=skill,
            rejection_reasons=[],
            required_scopes=["tools:inspect"],
            risk_level=RiskLevel.LOW,
            approval_required=False,
            validated_skill_plan=ValidatedSkillPlan(
                status=ArgumentValidationStatus.ACCEPTED,
                skill_id=skill.skill_id,
                skill_version=skill.version,
                step_arguments=[],
                issues=[],
            ),
        )

    monkeypatch.setattr(
        skill_graph_module.ProposalValidator,
        "validate",
        validate_with_missing_step,
    )

    state = _invoke_graph(
        proposer=StaticProposalProposer(
            "inspect_sandbox_health",
            {"inspect_issues": {"repository": "RAW_SHOULD_NOT_EXECUTE"}},
        ),
        identity=viewer,
        tool_registry=_recording_tool_registry(
            tool_name="inspect_sandbox_issues",
            required_scopes=["tools:inspect"],
            risk_level=RiskLevel.LOW,
            calls=calls,
        ),
    )

    assert state["status"] == TaskStatus.FAILED
    assert "Validated arguments are missing" in state["error_message"]
    assert state["tool_results"] == []
    assert calls == []


def test_raw_rejected_values_are_absent_from_api_response_and_audit(
    monkeypatch,
) -> None:
    raw_rejected_value = "RAW_SECRET_TOKEN_DO_NOT_LEAK_E23"
    invalid_service = SkillGraphService(
        proposer=StaticProposalProposer(
            "inspect_sandbox_health",
            {"inspect_issues": {"api_token": raw_rejected_value}},
        )
    )
    monkeypatch.setattr(skill_routes, "_skill_run_service", invalid_service)
    client = TestClient(create_app())

    response = client.post(
        "/skill-runs",
        headers={"X-API-Key": VIEWER_API_KEY},
        json={"task": "Inspect sandbox health."},
    )

    assert response.status_code == 202
    assert raw_rejected_value not in response.text

    body = response.json()
    assert body["status"] == "failed"
    assert body["validation"]["status"] == "rejected"
    assert body["validation"]["rejection_reasons"] == ["invalid_arguments"]
    assert body["validation"]["argument_validation_status"] == "rejected"
    assert body["validation"]["validated_argument_names"] == {}
    assert body["validation"]["redacted_argument_names"] == {}
    assert body["validation"]["argument_validation_issue_codes"] == [
        "forbidden_argument_name"
    ]

    audit_response = client.get(f"/skill-runs/{body['run_id']}/audit")

    assert audit_response.status_code == 200
    assert raw_rejected_value not in audit_response.text
    assert "forbidden_argument_name" in audit_response.text


def test_sensitive_accepted_values_are_summarized_by_name_not_value() -> None:
    secret_value = "ACCEPTED_SECRET_REPOSITORY_VALUE"
    calls: list[dict[str, Any]] = []
    viewer = resolve_identity_from_api_key(VIEWER_API_KEY)
    registry = _single_step_registry(
        [
            ToolArgumentSpec(
                name="repository",
                value_type=ArgumentValueType.STRING,
                required=True,
                sensitive=True,
            )
        ]
    )

    state = _invoke_graph(
        proposer=StaticProposalProposer(
            "inspect_sandbox_health",
            {"inspect_issues": {"repository": secret_value}},
            registry=registry,
        ),
        identity=viewer,
        skill_registry=registry,
        tool_registry=_recording_tool_registry(
            tool_name="inspect_sandbox_issues",
            required_scopes=["tools:inspect"],
            risk_level=RiskLevel.LOW,
            calls=calls,
        ),
    )

    assert state["status"] == TaskStatus.COMPLETED
    assert calls == [{"repository": secret_value}]

    audit_json = json.dumps(
        [event.model_dump(mode="json") for event in state["audit_trail"]],
        sort_keys=True,
    )
    assert secret_value not in audit_json
    assert '"validated_argument_names": {"inspect_issues": ["repository"]}' in audit_json
    assert '"redacted_argument_names": {"inspect_issues": ["repository"]}' in audit_json

    summary = skill_run_summary_from_state(state=state, proposer_mode=ProposerMode.FAKE)
    summary_json = summary.model_dump_json()

    assert secret_value not in summary_json
    assert summary.validation is not None
    assert summary.validation.validated_argument_names == {
        "inspect_issues": ["repository"]
    }
    assert summary.validation.redacted_argument_names == {
        "inspect_issues": ["repository"]
    }


def test_high_risk_workflow_with_valid_arguments_still_pauses_before_execution() -> None:
    service = SkillGraphService(
        proposer=StaticProposalProposer(
            "simulate_sandbox_workflow",
            {"simulate_workflow": {"workflow_name": "deploy.yml", "ref": "main"}},
        )
    )
    admin = resolve_identity_from_api_key(ADMIN_API_KEY)

    state = service.start_run(
        task="Simulate a high-risk sandbox workflow.",
        identity=admin,
    )

    assert state["status"] == TaskStatus.PAUSED_FOR_APPROVAL
    assert state["approval_request"].tool_arguments == {
        "workflow_name": "deploy.yml",
        "ref": "main",
    }
    assert state["tool_results"] == []


def test_approved_high_risk_workflow_executes_with_validated_arguments() -> None:
    service = SkillGraphService(
        proposer=StaticProposalProposer(
            "simulate_sandbox_workflow",
            {
                "simulate_workflow": {
                    "workflow_name": "deploy.yml",
                    "ref": "feature/e2-3",
                }
            },
        )
    )
    admin = resolve_identity_from_api_key(ADMIN_API_KEY)
    paused = service.start_run(
        task="Simulate a high-risk sandbox workflow.",
        identity=admin,
    )

    state = service.approve_run(
        run_id=paused["run_id"],
        approver=admin,
        reason="Approved validated dry-run arguments.",
    )

    assert state["status"] == TaskStatus.COMPLETED
    assert state["tool_results"][0].result["workflow_name"] == "deploy.yml"
    assert state["tool_results"][0].result["ref"] == "feature/e2-3"


def test_rejected_high_risk_workflow_does_not_execute() -> None:
    service = SkillGraphService(
        proposer=StaticProposalProposer(
            "simulate_sandbox_workflow",
            {"simulate_workflow": {"workflow_name": "deploy.yml", "ref": "main"}},
        )
    )
    admin = resolve_identity_from_api_key(ADMIN_API_KEY)
    paused = service.start_run(
        task="Simulate a high-risk sandbox workflow.",
        identity=admin,
    )

    state = service.reject_run(
        run_id=paused["run_id"],
        rejector=admin,
        reason="Reject high-risk dry-run test.",
    )

    assert state["status"] == TaskStatus.REJECTED
    assert state["tool_results"] == []


def test_argument_validation_does_not_bypass_high_risk_approval() -> None:
    service = SkillGraphService(
        proposer=StaticProposalProposer(
            "simulate_sandbox_workflow",
            {
                "simulate_workflow": {
                    "workflow_name": "deploy.yml",
                    "ref": "main",
                    "approval_decision": "approved",
                }
            },
        )
    )
    admin = resolve_identity_from_api_key(ADMIN_API_KEY)

    state = service.start_run(
        task="Try to smuggle approval through arguments.",
        identity=admin,
    )

    assert state["status"] == TaskStatus.FAILED
    assert state["validation_result"].status == ProposalValidationStatus.REJECTED
    assert state.get("approval_request") is None
    assert state["policy_decisions"] == []
    assert state["tool_results"] == []
