import json
import os
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.api import skill_routes
from app.api.main import create_app
from app.approval.schemas import ApprovalDecision
from app.github.fake_client import FakeGitHubIssueCommentClient
from app.identity.config import ADMIN_API_KEY, VIEWER_API_KEY
from app.identity.resolver import resolve_identity_from_api_key
from app.identity.schemas import IdentityContext
from app.policy.schemas import PolicyDecisionType
from app.side_effects.idempotency import (
    build_side_effect_id,
    validated_arguments_hash,
)
from app.side_effects.ledger import InMemorySideEffectLedger
from app.side_effects.schemas import SideEffectStatus
from app.skill_graph.service import SkillGraphService, SkillRunNotPausedError
from app.skills.argument_schemas import ArgumentValidationStatus
from app.skills.registry import build_default_skill_registry
from app.skills.schemas import (
    ProposalValidationReason,
    ProposalValidationStatus,
    SkillProposal,
    SkillProposalStep,
)
from app.state.schemas import TaskStatus
from app.tools.context import ToolExecutionContext
from app.tools.github_comment import (
    GITHUB_COMMENT_STEP_ID,
    GITHUB_COMMENT_TOOL_NAME,
    post_github_issue_comment,
)


def _admin() -> IdentityContext:
    return resolve_identity_from_api_key(ADMIN_API_KEY)


def _viewer() -> IdentityContext:
    return resolve_identity_from_api_key(VIEWER_API_KEY)


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
        rationale="A3.4 adversarial GitHub comment proposal.",
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


class MutableGitHubCommentProposer:
    def __init__(self, arguments: dict[str, Any]) -> None:
        self.arguments = arguments

    def propose(self, task: str, identity: IdentityContext) -> SkillProposal:
        del task, identity
        return _proposal(self.arguments)


def _service(
    *,
    proposer: MutableGitHubCommentProposer | None = None,
    arguments: dict[str, Any] | None = None,
    client: FakeGitHubIssueCommentClient | None = None,
    ledger: InMemorySideEffectLedger | None = None,
    allowed_repositories: tuple[str, ...] | None = None,
) -> SkillGraphService:
    return SkillGraphService(
        proposer=proposer or MutableGitHubCommentProposer(arguments or _valid_arguments()),
        github_issue_comment_client=client,
        side_effect_ledger=ledger,
        allowed_github_comment_repositories=allowed_repositories,
    )


def _issue_codes(state: dict[str, Any]) -> list[str]:
    validation_result = state["validation_result"]
    assert validation_result.validated_skill_plan is not None

    return [
        issue.reason_code for issue in validation_result.validated_skill_plan.issues
    ]


def _audit_json(state: dict[str, Any]) -> str:
    return json.dumps(
        [event.model_dump(mode="json") for event in state["audit_trail"]],
        sort_keys=True,
    )


def _github_concepts(state: dict[str, Any]) -> list[str]:
    concepts: list[str] = []
    for event in state["audit_trail"]:
        concept = event.metadata.get("github_comment_audit_concept")
        if concept is not None:
            concepts.append(concept)
        concepts.extend(event.metadata.get("github_comment_audit_concepts", []))

    return concepts


def _assert_rejected_before_execution(
    state: dict[str, Any],
    fake_client: FakeGitHubIssueCommentClient,
    expected_issue_code: str,
) -> None:
    assert state["status"] == TaskStatus.FAILED
    assert state["validation_result"].status == ProposalValidationStatus.REJECTED
    assert state["validation_result"].rejection_reasons == [
        ProposalValidationReason.INVALID_ARGUMENTS
    ]
    assert state["validation_result"].validated_skill_plan.status == (
        ArgumentValidationStatus.REJECTED
    )
    assert expected_issue_code in _issue_codes(state)
    assert state.get("approval_request") is None
    assert state["policy_decisions"] == []
    assert state["tool_results"] == []
    assert fake_client.calls == []


