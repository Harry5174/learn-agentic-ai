import pytest
from fastapi.testclient import TestClient

from app.api import skill_routes
from app.api.main import create_app
from app.identity.config import ADMIN_API_KEY, VIEWER_API_KEY
from app.identity.schemas import IdentityContext
from app.proposer.fake import FakeProposer, FakeProposalScenario
from app.skills.registry import build_default_skill_registry
from app.skills.schemas import SkillProposal, SkillProposalStep
from app.skill_graph.service import SkillGraphService


def _high_risk_service() -> SkillGraphService:
    return SkillGraphService(
        proposer=FakeProposer(FakeProposalScenario.VALID_HIGH_RISK)
    )


class StaticArgumentProposer:
    def __init__(
        self,
        skill_id: str,
        arguments_by_step_id: dict[str, dict[str, object]],
    ) -> None:
        self._skill_id = skill_id
        self._arguments_by_step_id = arguments_by_step_id

    def propose(self, task: str, identity: IdentityContext) -> SkillProposal:
        skill = build_default_skill_registry().get_skill(
            self._skill_id,
            version="1.0",
        )

        return SkillProposal(
            proposed_skill_id=skill.skill_id,
            proposed_skill_version=skill.version,
            rationale=f"Static argument proposal for {identity.user_id}: {task}",
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


def test_get_skills_returns_safe_registered_skill_summaries() -> None:
    client = TestClient(create_app())

    response = client.get("/skills")

    assert response.status_code == 200

    skills = response.json()
    skill_ids = {skill["skill_id"] for skill in skills}

    assert skill_ids == {
        "inspect_sandbox_health",
        "draft_sandbox_issue_comment",
        "simulate_sandbox_workflow",
        "post_github_issue_comment",
    }

    inspect_skill = next(
        skill for skill in skills if skill["skill_id"] == "inspect_sandbox_health"
    )
    assert inspect_skill["version"] == "1.0"
    assert inspect_skill["name"] == "Inspect sandbox health"
    assert inspect_skill["risk_level"] == "low"
    assert inspect_skill["required_scopes"] == ["tools:inspect"]
    assert inspect_skill["steps"][0] == {
        "step_id": "inspect_issues",
        "description": "Inspect sandbox issues using dry-run data.",
        "tool_name": "inspect_sandbox_issues",
        "risk_level": "low",
        "required_scopes": ["tools:inspect"],
    }


def test_get_skills_does_not_expose_unsafe_internals() -> None:
    client = TestClient(create_app())

    response = client.get("/skills")

    assert response.status_code == 200

    unsafe_fields = {
        "allowed_args_schema",
        "input_schema",
        "output_schema",
        "tags",
        "allowed_tool_names",
        "function",
        "callable",
        "handler",
        "registry",
        "graph",
        "checkpointer",
    }

    for skill in response.json():
        assert unsafe_fields.isdisjoint(skill)

        for step in skill["steps"]:
            assert unsafe_fields.isdisjoint(step)


def test_post_skill_runs_starts_low_risk_run_through_http() -> None:
    client = TestClient(create_app())

    response = client.post(
        "/skill-runs",
        headers={"X-API-Key": VIEWER_API_KEY},
        json={"task": "Inspect sandbox health.", "proposer_mode": "fake"},
    )

    assert response.status_code == 202

    body = response.json()
    assert body["run_id"]
    assert body["status"] == "completed"
    assert body["task"] == "Inspect sandbox health."
    assert body["proposer_mode"] == "fake"
    assert body["selected_skill_id"] == "inspect_sandbox_health"
    assert body["selected_skill_version"] == "1.0"
    assert body["validation_status"] == "accepted"
    assert body["approval_required"] is False
    assert body["approval_status"] == "not_required"
    assert body["risk_level"] == "low"
    assert body["final_report"] == "Skill run completed successfully."
    assert body["error_message"] is None
    assert body["proposal"]["proposed_skill_id"] == "inspect_sandbox_health"
    assert body["validation"]["status"] == "accepted"
    assert body["validation"]["rejection_reasons"] == []
    assert body["validation"]["argument_validation_status"] == "accepted"
    assert body["validation"]["validated_argument_names"] == {
        "inspect_issues": ["repository"]
    }
    assert body["validation"]["redacted_argument_names"] == {"inspect_issues": []}
    assert body["validation"]["argument_validation_issue_codes"] == []
    assert body["execution"] == {
        "attempted_step_count": 1,
        "completed_step_count": 1,
        "tool_names": ["inspect_sandbox_issues"],
        "dry_run": True,
    }


def test_post_skill_runs_requested_github_comment_creates_pending_approval(
    monkeypatch,
) -> None:
    monkeypatch.setattr(skill_routes, "_skill_run_service", SkillGraphService())
    client = TestClient(create_app())

    response = client.post(
        "/skill-runs",
        headers={"X-API-Key": ADMIN_API_KEY},
        json={
            "task": (
                "Create a local demo approval request for posting a safe "
                "GitHub issue comment."
            ),
            "proposer_mode": "fake",
            "requested_skill_id": "post_github_issue_comment",
        },
    )

    assert response.status_code == 202

    body = response.json()
    assert body["status"] == "paused_for_approval"
    assert body["selected_skill_id"] == "post_github_issue_comment"
    assert body["risk_level"] == "high"
    assert body["approval_required"] is True
    assert body["approval_status"] == "pending"
    assert body["proposal"]["proposed_tool_names"] == ["post_github_issue_comment"]
    assert body["execution"] == {
        "attempted_step_count": 0,
        "completed_step_count": 0,
        "tool_names": [],
        "dry_run": True,
    }


def test_post_skill_runs_unknown_requested_skill_fails_closed(
    monkeypatch,
) -> None:
    monkeypatch.setattr(skill_routes, "_skill_run_service", SkillGraphService())
    client = TestClient(create_app())

    response = client.post(
        "/skill-runs",
        headers={"X-API-Key": ADMIN_API_KEY},
        json={
            "task": "Try to force an unknown skill.",
            "proposer_mode": "fake",
            "requested_skill_id": "not_a_registered_demo_skill",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Unsupported requested_skill_id for fake demo mode: "
        "not_a_registered_demo_skill"
    )
    assert "inspect_sandbox_health" not in response.text


def test_post_skill_runs_without_requested_skill_preserves_low_risk_default(
    monkeypatch,
) -> None:
    monkeypatch.setattr(skill_routes, "_skill_run_service", SkillGraphService())
    client = TestClient(create_app())

    response = client.post(
        "/skill-runs",
        headers={"X-API-Key": VIEWER_API_KEY},
        json={"task": "Inspect sandbox health.", "proposer_mode": "fake"},
    )

    assert response.status_code == 202

    body = response.json()
    assert body["status"] == "completed"
    assert body["selected_skill_id"] == "inspect_sandbox_health"
    assert body["risk_level"] == "low"
    assert body["approval_required"] is False
    assert body["approval_status"] == "not_required"


def test_post_skill_runs_uses_server_derived_identity() -> None:
    client = TestClient(create_app())

    response = client.post(
        "/skill-runs",
        headers={"X-API-Key": VIEWER_API_KEY},
        json={"task": "Inspect sandbox health."},
    )

    assert response.status_code == 202

    body = response.json()
    assert "demo_viewer" in body["proposal"]["rationale"]
    assert "fake_admin" not in body["proposal"]["rationale"]


@pytest.mark.parametrize("field", ["user_id", "role", "scopes", "identity"])
def test_post_skill_runs_rejects_body_identity_fields(field: str) -> None:
    client = TestClient(create_app())

    response = client.post(
        "/skill-runs",
        headers={"X-API-Key": VIEWER_API_KEY},
        json={
            "task": "Inspect sandbox health.",
            field: "attacker-controlled",
        },
    )

    assert response.status_code == 422


@pytest.mark.parametrize(
    "field",
    [
        "policy_decision",
        "policy_override",
        "risk_override",
        "approval_decision",
        "approval_authority",
        "trusted_tool_names",
    ],
)
def test_post_skill_runs_rejects_policy_risk_and_approval_overrides(
    field: str,
) -> None:
    client = TestClient(create_app())

    response = client.post(
        "/skill-runs",
        headers={"X-API-Key": VIEWER_API_KEY},
        json={
            "task": "Inspect sandbox health.",
            field: "attacker-controlled",
        },
    )

    assert response.status_code == 422


def test_invalid_proposal_is_rejected_before_execution_through_http(
    monkeypatch,
) -> None:
    invalid_service = SkillGraphService(
        proposer=FakeProposer(FakeProposalScenario.INVALID_PROPOSAL)
    )
    monkeypatch.setattr(skill_routes, "_skill_run_service", invalid_service)
    client = TestClient(create_app())

    response = client.post(
        "/skill-runs",
        headers={"X-API-Key": VIEWER_API_KEY},
        json={"task": "Invalid proposal."},
    )

    assert response.status_code == 202

    body = response.json()
    assert body["status"] == "failed"
    assert body["validation_status"] == "rejected"
    assert body["validation"]["status"] == "rejected"
    assert body["validation"]["rejection_reasons"] == ["tool_not_allowed"]
    assert body["validation"]["argument_validation_status"] is None
    assert body["validation"]["validated_argument_names"] == {}
    assert body["validation"]["redacted_argument_names"] == {}
    assert body["validation"]["argument_validation_issue_codes"] == []
    assert body["final_report"] == "Proposal validation rejected."
    assert body["execution"] == {
        "attempted_step_count": 0,
        "completed_step_count": 0,
        "tool_names": [],
        "dry_run": True,
    }


def test_llm_proposer_mode_does_not_call_live_model_or_service(monkeypatch) -> None:
    class ExplodingService:
        def start_run(self, task, identity):
            raise AssertionError("Service should not run for disabled llm mode.")

    monkeypatch.setattr(skill_routes, "_skill_run_service", ExplodingService())
    client = TestClient(create_app())

    response = client.post(
        "/skill-runs",
        headers={"X-API-Key": VIEWER_API_KEY},
        json={"task": "Inspect sandbox health.", "proposer_mode": "llm"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "LLM proposer mode is not enabled for this API."


def test_get_skill_run_returns_safe_run_summary() -> None:
    client = TestClient(create_app())

    create_response = client.post(
        "/skill-runs",
        headers={"X-API-Key": VIEWER_API_KEY},
        json={"task": "Inspect sandbox health."},
    )

    run_id = create_response.json()["run_id"]

    response = client.get(f"/skill-runs/{run_id}")

    assert response.status_code == 200

    body = response.json()
    assert body["run_id"] == run_id
    assert body["status"] == "completed"
    assert body["proposer_mode"] == "fake"
    assert body["selected_skill_id"] == "inspect_sandbox_health"
    assert body["validation_status"] == "accepted"
    assert body["approval_required"] is False
    assert body["execution"]["tool_names"] == ["inspect_sandbox_issues"]

    unsafe_fields = {
        "identity",
        "approval_actor",
        "checkpoint",
        "checkpointer",
        "graph",
        "step_arguments",
    }
    assert unsafe_fields.isdisjoint(body)


def test_get_skill_run_unknown_run_returns_safe_404() -> None:
    client = TestClient(create_app())

    response = client.get("/skill-runs/not-a-run")

    assert response.status_code == 404
    assert response.json()["detail"] == "Skill run not found."


def test_high_risk_skill_run_is_observable_in_approval_required_state(
    monkeypatch,
) -> None:
    monkeypatch.setattr(skill_routes, "_skill_run_service", _high_risk_service())
    client = TestClient(create_app())

    create_response = client.post(
        "/skill-runs",
        headers={"X-API-Key": ADMIN_API_KEY},
        json={"task": "Simulate sandbox workflow."},
    )

    assert create_response.status_code == 202

    run_id = create_response.json()["run_id"]
    response = client.get(f"/skill-runs/{run_id}")

    assert response.status_code == 200

    body = response.json()
    assert body["status"] == "paused_for_approval"
    assert body["approval_required"] is True
    assert body["approval_status"] == "pending"
    assert body["risk_level"] == "high"
    assert body["selected_skill_id"] == "simulate_sandbox_workflow"
    assert body["execution"] == {
        "attempted_step_count": 0,
        "completed_step_count": 0,
        "tool_names": [],
        "dry_run": True,
    }


def test_approve_skill_run_resumes_and_executes_dry_run_tool(monkeypatch) -> None:
    monkeypatch.setattr(skill_routes, "_skill_run_service", _high_risk_service())
    client = TestClient(create_app())

    create_response = client.post(
        "/skill-runs",
        headers={"X-API-Key": ADMIN_API_KEY},
        json={"task": "Simulate sandbox workflow."},
    )
    run_id = create_response.json()["run_id"]

    response = client.post(
        f"/skill-runs/{run_id}/approve",
        headers={"X-API-Key": ADMIN_API_KEY},
        json={
            "reason": "Approved for dry-run workflow simulation.",
            "comment": "Reviewed for the local demo.",
        },
    )

    assert response.status_code == 200

    body = response.json()
    assert body["run_id"] == run_id
    assert body["status"] == "completed"
    assert body["approval_status"] == "approved"
    assert body["final_report"] == "Skill run completed successfully."
    assert body["execution"] == {
        "attempted_step_count": 1,
        "completed_step_count": 1,
        "tool_names": ["trigger_workflow_dry_run"],
        "dry_run": True,
    }


def test_reject_skill_run_prevents_dry_run_tool_execution(monkeypatch) -> None:
    monkeypatch.setattr(skill_routes, "_skill_run_service", _high_risk_service())
    client = TestClient(create_app())

    create_response = client.post(
        "/skill-runs",
        headers={"X-API-Key": ADMIN_API_KEY},
        json={"task": "Simulate sandbox workflow."},
    )
    run_id = create_response.json()["run_id"]

    response = client.post(
        f"/skill-runs/{run_id}/reject",
        headers={"X-API-Key": ADMIN_API_KEY},
        json={
            "reason": "Rejected during dry-run review.",
            "comment": "Do not run this workflow.",
        },
    )

    assert response.status_code == 200

    body = response.json()
    assert body["run_id"] == run_id
    assert body["status"] == "rejected"
    assert body["approval_status"] == "rejected"
    assert body["final_report"] == (
        "Skill run rejected: Rejected during dry-run review."
    )
    assert body["execution"] == {
        "attempted_step_count": 0,
        "completed_step_count": 0,
        "tool_names": [],
        "dry_run": True,
    }


def test_skill_run_approval_and_rejection_unknown_run_return_safe_404() -> None:
    client = TestClient(create_app())

    approve_response = client.post(
        "/skill-runs/not-a-run/approve",
        headers={"X-API-Key": ADMIN_API_KEY},
        json={"reason": "Approved."},
    )
    reject_response = client.post(
        "/skill-runs/not-a-run/reject",
        headers={"X-API-Key": ADMIN_API_KEY},
        json={"reason": "Rejected."},
    )

    assert approve_response.status_code == 404
    assert approve_response.json()["detail"] == "Skill run not found."
    assert reject_response.status_code == 404
    assert reject_response.json()["detail"] == "Skill run not found."


def test_approve_skill_run_non_paused_run_returns_conflict() -> None:
    client = TestClient(create_app())

    create_response = client.post(
        "/skill-runs",
        headers={"X-API-Key": VIEWER_API_KEY},
        json={"task": "Inspect sandbox health."},
    )
    run_id = create_response.json()["run_id"]

    response = client.post(
        f"/skill-runs/{run_id}/approve",
        headers={"X-API-Key": ADMIN_API_KEY},
        json={"reason": "Approved."},
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "Skill run is not paused for approval."


def test_approve_skill_run_uses_server_derived_identity(monkeypatch) -> None:
    monkeypatch.setattr(skill_routes, "_skill_run_service", _high_risk_service())
    client = TestClient(create_app())

    create_response = client.post(
        "/skill-runs",
        headers={"X-API-Key": ADMIN_API_KEY},
        json={"task": "Simulate sandbox workflow."},
    )
    run_id = create_response.json()["run_id"]

    response = client.post(
        f"/skill-runs/{run_id}/approve",
        headers={"X-API-Key": VIEWER_API_KEY},
        json={"reason": "Client claims this is approved."},
    )

    assert response.status_code == 200

    body = response.json()
    assert body["status"] == "failed"
    assert "approval:approve" in body["error_message"]
    assert body["execution"] == {
        "attempted_step_count": 0,
        "completed_step_count": 0,
        "tool_names": [],
        "dry_run": True,
    }


@pytest.mark.parametrize(
    "route_suffix",
    [
        "approve",
        "reject",
    ],
)
@pytest.mark.parametrize(
    "field",
    [
        "identity",
        "user_id",
        "role",
        "scopes",
        "api_key",
        "api_key_id",
        "approval_authority",
        "policy_override",
        "risk_override",
        "approval_decision",
    ],
)
def test_skill_run_approval_actions_reject_identity_and_override_fields(
    route_suffix: str,
    field: str,
) -> None:
    client = TestClient(create_app())

    response = client.post(
        f"/skill-runs/not-a-run/{route_suffix}",
        headers={"X-API-Key": ADMIN_API_KEY},
        json={
            "reason": "Please continue.",
            field: "attacker-controlled",
        },
    )

    assert response.status_code == 422


def test_get_skill_run_audit_returns_lifecycle_evidence(monkeypatch) -> None:
    monkeypatch.setattr(skill_routes, "_skill_run_service", _high_risk_service())
    client = TestClient(create_app())

    create_response = client.post(
        "/skill-runs",
        headers={"X-API-Key": ADMIN_API_KEY},
        json={"task": "Simulate sandbox workflow."},
    )
    run_id = create_response.json()["run_id"]

    approve_response = client.post(
        f"/skill-runs/{run_id}/approve",
        headers={"X-API-Key": ADMIN_API_KEY},
        json={"reason": "Approved for audit evidence."},
    )
    assert approve_response.status_code == 200

    response = client.get(f"/skill-runs/{run_id}/audit")

    assert response.status_code == 200

    body = response.json()
    events = body["events"]
    event_types = [event["event_type"] for event in events]

    assert body["run_id"] == run_id
    assert "task_created" in event_types
    assert "tool_selected" in event_types
    assert "permission_checked" in event_types
    assert "approval_requested" in event_types
    assert "approval_granted" in event_types
    assert "tool_executed" in event_types
    assert "task_completed" in event_types

    assert any(
        event["metadata"].get("kind") == "skill_proposal"
        and event["metadata"]["skill_id"] == "simulate_sandbox_workflow"
        for event in events
    )
    assert any(
        event["metadata"].get("kind") == "proposal_validation"
        and event["metadata"]["approval_required"] is True
        and event["metadata"]["argument_validation_status"] == "accepted"
        and event["metadata"]["validated_argument_names"]
        == {"simulate_workflow": ["workflow_name", "ref"]}
        and event["metadata"]["redacted_argument_names"] == {"simulate_workflow": []}
        and event["metadata"]["argument_validation_issue_codes"] == []
        for event in events
    )
    assert any(
        event["event_type"] == "permission_checked"
        and event["metadata"].get("decision") == "require_approval"
        and event["metadata"].get("tool_name") == "trigger_workflow_dry_run"
        for event in events
    )
    assert any(
        event["event_type"] == "tool_executed"
        and event["metadata"].get("dry_run") is True
        and event["metadata"].get("success") is True
        for event in events
    )


def test_invalid_argument_values_are_absent_from_api_and_audit(monkeypatch) -> None:
    raw_rejected_value = "RAW_SECRET_TOKEN_DO_NOT_LEAK"
    invalid_service = SkillGraphService(
        proposer=StaticArgumentProposer(
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
    assert any(
        event["metadata"].get("kind") == "proposal_validation"
        and event["metadata"]["argument_validation_status"] == "rejected"
        and event["metadata"]["argument_validation_issue_codes"]
        == ["forbidden_argument_name"]
        for event in audit_response.json()["events"]
    )


def test_get_skill_run_audit_unknown_run_returns_safe_404() -> None:
    client = TestClient(create_app())

    response = client.get("/skill-runs/not-a-run/audit")

    assert response.status_code == 404
    assert response.json()["detail"] == "Skill run not found."
