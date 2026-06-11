from app.audit.schemas import AuditEvent, AuditEventType
from app.identity.config import ADMIN_API_KEY, VIEWER_API_KEY
from app.identity.resolver import resolve_identity_from_api_key
from app.policy.schemas import PolicyDecisionType
from app.proposer.fake import FakeProposer, FakeProposalScenario
from app.skills.schemas import ProposalValidationStatus, SkillRunStatus
from app.skill_graph.service import SkillGraphService
from app.state.schemas import TaskStatus
from app.tools.schemas import RiskLevel


def _service(scenario: FakeProposalScenario) -> SkillGraphService:
    return SkillGraphService(proposer=FakeProposer(scenario))


def _event_types(audit_trail: list[AuditEvent]) -> list[AuditEventType]:
    return [event.event_type for event in audit_trail]


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
    assert policy_events[0].tool_name == "inspect_sandbox_issues"
    assert AuditEventType.TOOL_EXECUTED in event_types
    assert AuditEventType.TASK_COMPLETED in event_types
