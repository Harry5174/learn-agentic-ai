from typing import Any

from app.audit.schemas import AuditEvent, AuditEventType
from app.identity.config import ADMIN_API_KEY, VIEWER_API_KEY
from app.identity.schemas import IdentityContext
from app.identity.resolver import resolve_identity_from_api_key
from app.policy.schemas import PolicyDecisionType
from app.proposer.fake import FakeProposer, FakeProposalScenario
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
    SkillRunStatus,
    SkillSpec,
    SkillStep,
)
from app.skill_graph import graph as skill_graph_module
from app.skill_graph.graph import build_skill_execution_graph
from app.skill_graph.service import SkillGraphService
from app.state.schemas import TaskStatus
from app.tools.registry import ToolRegistry
from app.tools.schemas import RiskLevel, ToolExecutionResult, ToolSpec


def _service(scenario: FakeProposalScenario) -> SkillGraphService:
    return SkillGraphService(proposer=FakeProposer(scenario))


def _event_types(audit_trail: list[AuditEvent]) -> list[AuditEventType]:
    return [event.event_type for event in audit_trail]


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
            rationale=f"Static proposal for {identity.user_id}: {task}",
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
    run_id: str = "test-skill-run",
) -> dict[str, Any]:
    graph = build_skill_execution_graph(
        proposer=proposer,
        skill_registry=skill_registry,
        tool_registry=tool_registry,
    )

    return graph.invoke(
        {
            "run_id": run_id,
            "task": "Run a test skill.",
            "identity": identity,
            "status": TaskStatus.CREATED,
            "policy_decisions": [],
            "step_arguments": {},
            "tool_results": [],
            "audit_trail": [],
        },
        config={"configurable": {"thread_id": run_id}},
    )


def _inspect_registry_with_default(repository: str) -> SkillRegistry:
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
                    argument_specs=[
                        ToolArgumentSpec(
                            name="repository",
                            value_type=ArgumentValueType.STRING,
                            required=False,
                            default=repository,
                        )
                    ],
                    required_scopes=["tools:inspect"],
                    risk_level=RiskLevel.LOW,
                )
            ],
            required_scopes=["tools:inspect"],
            risk_level=RiskLevel.LOW,
        )
    )

    return registry


def test_valid_low_risk_proposal_executes_dry_run_tool() -> None:
    service = _service(FakeProposalScenario.VALID_LOW_RISK)
    viewer = resolve_identity_from_api_key(VIEWER_API_KEY)

    state = service.start_run(
        task="Inspect sandbox issues.",
        identity=viewer,
    )

    assert state["status"] == TaskStatus.COMPLETED
    assert state["validation_result"].status == ProposalValidationStatus.ACCEPTED
    assert state["policy_decisions"][0].decision == PolicyDecisionType.ALLOW
    assert state["tool_results"][0].tool_name == "inspect_sandbox_issues"
    assert state["tool_results"][0].dry_run is True
    assert state["final_result"].status == SkillRunStatus.COMPLETED
    assert state["final_result"].skill_id == "inspect_sandbox_health"


def test_validated_inspect_repository_affects_dry_run_result() -> None:
    service = SkillGraphService(
        proposer=StaticProposalProposer(
            "inspect_sandbox_health",
            {"inspect_issues": {"repository": "sandbox/custom-repo"}},
        )
    )
    viewer = resolve_identity_from_api_key(VIEWER_API_KEY)

    state = service.start_run(
        task="Inspect custom sandbox repository.",
        identity=viewer,
    )

    assert state["status"] == TaskStatus.COMPLETED
    assert state["tool_results"][0].result["repository"] == "sandbox/custom-repo"
    assert state["step_arguments"] == {
        "inspect_issues": {"repository": "sandbox/custom-repo"}
    }


def test_validated_draft_arguments_affect_dry_run_result() -> None:
    service = SkillGraphService(
        proposer=StaticProposalProposer(
            "draft_sandbox_issue_comment",
            {
                "draft_comment": {
                    "issue_id": 42,
                    "comment_body": "Validated draft from proposer.",
                }
            },
        )
    )
    admin = resolve_identity_from_api_key(ADMIN_API_KEY)

    state = service.start_run(
        task="Draft a sandbox issue comment.",
        identity=admin,
    )

    assert state["status"] == TaskStatus.COMPLETED
    assert state["tool_results"][0].result["issue_id"] == 42
    assert (
        state["tool_results"][0].result["comment_body"]
        == "Validated draft from proposer."
    )