@pytest.mark.parametrize(
    "argument_name",
    [
        "token",
        "github_token",
        "authorization",
        "headers",
        "api_base_url",
        "client_config",
        "transport",
        "real_mode",
        "dry_run",
        "approved",
        "approval_decision",
        "approval_authority",
        "policy_override",
        "risk_override",
        "requires_approval",
        "role",
        "scope",
        "scopes",
        "identity",
        "tool_name",
        "skill_id",
        "skill_version",
    ],
)
def test_github_comment_argument_smuggling_is_rejected_before_execution(
    argument_name: str,
) -> None:
    raw_secret = f"RAW_SECRET_FOR_{argument_name.upper()}"
    fake_client = FakeGitHubIssueCommentClient()
    state = _service(
        arguments={**_valid_arguments(), argument_name: raw_secret},
        client=fake_client,
    ).start_run(
        task="Try to smuggle control-plane data into a GitHub comment.",
        identity=_admin(),
    )

    _assert_rejected_before_execution(
        state=state,
        fake_client=fake_client,
        expected_issue_code="forbidden_argument_name",
    )
    assert raw_secret not in _audit_json(state)
    assert "github_comment_validation_failed" in _github_concepts(state)


@pytest.mark.parametrize(
    ("field_name", "field_value"),
    [
        ("repository", {"owner": "Harry5174", "name": "learn-agentic-ai"}),
        ("repository", ["Harry5174/learn-agentic-ai"]),
        ("issue_number", {"number": 1}),
        ("issue_number", [1]),
        ("comment_body", {"text": "nested comment"}),
        ("comment_body", ["nested comment"]),
        ("comment_body", {"blocks": [{"text": "nested comment"}]}),
    ],
)
def test_github_comment_unsupported_payloads_are_rejected_without_partial_acceptance(
    field_name: str,
    field_value: object,
) -> None:
    fake_client = FakeGitHubIssueCommentClient()
    state = _service(
        arguments={**_valid_arguments(), field_name: field_value},
        client=fake_client,
    ).start_run(
        task="Try unsupported GitHub comment payload shapes.",
        identity=_admin(),
    )

    _assert_rejected_before_execution(
        state=state,
        fake_client=fake_client,
        expected_issue_code="invalid_argument_type",
    )
    assert state["validation_result"].validated_skill_plan.step_arguments == []


def test_github_comment_arbitrary_json_blob_is_rejected_as_unknown_argument() -> None:
    fake_client = FakeGitHubIssueCommentClient()
    state = _service(
        arguments={
            **_valid_arguments(),
            "payload": {"repository": "Harry5174/learn-agentic-ai"},
        },
        client=fake_client,
    ).start_run(
        task="Try an arbitrary JSON blob instead of declared scalar arguments.",
        identity=_admin(),
    )

    _assert_rejected_before_execution(
        state=state,
        fake_client=fake_client,
        expected_issue_code="unknown_argument",
    )


@pytest.mark.parametrize(
    "repository",
    [
        "Harry5174/not-allowed",
        "harry5174/learn-agentic-ai",
        "Harry5174/learn-agentic-ai ",
        "https://github.com/Harry5174/learn-agentic-ai",
        "Harry5174/learn-agentic-ai/../other",
    ],
)
def test_github_comment_repository_policy_bypass_attempts_are_denied(
    repository: str,
) -> None:
    fake_client = FakeGitHubIssueCommentClient()
    state = _service(
        arguments={**_valid_arguments(), "repository": repository},
        client=fake_client,
    ).start_run(
        task="Try to bypass the trusted repository allowlist.",
        identity=_admin(),
    )

    assert state["status"] == TaskStatus.DENIED
    assert state["validation_result"].status == ProposalValidationStatus.ACCEPTED
    assert state["policy_decisions"][0].decision == PolicyDecisionType.DENY
    assert state.get("approval_request") is None
    assert state["tool_results"] == []
    assert fake_client.calls == []
    assert "github_comment_policy_denied" in _github_concepts(state)


@pytest.mark.parametrize(
    "argument_name",
    ["policy_override", "approval_decision", "requires_approval"],
)
def test_model_proposed_policy_or_approval_overrides_do_not_reach_policy(
    argument_name: str,
) -> None:
    fake_client = FakeGitHubIssueCommentClient()
    state = _service(
        arguments={**_valid_arguments(), argument_name: "attacker-controlled"},
        client=fake_client,
    ).start_run(
        task="Try to override policy or approval through model arguments.",
        identity=_admin(),
    )

    _assert_rejected_before_execution(
        state=state,
        fake_client=fake_client,
        expected_issue_code="forbidden_argument_name",
    )
    assert "github_comment_policy_allowed" not in _github_concepts(state)


def test_high_risk_github_comment_pauses_before_any_fake_client_call() -> None:
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


