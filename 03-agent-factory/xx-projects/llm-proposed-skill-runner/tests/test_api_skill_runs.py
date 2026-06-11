import pytest
from fastapi.testclient import TestClient

from app.api import skill_routes
from app.api.main import create_app
from app.identity.config import VIEWER_API_KEY
from app.proposer.fake import FakeProposer, FakeProposalScenario
from app.skill_graph.service import SkillGraphService


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
    assert body["execution"] == {
        "attempted_step_count": 1,
        "completed_step_count": 1,
        "tool_names": ["inspect_sandbox_issues"],
        "dry_run": True,
    }


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


def test_e1_2_skill_run_routes_are_not_registered() -> None:
    client = TestClient(create_app())

    get_response = client.get("/skill-runs/not-a-run")
    approve_response = client.post(
        "/skill-runs/not-a-run/approve",
        headers={"X-API-Key": VIEWER_API_KEY},
        json={"reason": "Approved."},
    )
    reject_response = client.post(
        "/skill-runs/not-a-run/reject",
        headers={"X-API-Key": VIEWER_API_KEY},
        json={"reason": "Rejected."},
    )
    audit_response = client.get("/skill-runs/not-a-run/audit")

    assert get_response.status_code == 404
    assert approve_response.status_code == 404
    assert reject_response.status_code == 404
    assert audit_response.status_code == 404
