import pytest
from fastapi.testclient import TestClient

from app.api import skill_routes
from app.api.main import create_app
from app.identity.config import ADMIN_API_KEY, OPERATOR_API_KEY, VIEWER_API_KEY
from app.proposer.fake import FakeProposer, FakeProposalScenario
from app.skill_graph.service import SkillGraphService


def _high_risk_service() -> SkillGraphService:
    return SkillGraphService(
        proposer=FakeProposer(FakeProposalScenario.VALID_HIGH_RISK)
    )


def _github_comment_service() -> SkillGraphService:
    return SkillGraphService(
        proposer=FakeProposer(FakeProposalScenario.VALID_GITHUB_COMMENT)
    )


def _create_paused_approval(client: TestClient) -> dict:
    response = client.post(
        "/skill-runs",
        headers={"X-API-Key": ADMIN_API_KEY},
        json={"task": "Simulate sandbox workflow."},
    )

    assert response.status_code == 202

    body = response.json()
    assert body["status"] == "paused_for_approval"
    return body


def test_operator_approval_list_returns_pending_summaries(monkeypatch) -> None:
    monkeypatch.setattr(skill_routes, "_skill_run_service", _high_risk_service())
    client = TestClient(create_app())
    paused = _create_paused_approval(client)

    response = client.get(
        "/operator/approvals",
        headers={"X-API-Key": OPERATOR_API_KEY},
    )

    assert response.status_code == 200

    body = response.json()
    approvals = body["approvals"]

    assert len(approvals) == 1
    assert approvals[0]["approval_id"] == paused["run_id"]
    assert approvals[0]["run_id"] == paused["run_id"]
    assert approvals[0]["status"] == "paused_for_approval"
    assert approvals[0]["task"] == "Simulate sandbox workflow."
    assert approvals[0]["risk_level"] == "high"
    assert approvals[0]["required_scopes"] == ["tools:trigger_workflow"]
    assert approvals[0]["policy_status"] == "require_approval"
    assert approvals[0]["approval_status"] == "pending"
    assert approvals[0]["tool_name"] == "trigger_workflow_dry_run"
    assert approvals[0]["target"] is None
    assert approvals[0]["side_effect_id"] is None
    assert approvals[0]["args_hash"] is None
    assert approvals[0]["requested_by"] == "demo_admin"
    assert approvals[0]["execution_mode"] == {
        "mode": "fake_default",
        "real_github_enabled": False,
        "token_required": False,
    }


def test_operator_approval_detail_returns_read_only_detail(monkeypatch) -> None:
    monkeypatch.setattr(skill_routes, "_skill_run_service", _high_risk_service())
    client = TestClient(create_app())
    paused = _create_paused_approval(client)

    response = client.get(
        f"/operator/approvals/{paused['run_id']}",
        headers={"X-API-Key": OPERATOR_API_KEY},
    )

    assert response.status_code == 200

    body = response.json()
    assert body["approval_id"] == paused["run_id"]
    assert body["proposal"]["proposed_skill_id"] == "simulate_sandbox_workflow"
    assert body["proposal"]["proposed_tool_names"] == ["trigger_workflow_dry_run"]
    assert body["policy_decisions"] == [
        {
            "decision": "require_approval",
            "tool_name": "trigger_workflow_dry_run",
            "reason": "High-risk tool requires approval before execution.",
            "required_scopes": ["tools:trigger_workflow"],
            "missing_scopes": [],
        }
    ]
    assert body["validated_arguments"] == {
        "simulate_workflow": {
            "workflow_name": "ci.yml",
            "ref": "main",
        }
    }
    event_types = [event["event_type"] for event in body["audit_events"]]
    assert event_types[:3] == [
        "task_created",
        "tool_selected",
        "permission_checked",
    ]
    assert event_types[-1] == "approval_requested"