def test_rejected_github_comment_approval_never_calls_fake_client() -> None:
    fake_client = FakeGitHubIssueCommentClient()
    service = _service(client=fake_client)
    paused = service.start_run(
        task="Post a fake GitHub comment.",
        identity=_admin(),
    )

    rejected = service.reject_run(
        run_id=paused["run_id"],
        rejector=_admin(),
        reason="Reject the local/demo comment.",
    )

    assert rejected["status"] == TaskStatus.REJECTED
    assert rejected["tool_results"] == []
    assert fake_client.calls == []
    assert "github_comment_approval_rejected" in _github_concepts(rejected)


def test_invalid_approval_actor_cannot_execute_github_comment() -> None:
    fake_client = FakeGitHubIssueCommentClient()
    service = _service(client=fake_client)
    paused = service.start_run(
        task="Post a fake GitHub comment.",
        identity=_admin(),
    )

    failed = service.approve_run(
        run_id=paused["run_id"],
        approver=_viewer(),
        reason="Viewer attempts to approve.",
    )

    assert failed["status"] == TaskStatus.FAILED
    assert "approval:approve" in failed["error_message"]
    assert failed["tool_results"] == []
    assert fake_client.calls == []


def test_public_github_comment_approval_route_rejects_smuggled_decision_fields(
    monkeypatch,
) -> None:
    fake_client = FakeGitHubIssueCommentClient()
    monkeypatch.setattr(
        skill_routes,
        "_skill_run_service",
        _service(client=fake_client),
    )
    client = TestClient(create_app())

    create_response = client.post(
        "/skill-runs",
        headers={"X-API-Key": ADMIN_API_KEY},
        json={"task": "Post a local/demo fake GitHub issue comment."},
    )
    assert create_response.status_code == 202
    run_id = create_response.json()["run_id"]

    approve_response = client.post(
        f"/skill-runs/{run_id}/approve",
        headers={"X-API-Key": ADMIN_API_KEY},
        json={
            "reason": "Approved.",
            "approval_decision": "approved by request body",
        },
    )

    assert approve_response.status_code == 422
    assert fake_client.calls == []


def test_public_github_comment_argument_failure_does_not_echo_raw_secret(
    monkeypatch,
) -> None:
    raw_secret = "RAW_GITHUB_TOKEN_SHOULD_NOT_LEAK_A34"
    service = _service(
        arguments={**_valid_arguments(), "github_token": raw_secret},
        client=FakeGitHubIssueCommentClient(),
    )
    monkeypatch.setattr(skill_routes, "_skill_run_service", service)
    client = TestClient(create_app())

    response = client.post(
        "/skill-runs",
        headers={"X-API-Key": ADMIN_API_KEY},
        json={"task": "Try to smuggle a token into GitHub comment arguments."},
    )

    assert response.status_code == 202
    assert raw_secret not in response.text
    body = response.json()
    assert body["status"] == "failed"
    assert body["validation"]["argument_validation_issue_codes"] == [
        "forbidden_argument_name"
    ]

    audit_response = client.get(f"/skill-runs/{body['run_id']}/audit")

    assert audit_response.status_code == 200
    assert raw_secret not in audit_response.text


def test_approval_resumes_checkpointed_validated_github_comment_arguments() -> None:
    original_arguments = _valid_arguments()
    proposer = MutableGitHubCommentProposer(original_arguments)
    fake_client = FakeGitHubIssueCommentClient()
    service = _service(proposer=proposer, client=fake_client)
    paused = service.start_run(
        task="Post a fake GitHub comment.",
        identity=_admin(),
    )

    proposer.arguments.update(
        {
            "repository": "Harry5174/not-allowed-after-pause",
            "issue_number": 999,
            "comment_body": "MUTATED AFTER APPROVAL REQUEST",
        }
    )
    approved = service.approve_run(
        run_id=paused["run_id"],
        approver=_admin(),
        reason="Approve checkpointed validated arguments.",
    )

    result = approved["tool_results"][0]
    expected_hash = validated_arguments_hash(_valid_arguments())
    expected_side_effect_id = build_side_effect_id(
        skill_run_id=paused["run_id"],
        step_id=GITHUB_COMMENT_STEP_ID,
        tool_name=GITHUB_COMMENT_TOOL_NAME,
        validated_arguments_hash=expected_hash,
    )

    assert approved["status"] == TaskStatus.COMPLETED
    assert [call.model_dump() for call in fake_client.calls] == [_valid_arguments()]
    assert result.result["validated_arguments_hash"] == expected_hash
    assert result.result["side_effect_id"] == expected_side_effect_id


