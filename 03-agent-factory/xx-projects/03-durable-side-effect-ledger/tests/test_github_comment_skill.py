from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.api import skill_routes
from app.api.main import create_app
from app.github.fake_client import FakeGitHubIssueCommentClient
from app.identity.config import ADMIN_API_KEY
from app.identity.resolver import resolve_identity_from_api_key
from app.identity.schemas import IdentityContext
from app.policy.schemas import PolicyDecisionType
from app.proposer.fake import FakeProposer, FakeProposalScenario
from app.side_effects.ledger import InMemorySideEffectLedger
from app.side_effects.schemas import SideEffectStatus
from app.skills.argument_schemas import ArgumentValidationStatus
from app.skills.registry import build_default_skill_registry
from app.skills.schemas import (
    ProposalValidationReason,
    ProposalValidationStatus,
    SkillProposal,
    SkillProposalStep,
)
from app.skills.validator import ProposalValidator
from app.skill_graph.service import SkillGraphService
from app.state.schemas import TaskStatus
from app.tools.context import ToolExecutionContext
from app.tools.github_comment import (
    GITHUB_COMMENT_STEP_ID,
    GITHUB_COMMENT_TOOL_NAME,
    post_github_issue_comment,
)
from app.tools.registry import build_default_tool_registry
from app.tools.schemas import RiskLevel


def _admin() -> IdentityContext:
    return resolve_identity_from_api_key(ADMIN_API_KEY)


def _valid_arguments() -> dict[str, Any]:
    return {
        "repository": "Harry5174/learn-agentic-ai",
        "issue_number": 1,
        "comment_body": "A deterministic fake GitHub comment.",
    }


def _proposal(arguments: dict[str, Any]) -> SkillProposal:
    skill = build_default_skill_registry().get_skill(
        GITHUB_COMMENT_TOOL_NAME,
        version="1.0",
    )
    step = skill.steps[0]

    return SkillProposal(
        proposed_skill_id=skill.skill_id,
        proposed_skill_version=skill.version,
        rationale="Static GitHub comment proposal for tests.",
        steps=[
            SkillProposalStep(
                step_id=step.step_id,
                description=step.description,
                tool_name=step.tool_name,
                allowed_args_schema=step.allowed_args_schema,
                required_scopes=step.required_scopes,
                risk_level=step.risk_level,
                arguments=arguments,
            )
        ],
    )


class StaticGitHubCommentProposer:
    def __init__(self, arguments: dict[str, Any]) -> None:
        self._arguments = arguments

    def propose(self, task: str, identity: IdentityContext) -> SkillProposal:
        del task, identity
        return _proposal(self._arguments)


def _service(
    *,
    arguments: dict[str, Any] | None = None,
    client: FakeGitHubIssueCommentClient | None = None,
    ledger: InMemorySideEffectLedger | None = None,
    allowed_repositories: tuple[str, ...] | None = None,
) -> SkillGraphService:
    return SkillGraphService(
        proposer=StaticGitHubCommentProposer(arguments or _valid_arguments()),
        github_issue_comment_client=client,
        side_effect_ledger=ledger,
        allowed_github_comment_repositories=allowed_repositories,
    )


def _github_concepts(state: dict[str, Any]) -> list[str]:
    concepts: list[str] = []
    for event in state["audit_trail"]:
        concept = event.metadata.get("github_comment_audit_concept")
        if concept is not None:
            concepts.append(concept)
        concepts.extend(event.metadata.get("github_comment_audit_concepts", []))

    return concepts


def test_github_comment_skill_and_tool_are_registered_with_high_risk_metadata() -> None:
    skill_registry = build_default_skill_registry()
    tool_registry = build_default_tool_registry()

    skill = skill_registry.get_skill(GITHUB_COMMENT_TOOL_NAME, version="1.0")
    tool = tool_registry.get_tool(GITHUB_COMMENT_TOOL_NAME)

    assert skill.skill_id == GITHUB_COMMENT_TOOL_NAME
    assert skill.allowed_tool_names == [GITHUB_COMMENT_TOOL_NAME]
    assert skill.required_scopes == ["tools:post_github_comment"]
    assert skill.risk_level == RiskLevel.HIGH
    assert tool.required_scopes == ["tools:post_github_comment"]
    assert tool.risk_level == RiskLevel.HIGH
    assert [argument.name for argument in skill.steps[0].argument_specs] == [
        "repository",
        "issue_number",
        "comment_body",
    ]


def test_valid_github_comment_arguments_are_accepted_and_require_approval() -> None:
    result = ProposalValidator(build_default_skill_registry()).validate(
        proposal=_proposal(_valid_arguments()),
        identity=_admin(),
    )

    assert result.status == ProposalValidationStatus.ACCEPTED
    assert result.approval_required is True
    assert result.validated_skill_plan is not None
    assert result.validated_skill_plan.status == ArgumentValidationStatus.ACCEPTED
    assert result.validated_skill_plan.step_arguments[0].arguments == _valid_arguments()