def test_validated_workflow_arguments_affect_approved_dry_run_result() -> None:
    service = SkillGraphService(
        proposer=StaticProposalProposer(
            "simulate_sandbox_workflow",
            {
                "simulate_workflow": {
                    "workflow_name": "deploy.yml",
                    "ref": "feature/e2-2",
                }
            },
        )
    )
    admin = resolve_identity_from_api_key(ADMIN_API_KEY)

    paused = service.start_run(
        task="Simulate a custom workflow.",
        identity=admin,
    )

    assert paused["status"] == TaskStatus.PAUSED_FOR_APPROVAL
    assert paused["approval_request"].tool_arguments == {
        "workflow_name": "deploy.yml",
        "ref": "feature/e2-2",
    }
    assert paused["tool_results"] == []

    approved = service.approve_run(
        run_id=paused["run_id"],
        approver=admin,
        reason="Approved custom dry-run workflow.",
    )

    assert approved["status"] == TaskStatus.COMPLETED
    assert approved["tool_results"][0].result["workflow_name"] == "deploy.yml"
    assert approved["tool_results"][0].result["ref"] == "feature/e2-2"


def test_tool_registry_execute_receives_validated_arguments() -> None:
    calls: list[dict[str, Any]] = []
    viewer = resolve_identity_from_api_key(VIEWER_API_KEY)
    proposer = StaticProposalProposer(
        "inspect_sandbox_health",
        {"inspect_issues": {"repository": "sandbox/validated-repo"}},
    )

    state = _invoke_graph(
        proposer=proposer,
        identity=viewer,
        tool_registry=_recording_tool_registry(
            tool_name="inspect_sandbox_issues",
            required_scopes=["tools:inspect"],
            risk_level=RiskLevel.LOW,
            calls=calls,
        ),
    )

    assert state["status"] == TaskStatus.COMPLETED
    assert calls == [{"repository": "sandbox/validated-repo"}]


def test_raw_proposal_arguments_are_not_used_when_validated_plan_differs() -> None:
    calls: list[dict[str, Any]] = []
    viewer = resolve_identity_from_api_key(VIEWER_API_KEY)
    skill_registry = _inspect_registry_with_default("sandbox/validator-default")
    proposer = StaticProposalProposer(
        "inspect_sandbox_health",
        {"inspect_issues": {}},
        registry=skill_registry,
    )

    state = _invoke_graph(
        proposer=proposer,
        identity=viewer,
        skill_registry=skill_registry,
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


def test_missing_validated_step_fails_closed(monkeypatch) -> None:
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
            {"inspect_issues": {"repository": "sandbox/raw-repo"}},
        ),
        identity=viewer,
    )

    assert state["status"] == TaskStatus.FAILED
    assert "Validated arguments are missing" in state["error_message"]
    assert state["policy_decisions"] == []
    assert state["tool_results"] == []


def test_invalid_argument_proposal_rejects_before_execution() -> None:
    service = SkillGraphService(
        proposer=StaticProposalProposer(
            "inspect_sandbox_health",
            {"inspect_issues": {"repository": 123}},
        )
    )
    viewer = resolve_identity_from_api_key(VIEWER_API_KEY)

    state = service.start_run(
        task="Inspect invalid sandbox repository.",
        identity=viewer,
    )

    assert state["status"] == TaskStatus.FAILED
    assert state["validation_result"].status == ProposalValidationStatus.REJECTED
    assert state["validation_result"].rejection_reasons == [
        ProposalValidationReason.INVALID_ARGUMENTS
    ]
    assert state["policy_decisions"] == []
    assert state["tool_results"] == []


def test_invalid_proposal_stops_before_policy_or_tool_execution() -> None:
    service = _service(FakeProposalScenario.INVALID_PROPOSAL)
    viewer = resolve_identity_from_api_key(VIEWER_API_KEY)

    state = service.start_run(
        task="Invalid proposal.",
        identity=viewer,
    )

    assert state["status"] == TaskStatus.FAILED
    assert state["validation_result"].status == ProposalValidationStatus.REJECTED
    assert state["policy_decisions"] == []
    assert state["tool_results"] == []
    assert state["final_result"].status == SkillRunStatus.FAILED

    event_types = _event_types(state["audit_trail"])

    assert AuditEventType.TOOL_EXECUTED not in event_types
    assert AuditEventType.APPROVAL_REQUESTED not in event_types


def test_unknown_skill_rejected_validation_prevents_execution() -> None:
    service = _service(FakeProposalScenario.UNKNOWN_SKILL)
    viewer = resolve_identity_from_api_key(VIEWER_API_KEY)

    state = service.start_run(
        task="Unknown skill proposal.",
        identity=viewer,
    )

    assert state["status"] == TaskStatus.FAILED
    assert state["validation_result"].status == ProposalValidationStatus.REJECTED
    assert state["validation_result"].skill is None
    assert state["policy_decisions"] == []
    assert state["tool_results"] == []

    event_types = _event_types(state["audit_trail"])

    assert AuditEventType.TOOL_EXECUTED not in event_types