def test_current_approval_decision_schema_does_not_persist_hash_or_side_effect_id() -> None:
    decision = ApprovalDecision(
        task_id="run-123",
        tool_name=GITHUB_COMMENT_TOOL_NAME,
        status="approved",
        decided_by="demo_admin",
        decider_role="admin",
        reason="A3.4 limitation check.",
    )

    decision_payload = decision.model_dump(mode="json")

    assert "validated_arguments_hash" not in decision_payload
    assert "side_effect_id" not in decision_payload


def test_duplicate_approval_after_completion_does_not_duplicate_fake_comment() -> None:
    fake_client = FakeGitHubIssueCommentClient()
    service = _service(client=fake_client)
    paused = service.start_run(
        task="Post a fake GitHub comment.",
        identity=_admin(),
    )

    completed = service.approve_run(
        run_id=paused["run_id"],
        approver=_admin(),
        reason="Approve once.",
    )

    with pytest.raises(SkillRunNotPausedError):
        service.approve_run(
            run_id=paused["run_id"],
            approver=_admin(),
            reason="Attempt duplicate approval.",
        )

    assert completed["status"] == TaskStatus.COMPLETED
    assert len(fake_client.calls) == 1


def test_ledger_success_hit_skips_fake_client_and_is_audited() -> None:
    fake_client = FakeGitHubIssueCommentClient()
    ledger = InMemorySideEffectLedger()
    service = _service(client=fake_client, ledger=ledger)
    paused = service.start_run(
        task="Post a fake GitHub comment.",
        identity=_admin(),
    )
    argument_hash = validated_arguments_hash(_valid_arguments())
    side_effect_id = build_side_effect_id(
        skill_run_id=paused["run_id"],
        step_id=GITHUB_COMMENT_STEP_ID,
        tool_name=GITHUB_COMMENT_TOOL_NAME,
        validated_arguments_hash=argument_hash,
    )
    ledger.record_started(
        side_effect_id=side_effect_id,
        skill_run_id=paused["run_id"],
        step_id=GITHUB_COMMENT_STEP_ID,
        tool_name=GITHUB_COMMENT_TOOL_NAME,
        validated_arguments_hash=argument_hash,
    )
    ledger.record_succeeded(
        side_effect_id,
        external_result={"comment_id": "preexisting-comment"},
    )

    approved = service.approve_run(
        run_id=paused["run_id"],
        approver=_admin(),
        reason="Approve already-recorded local/demo side effect.",
    )

    result = approved["tool_results"][0]

    assert approved["status"] == TaskStatus.COMPLETED
    assert fake_client.calls == []
    assert result.success is True
    assert result.result["ledger_hit"] is True
    assert result.result["client_called"] is False
    assert result.result["skipped"] is True
    assert "github_comment_ledger_hit" in _github_concepts(approved)
    assert "github_comment_client_not_called" in _github_concepts(approved)
    assert "github_comment_skipped" in _github_concepts(approved)


def test_replay_and_argument_mutation_change_side_effect_identity() -> None:
    fake_client = FakeGitHubIssueCommentClient()
    ledger = InMemorySideEffectLedger()
    context = ToolExecutionContext(
        run_id="a3-4-replay-run",
        step_id=GITHUB_COMMENT_STEP_ID,
        side_effect_ledger=ledger,
        github_issue_comment_client=fake_client,
    )

    first = post_github_issue_comment(_valid_arguments(), context=context)
    second = post_github_issue_comment(_valid_arguments(), context=context)
    changed_body = post_github_issue_comment(
        {**_valid_arguments(), "comment_body": "Different body."},
        context=context,
    )
    changed_issue = post_github_issue_comment(
        {**_valid_arguments(), "issue_number": 2},
        context=context,
    )

    assert first.result["client_called"] is True
    assert second.result["client_called"] is False
    assert second.result["ledger_hit"] is True
    assert second.result["skipped"] is True
    assert changed_body.result["side_effect_id"] != first.result["side_effect_id"]
    assert changed_issue.result["side_effect_id"] != first.result["side_effect_id"]
    assert len(fake_client.calls) == 3


def test_fake_client_failure_is_structured_recorded_audited_and_not_success() -> None:
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
        reason="Approve local/demo failure simulation.",
    )

    result = failed["tool_results"][0]
    record = ledger.get(result.result["side_effect_id"])
    result_json = failed["final_result"].model_dump_json()

    assert failed["status"] == TaskStatus.FAILED
    assert result.success is False
    assert result.result["client_called"] is True
    assert result.result["error_type"] == "rate_limited"
    assert record is not None
    assert record.status == SideEffectStatus.FAILED
    assert record.failure is not None
    assert record.failure["error_type"] == "rate_limited"
    assert "github_comment_failed" in _github_concepts(failed)
    assert len(fake_client.calls) == 1
    assert "ghp_" not in result_json
    assert "token" not in result_json.lower()