@pytest.mark.parametrize(
    ("arguments", "issue_code"),
    [
        ({k: v for k, v in _valid_arguments().items() if k != "repository"}, "missing_required_argument"),
        ({k: v for k, v in _valid_arguments().items() if k != "issue_number"}, "missing_required_argument"),
        ({k: v for k, v in _valid_arguments().items() if k != "comment_body"}, "missing_required_argument"),
        ({**_valid_arguments(), "issue_number": "1"}, "invalid_argument_type"),
        ({**_valid_arguments(), "issue_number": True}, "invalid_argument_type"),
        ({**_valid_arguments(), "comment_body": ["nested"]}, "invalid_argument_type"),
        ({**_valid_arguments(), "repository": {"owner": "Harry5174"}}, "invalid_argument_type"),
        ({**_valid_arguments(), "extra": "not allowed"}, "unknown_argument"),
        ({**_valid_arguments(), "token": "ghp_secret"}, "forbidden_argument_name"),
        ({**_valid_arguments(), "headers": {"authorization": "secret"}}, "forbidden_argument_name"),
        ({**_valid_arguments(), "real_mode": True}, "forbidden_argument_name"),
        ({**_valid_arguments(), "identity": "demo_admin"}, "forbidden_argument_name"),
    ],
)
def test_invalid_github_comment_arguments_are_rejected(
    arguments: dict[str, Any],
    issue_code: str,
) -> None:
    result = ProposalValidator(build_default_skill_registry()).validate(
        proposal=_proposal(arguments),
        identity=_admin(),
    )

    assert result.status == ProposalValidationStatus.REJECTED
    assert ProposalValidationReason.INVALID_ARGUMENTS in result.rejection_reasons
    assert result.validated_skill_plan is not None
    assert result.validated_skill_plan.status == ArgumentValidationStatus.REJECTED
    assert issue_code in {
        issue.reason_code for issue in result.validated_skill_plan.issues
    }


def test_unallowed_repository_is_denied_before_approval_or_client_call() -> None:
    fake_client = FakeGitHubIssueCommentClient()
    state = _service(
        arguments={**_valid_arguments(), "repository": "Harry5174/not-allowed"},
        client=fake_client,
    ).start_run(
        task="Post a fake GitHub comment.",
        identity=_admin(),
    )

    assert state["status"] == TaskStatus.DENIED
    assert state.get("approval_request") is None
    assert state["tool_results"] == []
    assert fake_client.calls == []
    assert state["policy_decisions"][0].decision == PolicyDecisionType.DENY
    assert "github_comment_policy_denied" in _github_concepts(state)


def test_github_comment_pauses_for_approval_without_client_call() -> None:
    fake_client = FakeGitHubIssueCommentClient()
    state = _service(client=fake_client).start_run(
        task="Post a fake GitHub comment.",
        identity=_admin(),
    )

    assert state["status"] == TaskStatus.PAUSED_FOR_APPROVAL
    assert state["approval_request"].tool_name == GITHUB_COMMENT_TOOL_NAME
    assert state["approval_request"].tool_arguments == _valid_arguments()
    assert state["tool_results"] == []
    assert fake_client.calls == []
    assert "github_comment_approval_required" in _github_concepts(state)


def test_rejected_github_comment_run_does_not_call_fake_client() -> None:
    fake_client = FakeGitHubIssueCommentClient()
    service = _service(client=fake_client)
    paused = service.start_run(
        task="Post a fake GitHub comment.",
        identity=_admin(),
    )

    rejected = service.reject_run(
        run_id=paused["run_id"],
        rejector=_admin(),
        reason="Do not post even a fake comment.",
    )

    assert rejected["status"] == TaskStatus.REJECTED
    assert rejected["tool_results"] == []
    assert fake_client.calls == []
    assert "github_comment_approval_rejected" in _github_concepts(rejected)