def test_high_risk_proposal_pauses_without_execution_before_approval() -> None:
    service = _service(FakeProposalScenario.VALID_HIGH_RISK)
    admin = resolve_identity_from_api_key(ADMIN_API_KEY)

    state = service.start_run(
        task="Simulate workflow.",
        identity=admin,
    )

    assert state["status"] == TaskStatus.PAUSED_FOR_APPROVAL
    assert state["validation_result"].status == ProposalValidationStatus.ACCEPTED
    assert state["validation_result"].approval_required is True
    assert state["policy_decisions"][0].decision == PolicyDecisionType.REQUIRE_APPROVAL
    assert state["approval_request"] is not None
    assert state["approval_request"].tool_name == "trigger_workflow_dry_run"
    assert state["approval_request"].tool_arguments == {
        "workflow_name": "ci.yml",
        "ref": "main",
    }
    assert state["approval_request"].risk_level == RiskLevel.HIGH
    assert state["tool_results"] == []

    event_types = _event_types(state["audit_trail"])

    assert AuditEventType.APPROVAL_REQUESTED in event_types
    assert AuditEventType.TOOL_EXECUTED not in event_types
    assert AuditEventType.TASK_COMPLETED not in event_types


def test_approved_high_risk_proposal_resumes_and_executes() -> None:
    service = _service(FakeProposalScenario.VALID_HIGH_RISK)
    admin = resolve_identity_from_api_key(ADMIN_API_KEY)

    paused = service.start_run(
        task="Simulate workflow.",
        identity=admin,
    )

    approved = service.approve_run(
        run_id=paused["run_id"],
        approver=admin,
        reason="Approved for dry-run workflow simulation.",
    )

    assert approved["status"] == TaskStatus.COMPLETED
    assert approved["tool_results"][0].tool_name == "trigger_workflow_dry_run"
    assert approved["tool_results"][0].dry_run is True
    assert approved["tool_results"][0].success is True
    assert approved["tool_results"][0].result["workflow_name"] == "ci.yml"
    assert approved["tool_results"][0].result["ref"] == "main"
    assert approved["final_result"].status == SkillRunStatus.COMPLETED

    event_types = _event_types(approved["audit_trail"])

    assert AuditEventType.APPROVAL_GRANTED in event_types
    assert AuditEventType.TOOL_EXECUTED in event_types
    assert AuditEventType.TASK_COMPLETED in event_types


def test_rejected_high_risk_approval_does_not_execute() -> None:
    service = _service(FakeProposalScenario.VALID_HIGH_RISK)
    admin = resolve_identity_from_api_key(ADMIN_API_KEY)

    paused = service.start_run(
        task="Simulate workflow.",
        identity=admin,
    )

    rejected = service.reject_run(
        run_id=paused["run_id"],
        rejector=admin,
        reason="Rejected for this dry-run review.",
    )

    assert rejected["status"] == TaskStatus.REJECTED
    assert rejected["tool_results"] == []
    assert rejected["final_result"].status == SkillRunStatus.FAILED

    event_types = _event_types(rejected["audit_trail"])

    assert AuditEventType.APPROVAL_REJECTED in event_types
    assert AuditEventType.TOOL_EXECUTED not in event_types
    assert AuditEventType.TASK_COMPLETED not in event_types


def test_audit_records_proposal_validation_policy_and_execution() -> None:
    service = _service(FakeProposalScenario.VALID_LOW_RISK)
    viewer = resolve_identity_from_api_key(VIEWER_API_KEY)

    state = service.start_run(
        task="Inspect sandbox issues.",
        identity=viewer,
    )

    audit_trail = state["audit_trail"]
    proposal_events = [
        event
        for event in audit_trail
        if event.metadata.get("kind") == "skill_proposal"
    ]
    validation_events = [
        event
        for event in audit_trail
        if event.metadata.get("kind") == "proposal_validation"
    ]
    policy_events = [
        event
        for event in audit_trail
        if event.event_type == AuditEventType.PERMISSION_CHECKED
        and event.metadata.get("decision") == PolicyDecisionType.ALLOW.value
    ]
    event_types = _event_types(audit_trail)

    assert proposal_events[0].metadata["skill_id"] == "inspect_sandbox_health"
    assert validation_events[0].metadata["status"] == "accepted"
    assert validation_events[0].metadata["approval_required"] is False
    assert validation_events[0].metadata["argument_validation_status"] == "accepted"
    assert validation_events[0].metadata["validated_argument_names"] == {
        "inspect_issues": ["repository"]
    }
    assert validation_events[0].metadata["redacted_argument_names"] == {
        "inspect_issues": []
    }
    assert validation_events[0].metadata["argument_validation_issue_codes"] == []
    assert policy_events[0].tool_name == "inspect_sandbox_issues"
    assert AuditEventType.TOOL_EXECUTED in event_types
    assert AuditEventType.TASK_COMPLETED in event_types