def test_fake_client_does_not_read_environment_tokens(monkeypatch) -> None:
    monkeypatch.setenv("GITHUB_TOKEN", "ghp_should_not_be_read_a34")
    fake_client = FakeGitHubIssueCommentClient()
    context = ToolExecutionContext(
        run_id="a3-4-token-run",
        step_id=GITHUB_COMMENT_STEP_ID,
        side_effect_ledger=InMemorySideEffectLedger(),
        github_issue_comment_client=fake_client,
    )

    result = post_github_issue_comment(_valid_arguments(), context=context)

    assert result.success is True
    assert result.dry_run is True
    assert result.result["mode"] == "fake_client"
    assert os.environ["GITHUB_TOKEN"] == "ghp_should_not_be_read_a34"


def test_runtime_github_comment_path_has_no_network_or_token_loading_code() -> None:
    runtime_files = [
        Path("src/app/tools/github_comment.py"),
        Path("src/app/github/client.py"),
        Path("src/app/github/fake_client.py"),
        Path("src/app/github/schemas.py"),
    ]
    combined_source = "\n".join(path.read_text() for path in runtime_files)

    forbidden_network_terms = [
        "requests.",
        "httpx.",
        "urllib.request",
        "PyGithub",
        "Github(",
    ]
    forbidden_token_loading_terms = [
        "GITHUB_TOKEN",
        "GH_TOKEN",
        "Authorization",
        "Bearer",
        "os.environ",
        "os.getenv",
    ]

    assert not any(term in combined_source for term in forbidden_network_terms)
    assert not any(term in combined_source for term in forbidden_token_loading_terms)


def test_audit_concepts_cover_github_comment_safety_lifecycle() -> None:
    invalid_client = FakeGitHubIssueCommentClient()
    invalid_state = _service(
        arguments={**_valid_arguments(), "token": "RAW_SHOULD_NOT_LEAK"},
        client=invalid_client,
    ).start_run(
        task="Invalid GitHub comment proposal.",
        identity=_admin(),
    )
    denied_state = _service(
        arguments={**_valid_arguments(), "repository": "Harry5174/not-allowed"},
        client=FakeGitHubIssueCommentClient(),
    ).start_run(
        task="Denied GitHub comment proposal.",
        identity=_admin(),
    )

    approved_client = FakeGitHubIssueCommentClient()
    approved_service = _service(client=approved_client)
    paused = approved_service.start_run(
        task="Approved GitHub comment proposal.",
        identity=_admin(),
    )
    approved_state = approved_service.approve_run(
        run_id=paused["run_id"],
        approver=_admin(),
        reason="Approve for audit coverage.",
    )

    rejected_service = _service(client=FakeGitHubIssueCommentClient())
    rejected_paused = rejected_service.start_run(
        task="Rejected GitHub comment proposal.",
        identity=_admin(),
    )
    rejected_state = rejected_service.reject_run(
        run_id=rejected_paused["run_id"],
        rejector=_admin(),
        reason="Reject for audit coverage.",
    )

    failing_service = _service(
        client=FakeGitHubIssueCommentClient(should_fail=True),
        ledger=InMemorySideEffectLedger(),
    )
    failing_paused = failing_service.start_run(
        task="Failing GitHub comment proposal.",
        identity=_admin(),
    )
    failed_state = failing_service.approve_run(
        run_id=failing_paused["run_id"],
        approver=_admin(),
        reason="Approve failure for audit coverage.",
    )

    combined_concepts = (
        _github_concepts(invalid_state)
        + _github_concepts(denied_state)
        + _github_concepts(paused)
        + _github_concepts(approved_state)
        + _github_concepts(rejected_state)
        + _github_concepts(failed_state)
    )

    expected_concepts = {
        "github_comment_validation_failed",
        "github_comment_policy_denied",
        "github_comment_approval_required",
        "github_comment_approval_granted",
        "github_comment_approval_rejected",
        "github_comment_side_effect_id_computed",
        "github_comment_ledger_miss",
        "github_comment_client_called",
        "github_comment_executed",
        "github_comment_failed",
    }

    assert expected_concepts.issubset(set(combined_concepts))
    assert invalid_client.calls == []