def test_approved_github_comment_calls_fake_client_after_gates_and_records_ledger() -> None:
    fake_client = FakeGitHubIssueCommentClient()
    ledger = InMemorySideEffectLedger()
    service = _service(client=fake_client, ledger=ledger)
    paused = service.start_run(
        task="Post a fake GitHub comment.",
        identity=_admin(),
    )

    approved = service.approve_run(
        run_id=paused["run_id"],
        approver=_admin(),
        reason="Approved local/demo fake GitHub comment.",
    )

    result = approved["tool_results"][0]
    side_effect_id = result.result["side_effect_id"]
    record = ledger.get(side_effect_id)

    assert approved["status"] == TaskStatus.COMPLETED
    assert [call.model_dump() for call in fake_client.calls] == [_valid_arguments()]
    assert result.tool_name == GITHUB_COMMENT_TOOL_NAME
    assert result.success is True
    assert result.result["client_called"] is True
    assert result.result["ledger_miss"] is True
    assert record is not None
    assert record.status == SideEffectStatus.SUCCEEDED
    assert "github_comment_approval_granted" in _github_concepts(approved)
    assert "github_comment_side_effect_id_computed" in _github_concepts(approved)
    assert "github_comment_ledger_miss" in _github_concepts(approved)
    assert "github_comment_client_called" in _github_concepts(approved)
    assert "github_comment_executed" in _github_concepts(approved)


def test_github_comment_replay_skips_duplicate_fake_client_call_after_success() -> None:
    fake_client = FakeGitHubIssueCommentClient()
    ledger = InMemorySideEffectLedger()
    context = ToolExecutionContext(
        run_id="run-replay-1",
        step_id=GITHUB_COMMENT_STEP_ID,
        side_effect_ledger=ledger,
        github_issue_comment_client=fake_client,
    )

    first = post_github_issue_comment(_valid_arguments(), context=context)
    second = post_github_issue_comment(_valid_arguments(), context=context)
    third = post_github_issue_comment(
        {**_valid_arguments(), "comment_body": "Different fake comment."},
        context=context,
    )

    assert first.result["client_called"] is True
    assert second.result["client_called"] is False
    assert second.result["ledger_hit"] is True
    assert second.result["skipped"] is True
    assert first.result["side_effect_id"] != third.result["side_effect_id"]
    assert len(fake_client.calls) == 2


def test_fake_client_failure_is_structured_audited_and_recorded_in_ledger() -> None:
    fake_client = FakeGitHubIssueCommentClient(
        should_fail=True,
        failure_error_type="rate_limited",
        failure_message="Simulated rate limit without credentials.",
        failure_retryable=True,
    )
    ledger = InMemorySideEffectLedger()
    service = _service(client=fake_client, ledger=ledger)
    paused = service.start_run(
        task="Post a fake GitHub comment.",
        identity=_admin(),
    )

    failed = service.approve_run(
        run_id=paused["run_id"],
        approver=_admin(),
        reason="Approved local/demo fake GitHub comment.",
    )

    result = failed["tool_results"][0]
    record = ledger.get(result.result["side_effect_id"])
    safe_json = failed["final_result"].model_dump_json()

    assert failed["status"] == TaskStatus.FAILED
    assert result.success is False
    assert result.result["client_called"] is True
    assert result.result["error_type"] == "rate_limited"
    assert record is not None
    assert record.status == SideEffectStatus.FAILED
    assert record.failure is not None
    assert record.failure["error_type"] == "rate_limited"
    assert "github_comment_failed" in _github_concepts(failed)
    assert "ghp_" not in safe_json
    assert "token" not in safe_json.lower()


def test_github_comment_skill_uses_existing_http_lifecycle(monkeypatch) -> None:
    fake_client = FakeGitHubIssueCommentClient()
    monkeypatch.setattr(
        skill_routes,
        "_skill_run_service",
        SkillGraphService(
            proposer=FakeProposer(FakeProposalScenario.VALID_GITHUB_COMMENT),
            github_issue_comment_client=fake_client,
            side_effect_ledger=InMemorySideEffectLedger(),
        ),
    )
    client = TestClient(create_app())

    create_response = client.post(
        "/skill-runs",
        headers={"X-API-Key": ADMIN_API_KEY},
        json={"task": "Post a local/demo fake GitHub issue comment."},
    )
    assert create_response.status_code == 202

    create_body = create_response.json()
    run_id = create_body["run_id"]

    assert create_body["status"] == "paused_for_approval"
    assert create_body["selected_skill_id"] == GITHUB_COMMENT_TOOL_NAME
    assert create_body["approval_required"] is True
    assert create_body["execution"]["attempted_step_count"] == 0
    assert fake_client.calls == []

    approve_response = client.post(
        f"/skill-runs/{run_id}/approve",
        headers={"X-API-Key": ADMIN_API_KEY},
        json={"reason": "Approved local/demo fake GitHub comment."},
    )
    assert approve_response.status_code == 200

    approve_body = approve_response.json()
    assert approve_body["status"] == "completed"
    assert approve_body["approval_status"] == "approved"
    assert approve_body["execution"] == {
        "attempted_step_count": 1,
        "completed_step_count": 1,
        "tool_names": [GITHUB_COMMENT_TOOL_NAME],
        "dry_run": True,
    }
    assert len(fake_client.calls) == 1