def test_unknown_operator_approval_returns_safe_404(monkeypatch) -> None:
    monkeypatch.setattr(skill_routes, "_skill_run_service", _high_risk_service())
    client = TestClient(create_app())

    response = client.get(
        "/operator/approvals/not-a-real-approval",
        headers={"X-API-Key": OPERATOR_API_KEY},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Approval not found."


def test_operator_approval_list_and_detail_are_read_only(monkeypatch) -> None:
    service = _high_risk_service()
    monkeypatch.setattr(skill_routes, "_skill_run_service", service)
    client = TestClient(create_app())
    paused = _create_paused_approval(client)

    list_response = client.get(
        "/operator/approvals",
        headers={"X-API-Key": OPERATOR_API_KEY},
    )
    detail_response = client.get(
        f"/operator/approvals/{paused['run_id']}",
        headers={"X-API-Key": OPERATOR_API_KEY},
    )
    run_response = client.get(f"/skill-runs/{paused['run_id']}")

    assert list_response.status_code == 200
    assert detail_response.status_code == 200
    assert run_response.status_code == 200
    assert run_response.json()["status"] == "paused_for_approval"
    assert run_response.json()["approval_status"] == "pending"
    assert run_response.json()["execution"] == {
        "attempted_step_count": 0,
        "completed_step_count": 0,
        "tool_names": [],
        "dry_run": True,
    }


@pytest.mark.parametrize("suffix", ["approve", "reject"])
def test_operator_approval_action_routes_exist_and_enforce_safety(
    monkeypatch,
    suffix: str,
) -> None:
    monkeypatch.setattr(skill_routes, "_skill_run_service", _high_risk_service())
    client = TestClient(create_app())
    paused = _create_paused_approval(client)

    payload = (
        {"decision_reason": "Rejected through explicit operator route."}
        if suffix == "reject"
        else {"decision_reason": "Approved through explicit operator route."}
    )
    response = client.post(
        f"/operator/approvals/{paused['run_id']}/{suffix}",
        headers={"X-API-Key": ADMIN_API_KEY},
        json=payload,
    )

    assert response.status_code == 200
    assert response.json()["approval_id"] == paused["run_id"]
    assert response.json()["decision"] == suffix


@pytest.mark.parametrize(
    "spoofed_query",
    [
        "?role=admin",
        "?scopes=admin",
        "?identity=admin",
        "?actor=admin",
    ],
)
def test_operator_approval_query_spoofing_is_ignored(
    monkeypatch,
    spoofed_query: str,
) -> None:
    monkeypatch.setattr(skill_routes, "_skill_run_service", _high_risk_service())
    client = TestClient(create_app())
    paused = _create_paused_approval(client)

    list_response = client.get(
        f"/operator/approvals{spoofed_query}",
        headers={"X-API-Key": VIEWER_API_KEY},
    )
    detail_response = client.get(
        f"/operator/approvals/{paused['run_id']}{spoofed_query}",
        headers={"X-API-Key": VIEWER_API_KEY},
    )

    assert list_response.status_code == 200
    assert detail_response.status_code == 200
    assert list_response.json()["approvals"][0]["requested_by"] == "demo_admin"
    assert detail_response.json()["requested_by"] == "demo_admin"


def test_operator_approval_api_requires_no_token_or_env(monkeypatch) -> None:
    monkeypatch.delenv("AGENT_FACTORY_GITHUB_TOKEN", raising=False)
    monkeypatch.setattr(skill_routes, "_skill_run_service", _high_risk_service())
    client = TestClient(create_app())
    _create_paused_approval(client)

    response = client.get(
        "/operator/approvals",
        headers={"X-API-Key": VIEWER_API_KEY},
    )

    assert response.status_code == 200
    assert response.json()["approvals"][0]["execution_mode"] == {
        "mode": "fake_default",
        "real_github_enabled": False,
        "token_required": False,
    }


def test_operator_approval_api_does_not_call_github_client(monkeypatch) -> None:
    monkeypatch.setattr(skill_routes, "_skill_run_service", _high_risk_service())
    client = TestClient(create_app())
    paused = _create_paused_approval(client)

    list_response = client.get(
        "/operator/approvals",
        headers={"X-API-Key": OPERATOR_API_KEY},
    )
    detail_response = client.get(
        f"/operator/approvals/{paused['run_id']}",
        headers={"X-API-Key": OPERATOR_API_KEY},
    )
    run_response = client.get(f"/skill-runs/{paused['run_id']}")

    assert list_response.status_code == 200
    assert detail_response.status_code == 200
    assert run_response.json()["execution"]["attempted_step_count"] == 0


def test_operator_approval_responses_do_not_expose_token_like_values(
    monkeypatch,
) -> None:
    secret_like_task = (
        "Review request with ghp_fake_secret and "
        "Authorization: Bearer fake-token."
    )
    monkeypatch.setattr(skill_routes, "_skill_run_service", _high_risk_service())
    client = TestClient(create_app())

    create_response = client.post(
        "/skill-runs",
        headers={"X-API-Key": ADMIN_API_KEY},
        json={"task": secret_like_task},
    )
    run_id = create_response.json()["run_id"]

    list_response = client.get(
        "/operator/approvals",
        headers={"X-API-Key": OPERATOR_API_KEY},
    )
    detail_response = client.get(
        f"/operator/approvals/{run_id}",
        headers={"X-API-Key": OPERATOR_API_KEY},
    )

    assert list_response.status_code == 200
    assert detail_response.status_code == 200

    forbidden_fragments = [
        "ghp_fake_secret",
        "Authorization",
        "Bearer",
        "fake-token",
    ]

    for fragment in forbidden_fragments:
        assert fragment not in list_response.text
        assert fragment not in detail_response.text


@pytest.mark.parametrize("suffix", ["approve", "reject"])
def test_viewer_cannot_approve_or_reject_operator_approval(
    monkeypatch,
    suffix: str,
) -> None:
    service = _high_risk_service()
    monkeypatch.setattr(skill_routes, "_skill_run_service", service)
    client = TestClient(create_app())
    paused = _create_paused_approval(client)

    payload = (
        {"decision_reason": "Viewer rejection attempt."}
        if suffix == "reject"
        else {"decision_reason": "Viewer approval attempt."}
    )
    response = client.post(
        f"/operator/approvals/{paused['run_id']}/{suffix}",
        headers={"X-API-Key": VIEWER_API_KEY},
        json=payload,
    )

    assert response.status_code == 403
    assert service.get_run(paused["run_id"])["status"].value == "paused_for_approval"


def test_operator_can_approve_pending_operator_approval(monkeypatch) -> None:
    service = _high_risk_service()
    monkeypatch.setattr(skill_routes, "_skill_run_service", service)
    client = TestClient(create_app())
    paused = _create_paused_approval(client)

    response = client.post(
        f"/operator/approvals/{paused['run_id']}/approve",
        headers={"X-API-Key": OPERATOR_API_KEY},
        json={"decision_reason": "Approved for local demo execution."},
    )

    assert response.status_code == 200

    body = response.json()
    assert body["approval_id"] == paused["run_id"]
    assert body["run_id"] == paused["run_id"]
    assert body["decision"] == "approve"
    assert body["status"] == "completed"
    assert body["approval_status"] == "approved"
    assert body["decision_reason"] == "Approved for local demo execution."
    assert body["actor"]["user_id"] == "demo_operator"
    assert body["actor"]["role"] == "operator"
    assert body["actor"]["server_derived"] is True
    assert "approval:approve" in body["actor"]["scopes"]
    assert body["execution_mode"] == {
        "mode": "fake_default",
        "real_github_enabled": False,
        "token_required": False,
    }

    audit_trail = service.get_audit(paused["run_id"])
    approval_event = next(
        event for event in audit_trail if event.event_type.value == "approval_granted"
    )
    assert approval_event.actor_id == "demo_operator"
    assert approval_event.metadata["reason"] == "Approved for local demo execution."


def test_operator_can_reject_pending_operator_approval(monkeypatch) -> None:
    service = _high_risk_service()
    monkeypatch.setattr(skill_routes, "_skill_run_service", service)
    client = TestClient(create_app())
    paused = _create_paused_approval(client)

    response = client.post(
        f"/operator/approvals/{paused['run_id']}/reject",
        headers={"X-API-Key": OPERATOR_API_KEY},
        json={"decision_reason": "Rejected by operator review."},
    )

    assert response.status_code == 200

    body = response.json()
    assert body["decision"] == "reject"
    assert body["status"] == "rejected"
    assert body["approval_status"] == "rejected"
    assert body["actor"]["user_id"] == "demo_operator"
    assert "approval:reject" in body["actor"]["scopes"]

    audit_trail = service.get_audit(paused["run_id"])
    event_types = [event.event_type.value for event in audit_trail]
    assert "approval_rejected" in event_types
    assert "tool_executed" not in event_types
    rejection_event = next(
        event for event in audit_trail if event.event_type.value == "approval_rejected"
    )
    assert rejection_event.actor_id == "demo_operator"
    assert rejection_event.metadata["reason"] == "Rejected by operator review."


@pytest.mark.parametrize("suffix", ["approve", "reject"])
def test_admin_can_approve_or_reject_operator_approval(
    monkeypatch,
    suffix: str,
) -> None:
    monkeypatch.setattr(skill_routes, "_skill_run_service", _high_risk_service())
    client = TestClient(create_app())
    paused = _create_paused_approval(client)

    response = client.post(
        f"/operator/approvals/{paused['run_id']}/{suffix}",
        headers={"X-API-Key": ADMIN_API_KEY},
        json={"decision_reason": f"Admin {suffix} decision."},
    )

    assert response.status_code == 200
    assert response.json()["actor"]["user_id"] == "demo_admin"
    assert response.json()["decision"] == suffix


@pytest.mark.parametrize("suffix", ["approve", "reject"])
@pytest.mark.parametrize(
    "field",
    [
        "actor_id",
        "api_key_id",
        "role",
        "scopes",
        "identity",
        "is_admin",
        "is_operator",
        "approval_authority",
    ],
)
def test_operator_decision_body_cannot_claim_identity_or_authority(
    monkeypatch,
    suffix: str,
    field: str,
) -> None:
    monkeypatch.setattr(skill_routes, "_skill_run_service", _high_risk_service())
    client = TestClient(create_app())
    paused = _create_paused_approval(client)

    response = client.post(
        f"/operator/approvals/{paused['run_id']}/{suffix}",
        headers={"X-API-Key": ADMIN_API_KEY},
        json={
            "decision_reason": "Attempting to smuggle identity.",
            field: "attacker-controlled",
        },
    )

    assert response.status_code == 422


@pytest.mark.parametrize("suffix", ["approve", "reject"])
def test_operator_decision_query_spoofing_is_ignored(
    monkeypatch,
    suffix: str,
) -> None:
    service = _high_risk_service()
    monkeypatch.setattr(skill_routes, "_skill_run_service", service)
    client = TestClient(create_app())
    paused = _create_paused_approval(client)

    response = client.post(
        (
            f"/operator/approvals/{paused['run_id']}/{suffix}"
            "?role=admin&scopes=approval:approve&actor=demo_admin"
        ),
        headers={"X-API-Key": VIEWER_API_KEY},
        json={"decision_reason": "Query string claims authority."},
    )

    assert response.status_code == 403
    assert service.get_run(paused["run_id"])["status"].value == "paused_for_approval"


def test_operator_rejection_requires_decision_reason(monkeypatch) -> None:
    monkeypatch.setattr(skill_routes, "_skill_run_service", _high_risk_service())
    client = TestClient(create_app())
    paused = _create_paused_approval(client)

    response = client.post(
        f"/operator/approvals/{paused['run_id']}/reject",
        headers={"X-API-Key": ADMIN_API_KEY},
        json={},
    )

    assert response.status_code == 422
    assert response.json()["detail"] == "decision_reason is required for rejection."


@pytest.mark.parametrize("suffix", ["approve", "reject"])
def test_operator_decision_unknown_approval_returns_safe_404(
    monkeypatch,
    suffix: str,
) -> None:
    monkeypatch.setattr(skill_routes, "_skill_run_service", _high_risk_service())
    client = TestClient(create_app())

    response = client.post(
        f"/operator/approvals/not-a-real-approval/{suffix}",
        headers={"X-API-Key": ADMIN_API_KEY},
        json={"decision_reason": "Missing approval."},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Approval not found."


def test_terminal_approval_cannot_be_approved_again(monkeypatch) -> None:
    monkeypatch.setattr(skill_routes, "_skill_run_service", _high_risk_service())
    client = TestClient(create_app())
    paused = _create_paused_approval(client)

    first = client.post(
        f"/operator/approvals/{paused['run_id']}/approve",
        headers={"X-API-Key": ADMIN_API_KEY},
        json={"decision_reason": "First approval."},
    )
    second = client.post(
        f"/operator/approvals/{paused['run_id']}/approve",
        headers={"X-API-Key": ADMIN_API_KEY},
        json={"decision_reason": "Stale approval."},
    )

    assert first.status_code == 200
    assert second.status_code == 409
    assert "not pending" in second.json()["detail"]


def test_terminal_approval_cannot_be_rejected_again(monkeypatch) -> None:
    monkeypatch.setattr(skill_routes, "_skill_run_service", _high_risk_service())
    client = TestClient(create_app())
    paused = _create_paused_approval(client)

    first = client.post(
        f"/operator/approvals/{paused['run_id']}/reject",
        headers={"X-API-Key": ADMIN_API_KEY},
        json={"decision_reason": "First rejection."},
    )
    second = client.post(
        f"/operator/approvals/{paused['run_id']}/reject",
        headers={"X-API-Key": ADMIN_API_KEY},
        json={"decision_reason": "Stale rejection."},
    )

    assert first.status_code == 200
    assert second.status_code == 409
    assert "not pending" in second.json()["detail"]


def test_expected_side_effect_id_mismatch_fails_safely(monkeypatch) -> None:
    monkeypatch.setattr(skill_routes, "_skill_run_service", _github_comment_service())
    client = TestClient(create_app())
    paused = _create_paused_approval(client)

    response = client.post(
        f"/operator/approvals/{paused['run_id']}/approve",
        headers={"X-API-Key": OPERATOR_API_KEY},
        json={
            "decision_reason": "Approve with stale side effect.",
            "expected_side_effect_id": "not-the-current-side-effect",
        },
    )

    assert response.status_code == 409
    assert "side_effect_id" in response.json()["detail"]


def test_expected_args_hash_mismatch_fails_safely(monkeypatch) -> None:
    monkeypatch.setattr(skill_routes, "_skill_run_service", _github_comment_service())
    client = TestClient(create_app())
    paused = _create_paused_approval(client)

    response = client.post(
        f"/operator/approvals/{paused['run_id']}/approve",
        headers={"X-API-Key": OPERATOR_API_KEY},
        json={
            "decision_reason": "Approve with stale hash.",
            "expected_args_hash": "not-the-current-args-hash",
        },
    )

    assert response.status_code == 409
    assert "args_hash" in response.json()["detail"]


@pytest.mark.parametrize("field", ["expected_side_effect_id", "expected_args_hash"])
def test_expected_value_unavailable_fails_safely(monkeypatch, field: str) -> None:
    monkeypatch.setattr(skill_routes, "_skill_run_service", _high_risk_service())
    client = TestClient(create_app())
    paused = _create_paused_approval(client)

    response = client.post(
        f"/operator/approvals/{paused['run_id']}/approve",
        headers={"X-API-Key": OPERATOR_API_KEY},
        json={
            "decision_reason": "Approve with unavailable expectation.",
            field: "unavailable-value",
        },
    )

    assert response.status_code == 409
    assert "to compare" in response.json()["detail"]


def test_github_comment_approval_returns_side_effect_identity_without_live_github(
    monkeypatch,
) -> None:
    monkeypatch.delenv("AGENT_FACTORY_GITHUB_TOKEN", raising=False)
    monkeypatch.setattr(skill_routes, "_skill_run_service", _github_comment_service())
    client = TestClient(create_app())
    paused = _create_paused_approval(client)

    response = client.post(
        f"/operator/approvals/{paused['run_id']}/approve",
        headers={"X-API-Key": OPERATOR_API_KEY},
        json={"decision_reason": "Approved for fake GitHub comment."},
    )

    assert response.status_code == 200

    body = response.json()
    assert body["side_effect_id"]
    assert body["args_hash"]
    assert body["execution_mode"] == {
        "mode": "fake_default",
        "real_github_enabled": False,
        "token_required": False,
    }
    assert "AGENT_FACTORY_GITHUB_TOKEN" not in response.text


def test_operator_approval_status_returns_current_status(monkeypatch) -> None:
    service = _high_risk_service()
    monkeypatch.setattr(skill_routes, "_skill_run_service", service)
    client = TestClient(create_app())
    paused = _create_paused_approval(client)

    response = client.get(
        f"/operator/approvals/{paused['run_id']}/status",
        headers={"X-API-Key": OPERATOR_API_KEY},
    )

    assert response.status_code == 200

    body = response.json()
    assert body["approval_id"] == paused["run_id"]
    assert body["run_id"] == paused["run_id"]
    assert body["status"] == "paused_for_approval"
    assert body["approval_status"] == "pending"
    assert body["decision_state"] == "pending"
    assert body["can_approve"] is True
    assert body["can_reject"] is True
    assert body["action_unavailable_reason"] is None
    assert body["execution_mode"] == {
        "mode": "fake_default",
        "real_github_enabled": False,
        "token_required": False,
    }


def test_viewer_can_read_visibility_but_cannot_decide(monkeypatch) -> None:
    service = _high_risk_service()
    monkeypatch.setattr(skill_routes, "_skill_run_service", service)
    client = TestClient(create_app())
    paused = _create_paused_approval(client)

    status_response = client.get(
        (
            f"/operator/approvals/{paused['run_id']}/status"
            "?role=admin&scopes=approval:approve&actor=demo_admin"
        ),
        headers={"X-API-Key": VIEWER_API_KEY},
    )
    audit_response = client.get(
        f"/operator/approvals/{paused['run_id']}/audit",
        headers={"X-API-Key": VIEWER_API_KEY},
    )

    assert status_response.status_code == 200
    assert audit_response.status_code == 200
    assert status_response.json()["can_approve"] is False
    assert status_response.json()["can_reject"] is False
    assert status_response.json()["action_unavailable_reason"] == (
        "Current identity cannot approve or reject this approval."
    )


def test_operator_approval_audit_returns_local_demo_evidence(monkeypatch) -> None:
    monkeypatch.setattr(skill_routes, "_skill_run_service", _high_risk_service())
    client = TestClient(create_app())
    paused = _create_paused_approval(client)

    response = client.get(
        f"/operator/approvals/{paused['run_id']}/audit",
        headers={"X-API-Key": OPERATOR_API_KEY},
    )

    assert response.status_code == 200

    body = response.json()
    assert body["approval_id"] == paused["run_id"]
    assert body["run_id"] == paused["run_id"]
    assert body["audit_scope"] == "local_demo"
    assert "production-grade" in body["audit_limitations"]

    event_types = [event["event_type"] for event in body["events"]]
    assert event_types[:3] == [
        "task_created",
        "tool_selected",
        "permission_checked",
    ]
    assert event_types[-1] == "approval_requested"
    assert body["events"][0]["sequence"] == 1


def test_visibility_unknown_ids_return_safe_404(monkeypatch) -> None:
    monkeypatch.setattr(skill_routes, "_skill_run_service", _high_risk_service())
    client = TestClient(create_app())

    status_response = client.get(
        "/operator/approvals/not-a-real-approval/status",
        headers={"X-API-Key": OPERATOR_API_KEY},
    )
    audit_response = client.get(
        "/operator/approvals/not-a-real-approval/audit",
        headers={"X-API-Key": OPERATOR_API_KEY},
    )
    side_effect_response = client.get(
        "/operator/side-effects/not-a-real-side-effect",
        headers={"X-API-Key": OPERATOR_API_KEY},
    )

    assert status_response.status_code == 404
    assert status_response.json()["detail"] == "Approval not found."
    assert audit_response.status_code == 404
    assert audit_response.json()["detail"] == "Approval not found."
    assert side_effect_response.status_code == 404
    assert side_effect_response.json()["detail"] == "Side effect not found."


def test_visibility_endpoints_are_read_only_and_do_not_mutate_run_state(
    monkeypatch,
) -> None:
    service = _high_risk_service()
    monkeypatch.setattr(skill_routes, "_skill_run_service", service)
    client = TestClient(create_app())
    paused = _create_paused_approval(client)
    run_id = paused["run_id"]
    before = service.get_run(run_id)

    status_response = client.get(
        f"/operator/approvals/{run_id}/status",
        headers={"X-API-Key": OPERATOR_API_KEY},
    )
    audit_response = client.get(
        f"/operator/approvals/{run_id}/audit",
        headers={"X-API-Key": OPERATOR_API_KEY},
    )
    after = service.get_run(run_id)

    assert status_response.status_code == 200
    assert audit_response.status_code == 200
    assert after["status"] == before["status"]
    assert after.get("approval_decision") == before.get("approval_decision")
    assert after.get("tool_results") == before.get("tool_results")
    assert len(after.get("audit_trail", [])) == len(before.get("audit_trail", []))


def test_visibility_endpoints_require_no_token_or_env(monkeypatch) -> None:
    monkeypatch.delenv("AGENT_FACTORY_GITHUB_TOKEN", raising=False)
    monkeypatch.setattr(skill_routes, "_skill_run_service", _github_comment_service())
    client = TestClient(create_app())
    paused = _create_paused_approval(client)

    status_response = client.get(
        f"/operator/approvals/{paused['run_id']}/status",
        headers={"X-API-Key": VIEWER_API_KEY},
    )
    audit_response = client.get(
        f"/operator/approvals/{paused['run_id']}/audit",
        headers={"X-API-Key": VIEWER_API_KEY},
    )
    side_effect_id = status_response.json()["side_effect_id"]
    side_effect_response = client.get(
        f"/operator/side-effects/{side_effect_id}",
        headers={"X-API-Key": VIEWER_API_KEY},
    )

    assert status_response.status_code == 200
    assert audit_response.status_code == 200
    assert side_effect_response.status_code == 200
    assert "AGENT_FACTORY_GITHUB_TOKEN" not in status_response.text
    assert "AGENT_FACTORY_GITHUB_TOKEN" not in audit_response.text
    assert "AGENT_FACTORY_GITHUB_TOKEN" not in side_effect_response.text


def test_approval_followed_by_status_read_shows_updated_status(
    monkeypatch,
) -> None:
    monkeypatch.setattr(skill_routes, "_skill_run_service", _high_risk_service())
    client = TestClient(create_app())
    paused = _create_paused_approval(client)

    approve_response = client.post(
        f"/operator/approvals/{paused['run_id']}/approve",
        headers={"X-API-Key": OPERATOR_API_KEY},
        json={"decision_reason": "Approved before status visibility."},
    )
    status_response = client.get(
        f"/operator/approvals/{paused['run_id']}/status",
        headers={"X-API-Key": OPERATOR_API_KEY},
    )

    assert approve_response.status_code == 200
    assert status_response.status_code == 200

    body = status_response.json()
    assert body["status"] == "completed"
    assert body["approval_status"] == "approved"
    assert body["can_approve"] is False
    assert body["can_reject"] is False
    assert body["action_unavailable_reason"] == "Approval is not pending."
    assert body["decision_history"][0]["reason"] == (
        "Approved before status visibility."
    )
    assert body["execution_result"]["attempted_step_count"] == 1
    assert body["execution_result"]["completed_step_count"] == 1


def test_rejection_followed_by_audit_and_status_read_shows_evidence(
    monkeypatch,
) -> None:
    monkeypatch.setattr(skill_routes, "_skill_run_service", _high_risk_service())
    client = TestClient(create_app())
    paused = _create_paused_approval(client)

    reject_response = client.post(
        f"/operator/approvals/{paused['run_id']}/reject",
        headers={"X-API-Key": OPERATOR_API_KEY},
        json={"decision_reason": "Rejected before audit visibility."},
    )
    status_response = client.get(
        f"/operator/approvals/{paused['run_id']}/status",
        headers={"X-API-Key": OPERATOR_API_KEY},
    )
    audit_response = client.get(
        f"/operator/approvals/{paused['run_id']}/audit",
        headers={"X-API-Key": OPERATOR_API_KEY},
    )

    assert reject_response.status_code == 200
    assert status_response.status_code == 200
    assert audit_response.status_code == 200
    assert status_response.json()["approval_status"] == "rejected"

    event_types = [event["event_type"] for event in audit_response.json()["events"]]
    assert "approval_rejected" in event_types
    assert "tool_executed" not in event_types
    assert audit_response.json()["decision_history"][0]["reason"] == (
        "Rejected before audit visibility."
    )


def test_side_effect_endpoint_returns_local_demo_ledger_evidence_when_available(
    monkeypatch,
) -> None:
    monkeypatch.delenv("AGENT_FACTORY_GITHUB_TOKEN", raising=False)
    monkeypatch.setattr(skill_routes, "_skill_run_service", _github_comment_service())
    client = TestClient(create_app())
    paused = _create_paused_approval(client)

    approve_response = client.post(
        f"/operator/approvals/{paused['run_id']}/approve",
        headers={"X-API-Key": OPERATOR_API_KEY},
        json={"decision_reason": "Approved for fake side-effect visibility."},
    )
    side_effect_id = approve_response.json()["side_effect_id"]
    response = client.get(
        f"/operator/side-effects/{side_effect_id}",
        headers={"X-API-Key": OPERATOR_API_KEY},
    )

    assert approve_response.status_code == 200
    assert response.status_code == 200

    body = response.json()
    assert body["side_effect_id"] == side_effect_id
    assert body["run_id"] == paused["run_id"]
    assert body["tool_name"] == "post_github_issue_comment"
    assert body["repository"] == "Harry5174/learn-agentic-ai"
    assert body["issue_number"] == 1
    assert body["args_hash"]
    assert body["status"] == "succeeded"
    assert body["ledger_status"] == "succeeded"
    assert body["record_available"] is True
    assert body["external_result_summary"]["client_called"] is True
    assert body["execution_mode"]["real_github_enabled"] is False
    assert "AGENT_FACTORY_GITHUB_TOKEN" not in response.text


def test_side_effect_endpoint_returns_limitation_for_known_unexecuted_side_effect(
    monkeypatch,
) -> None:
    monkeypatch.setattr(skill_routes, "_skill_run_service", _github_comment_service())
    client = TestClient(create_app())
    paused = _create_paused_approval(client)

    status_response = client.get(
        f"/operator/approvals/{paused['run_id']}/status",
        headers={"X-API-Key": OPERATOR_API_KEY},
    )
    side_effect_id = status_response.json()["side_effect_id"]
    side_effect_response = client.get(
        f"/operator/side-effects/{side_effect_id}",
        headers={"X-API-Key": OPERATOR_API_KEY},
    )

    assert status_response.status_code == 200
    assert side_effect_response.status_code == 200
    assert side_effect_response.json()["record_available"] is False
    assert side_effect_response.json()["ledger_status"] == "not_available"
    assert "no ledger record is available" in side_effect_response.json()["message"]


def test_visibility_responses_do_not_expose_token_like_values(
    monkeypatch,
) -> None:
    dangerous_task = (
        "Review <img src=x onerror=alert(1)> <script>alert(1)</script> "
        "with ghp_fake_secret and Authorization: Bearer fake-token."
    )
    monkeypatch.setattr(skill_routes, "_skill_run_service", _high_risk_service())
    client = TestClient(create_app())

    create_response = client.post(
        "/skill-runs",
        headers={"X-API-Key": ADMIN_API_KEY},
        json={"task": dangerous_task},
    )
    run_id = create_response.json()["run_id"]

    status_response = client.get(
        f"/operator/approvals/{run_id}/status",
        headers={"X-API-Key": OPERATOR_API_KEY},
    )
    audit_response = client.get(
        f"/operator/approvals/{run_id}/audit",
        headers={"X-API-Key": OPERATOR_API_KEY},
    )

    assert status_response.status_code == 200
    assert audit_response.status_code == 200
    assert "[redacted]" in status_response.text
    assert "[redacted]" in audit_response.text

    forbidden_fragments = [
        "ghp_fake_secret",
        "Authorization",
        "Bearer",
        "fake-token",
    ]
    for fragment in forbidden_fragments:
        assert fragment not in status_response.text
        assert fragment not in audit_response.text


def test_side_effect_visibility_read_does_not_mutate_terminal_run(
    monkeypatch,
) -> None:
    service = _github_comment_service()
    monkeypatch.setattr(skill_routes, "_skill_run_service", service)
    client = TestClient(create_app())
    paused = _create_paused_approval(client)

    approve_response = client.post(
        f"/operator/approvals/{paused['run_id']}/approve",
        headers={"X-API-Key": OPERATOR_API_KEY},
        json={"decision_reason": "Approved before side-effect read."},
    )
    side_effect_id = approve_response.json()["side_effect_id"]
    before = service.get_run(paused["run_id"])
    response = client.get(
        f"/operator/side-effects/{side_effect_id}",
        headers={"X-API-Key": OPERATOR_API_KEY},
    )
    after = service.get_run(paused["run_id"])

    assert response.status_code == 200
    assert after["status"] == before["status"]
    assert after.get("approval_decision") == before.get("approval_decision")
    assert after.get("tool_results") == before.get("tool_results")
    assert len(after.get("audit_trail", [])) == len(before.get("audit_trail", []))
    assert "github_pat_" not in response.text
    assert "ghp_" not in response.text
