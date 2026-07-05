from __future__ import annotations

from dataclasses import fields, replace
from pathlib import Path

import pytest

from github_repo_steward import (
    FakeProposalProvider,
    RawRepoSnapshot,
    RealWriteReadinessError,
    RealWriteReadinessEvaluation,
    RealWriteReadinessEvidenceRecord,
    RealWriteReadinessRequest,
    analyze_repo_snapshot,
    build_approval_inbox,
    build_real_read_evidence_record,
    build_real_write_readiness_evidence_record,
    dry_run_ledger_record,
    evaluate_fake_default_real_read_gate,
    evaluate_fake_default_real_write_readiness_gate,
    evaluate_real_write_readiness,
    evaluate_repo_proposals,
    load_default_github_api_fixture_snapshot,
    normalize_repo_snapshot,
    record_decision_to_ledger,
    record_operator_decision,
)


# --- Model shape tests ---


def test_real_write_readiness_models_contain_expected_local_fields_only() -> None:
    assert [field.name for field in fields(RealWriteReadinessRequest)] == [
        "mode",
        "repository_full_name",
        "requested_by",
        "product_owner_authorized",
        "authorization_reference",
        "real_read_evidence_id",
        "dry_run_id",
        "ledger_record_id",
        "decision_id",
        "proposal_id",
        "proposal_type",
        "target_type",
        "target_number",
        "operator_decision",
        "write_operation_type",
        "adapter_boundary_confirmed",
        "real_read_gate_confirmed",
        "dry_run_confirmed",
        "ledger_confirmed",
        "policy_confirmed",
        "approval_confirmed",
        "writes_allowed",
        "credential_source",
        "secret_handling_confirmed",
        "executor_runtime_enabled",
        "evidence_expected",
    ]
    assert [field.name for field in fields(RealWriteReadinessEvaluation)] == [
        "evaluation_id",
        "mode",
        "repository_full_name",
        "write_operation_type",
        "verdict",
        "reasons",
        "github_status",
        "network_status",
        "write_status",
        "secret_status",
        "executor_status",
        "safe_for_future_write_review",
    ]
    assert [
        field.name for field in fields(RealWriteReadinessEvidenceRecord)
    ] == [
        "evidence_id",
        "evaluation_id",
        "repository_full_name",
        "mode",
        "write_operation_type",
        "real_read_evidence_id",
        "dry_run_id",
        "ledger_record_id",
        "decision_id",
        "proposal_id",
        "adapter_boundary_status",
        "real_read_gate_status",
        "dry_run_status",
        "ledger_status",
        "policy_status",
        "approval_status",
        "github_status",
        "write_status",
        "executor_status",
        "secret_status",
        "summary",
    ]
    # Verify no write-execution fields exist
    all_field_names = {
        field.name
        for model in (
            RealWriteReadinessRequest,
            RealWriteReadinessEvaluation,
            RealWriteReadinessEvidenceRecord,
        )
        for field in fields(model)
    }
    forbidden = {
        "github_write_token",
        "comment_posted",
        "label_applied",
        "issue_closed",
        "pr_merged",
        "write_request_id",
        "github_write_response",
        "external_url",
        "posted_at",
        "executed_at",
    }
    assert not forbidden & all_field_names


# --- Fake/default gate tests ---


def test_fake_default_write_readiness_gate_is_blocked() -> None:
    evaluation = evaluate_fake_default_real_write_readiness_gate()

    assert evaluation.verdict == "fake_default_write_readiness_blocked"
    assert "fake_default_mode_blocks_real_write_readiness" in evaluation.reasons
    assert evaluation.safe_for_future_write_review is False


def test_fake_default_gate_does_not_require_credentials() -> None:
    evaluation = evaluate_fake_default_real_write_readiness_gate()

    assert evaluation.secret_status == "not_required_for_fake_default"


def test_fake_default_gate_has_github_status_not_called() -> None:
    evaluation = evaluate_fake_default_real_write_readiness_gate()

    assert evaluation.github_status == "not_called"


def test_fake_default_gate_has_network_status_not_used() -> None:
    evaluation = evaluate_fake_default_real_write_readiness_gate()

    assert evaluation.network_status == "not_used"


# --- Blocked real-write readiness tests ---


def test_real_write_readiness_without_product_owner_authorization_is_blocked() -> None:
    evaluation = evaluate_real_write_readiness(_write_readiness_request())

    assert evaluation.verdict == "real_write_readiness_blocked"
    assert "product_owner_authorization_required" in evaluation.reasons
    assert evaluation.safe_for_future_write_review is False


def test_real_write_readiness_without_repository_full_name_is_blocked() -> None:
    evaluation = evaluate_real_write_readiness(
        replace(
            _write_readiness_request(product_owner_authorized=True),
            repository_full_name="",
        )
    )

    assert evaluation.verdict == "real_write_readiness_blocked"
    assert "repository_full_name_required" in evaluation.reasons


def test_real_write_readiness_without_real_read_evidence_id_is_blocked() -> None:
    evaluation = evaluate_real_write_readiness(
        replace(
            _write_readiness_request(product_owner_authorized=True),
            real_read_evidence_id="",
        )
    )

    assert evaluation.verdict == "real_write_readiness_blocked"
    assert "real_read_evidence_id_required" in evaluation.reasons


def test_real_write_readiness_without_dry_run_id_is_blocked() -> None:
    evaluation = evaluate_real_write_readiness(
        replace(
            _write_readiness_request(product_owner_authorized=True),
            dry_run_id="",
        )
    )

    assert evaluation.verdict == "real_write_readiness_blocked"
    assert "dry_run_id_required" in evaluation.reasons


def test_real_write_readiness_without_ledger_record_id_is_blocked() -> None:
    evaluation = evaluate_real_write_readiness(
        replace(
            _write_readiness_request(product_owner_authorized=True),
            ledger_record_id="",
        )
    )

    assert evaluation.verdict == "real_write_readiness_blocked"
    assert "ledger_record_id_required" in evaluation.reasons


def test_real_write_readiness_without_decision_id_is_blocked() -> None:
    evaluation = evaluate_real_write_readiness(
        replace(
            _write_readiness_request(product_owner_authorized=True),
            decision_id="",
        )
    )

    assert evaluation.verdict == "real_write_readiness_blocked"
    assert "decision_id_required" in evaluation.reasons


def test_real_write_readiness_without_proposal_id_is_blocked() -> None:
    evaluation = evaluate_real_write_readiness(
        replace(
            _write_readiness_request(product_owner_authorized=True),
            proposal_id="",
        )
    )

    assert evaluation.verdict == "real_write_readiness_blocked"
    assert "proposal_id_required" in evaluation.reasons


def test_rejected_operator_decision_is_blocked() -> None:
    evaluation = evaluate_real_write_readiness(
        replace(
            _write_readiness_request(product_owner_authorized=True),
            operator_decision="rejected_by_operator",
        )
    )

    assert evaluation.verdict == "real_write_readiness_blocked"
    assert "operator_decision_must_be_approved" in evaluation.reasons


def test_unsupported_write_operation_type_is_blocked() -> None:
    evaluation = evaluate_real_write_readiness(
        replace(
            _write_readiness_request(product_owner_authorized=True),
            write_operation_type="future_label_mutation",
        )
    )

    assert evaluation.verdict == "real_write_readiness_blocked"
    assert "unsupported_write_operation_type" in evaluation.reasons


def test_adapter_boundary_not_confirmed_is_blocked() -> None:
    evaluation = evaluate_real_write_readiness(
        replace(
            _write_readiness_request(product_owner_authorized=True),
            adapter_boundary_confirmed=False,
        )
    )

    assert evaluation.verdict == "real_write_readiness_blocked"
    assert "adapter_boundary_confirmation_required" in evaluation.reasons


def test_real_read_gate_not_confirmed_is_blocked() -> None:
    evaluation = evaluate_real_write_readiness(
        replace(
            _write_readiness_request(product_owner_authorized=True),
            real_read_gate_confirmed=False,
        )
    )

    assert evaluation.verdict == "real_write_readiness_blocked"
    assert "real_read_gate_confirmation_required" in evaluation.reasons


def test_dry_run_not_confirmed_is_blocked() -> None:
    evaluation = evaluate_real_write_readiness(
        replace(
            _write_readiness_request(product_owner_authorized=True),
            dry_run_confirmed=False,
        )
    )

    assert evaluation.verdict == "real_write_readiness_blocked"
    assert "dry_run_confirmation_required" in evaluation.reasons


def test_ledger_not_confirmed_is_blocked() -> None:
    evaluation = evaluate_real_write_readiness(
        replace(
            _write_readiness_request(product_owner_authorized=True),
            ledger_confirmed=False,
        )
    )

    assert evaluation.verdict == "real_write_readiness_blocked"
    assert "ledger_confirmation_required" in evaluation.reasons


def test_policy_not_confirmed_is_blocked() -> None:
    evaluation = evaluate_real_write_readiness(
        replace(
            _write_readiness_request(product_owner_authorized=True),
            policy_confirmed=False,
        )
    )

    assert evaluation.verdict == "real_write_readiness_blocked"
    assert "policy_confirmation_required" in evaluation.reasons


def test_approval_not_confirmed_is_blocked() -> None:
    evaluation = evaluate_real_write_readiness(
        replace(
            _write_readiness_request(product_owner_authorized=True),
            approval_confirmed=False,
        )
    )

    assert evaluation.verdict == "real_write_readiness_blocked"
    assert "approval_confirmation_required" in evaluation.reasons


def test_secret_handling_not_confirmed_is_blocked() -> None:
    evaluation = evaluate_real_write_readiness(
        replace(
            _write_readiness_request(product_owner_authorized=True),
            secret_handling_confirmed=False,
        )
    )

    assert evaluation.verdict == "real_write_readiness_blocked"
    assert "secret_handling_confirmation_required" in evaluation.reasons


def test_executor_runtime_enabled_is_blocked() -> None:
    evaluation = evaluate_real_write_readiness(
        replace(
            _write_readiness_request(product_owner_authorized=True),
            executor_runtime_enabled=True,
        )
    )

    assert evaluation.verdict == "real_write_readiness_blocked"
    assert "executor_runtime_must_be_disabled" in evaluation.reasons


# --- Preflight-allowed tests ---


def test_complete_safe_request_produces_write_preflight_allowed() -> None:
    evaluation = evaluate_real_write_readiness(
        _write_readiness_request(product_owner_authorized=True)
    )

    assert evaluation.verdict == "real_write_preflight_allowed"
    assert evaluation.reasons == ()
    assert evaluation.github_status == "write_preflight_only"
    assert evaluation.network_status == "preflight_allowed"
    assert evaluation.write_status == "write_preflight_only"
    assert evaluation.secret_status == "credentials_not_inspected"
    assert evaluation.executor_status == "preflight_only"
    assert evaluation.safe_for_future_write_review is True


def test_write_preflight_allowed_does_not_call_github() -> None:
    evaluation = evaluate_real_write_readiness(
        _write_readiness_request(product_owner_authorized=True)
    )

    # github_status == "write_preflight_only" means the gate recorded
    # metadata about a future write path but did not call GitHub.
    assert evaluation.github_status == "write_preflight_only"
    assert evaluation.write_status == "write_preflight_only"


def test_write_preflight_allowed_does_not_execute() -> None:
    evaluation = evaluate_real_write_readiness(
        _write_readiness_request(product_owner_authorized=True)
    )

    assert evaluation.executor_status == "preflight_only"


def test_write_preflight_allowed_is_not_proof_of_real_write() -> None:
    evaluation = evaluate_real_write_readiness(
        _write_readiness_request(product_owner_authorized=True)
    )
    evidence = build_real_write_readiness_evidence_record(
        evaluation,
        adapter_boundary_status="adapter_confirmed",
        real_read_gate_status="real_read_gate_confirmed",
        dry_run_status="dry_run_completed",
        ledger_status="ledger_confirmed",
        policy_status="policy_confirmed",
        approval_status="approval_confirmed",
        summary="Write-readiness preflight only; no real write attempted.",
    )

    assert evidence.write_status == "write_preflight_only"
    assert evidence.github_status == "write_preflight_only"
    assert evidence.executor_status == "preflight_only"


def test_write_preflight_allowed_for_pull_request_comment() -> None:
    evaluation = evaluate_real_write_readiness(
        _write_readiness_request(
            product_owner_authorized=True,
            write_operation_type="future_pull_request_comment",
        )
    )

    assert evaluation.verdict == "real_write_preflight_allowed"
    assert evaluation.write_operation_type == "future_pull_request_comment"


# --- Evidence record tests ---


def test_evidence_record_can_represent_blocked_fake_default_path() -> None:
    evaluation = evaluate_fake_default_real_write_readiness_gate()

    evidence = build_real_write_readiness_evidence_record(
        evaluation,
        adapter_boundary_status="adapter_not_confirmed",
        real_read_gate_status="real_read_gate_not_confirmed",
        dry_run_status="dry_run_not_completed",
        ledger_status="ledger_not_confirmed",
        policy_status="policy_not_confirmed",
        approval_status="approval_not_confirmed",
        summary="Fake/default write-readiness gate blocked.",
    )

    assert evidence.mode == "fake_default"
    assert evidence.github_status == "not_called"
    assert evidence.write_status == "not_written"


def test_evidence_record_can_represent_blocked_real_write_path() -> None:
    evaluation = evaluate_real_write_readiness(_write_readiness_request())

    evidence = build_real_write_readiness_evidence_record(
        evaluation,
        adapter_boundary_status="blocked_before_adapter",
        real_read_gate_status="blocked_before_read_gate",
        dry_run_status="blocked_before_dry_run",
        ledger_status="blocked_before_ledger",
        policy_status="blocked_before_policy",
        approval_status="blocked_before_approval",
        summary="Blocked before write-readiness preflight.",
    )

    assert evidence.mode == "real_write_readiness_requested"
    assert evidence.github_status == "not_called"
    assert evidence.write_status == "writes_forbidden"


def test_evidence_record_can_represent_preflight_allowed_path() -> None:
    evaluation = evaluate_real_write_readiness(
        _write_readiness_request(product_owner_authorized=True)
    )

    evidence = build_real_write_readiness_evidence_record(
        evaluation,
        adapter_boundary_status="adapter_confirmed",
        real_read_gate_status="real_read_gate_confirmed",
        dry_run_status="dry_run_completed",
        ledger_status="ledger_confirmed",
        policy_status="policy_confirmed",
        approval_status="approval_confirmed",
        summary="Write-readiness preflight allowed only.",
    )

    assert evidence.mode == "real_write_readiness_requested"
    assert evidence.write_status == "write_preflight_only"
    assert evidence.executor_status == "preflight_only"


# --- Invariant tests ---


def test_gate_invariants_reject_invalid_verdict_combinations() -> None:
    evaluation = evaluate_fake_default_real_write_readiness_gate()

    with pytest.raises(RealWriteReadinessError, match="safe for"):
        replace(
            evaluation,
            safe_for_future_write_review=True,
        )
    with pytest.raises(RealWriteReadinessError, match="Only fake_default"):
        replace(
            evaluation,
            mode="real_write_readiness_requested",
        )


def test_malformed_gate_inputs_fail_safely() -> None:
    with pytest.raises(
        RealWriteReadinessError, match="Unsupported write-readiness mode"
    ):
        RealWriteReadinessRequest(
            mode="live_write_execute",
            repository_full_name="owner/repo",
            requested_by="operator",
            product_owner_authorized=False,
            authorization_reference="none",
            real_read_evidence_id="",
            dry_run_id="",
            ledger_record_id="",
            decision_id="",
            proposal_id="",
            proposal_type="",
            target_type="",
            target_number=0,
            operator_decision="",
            write_operation_type="",
            adapter_boundary_confirmed=False,
            real_read_gate_confirmed=False,
            dry_run_confirmed=False,
            ledger_confirmed=False,
            policy_confirmed=False,
            approval_confirmed=False,
            writes_allowed=False,
            credential_source="none",
            secret_handling_confirmed=False,
            executor_runtime_enabled=False,
            evidence_expected=(),
        )
    with pytest.raises(
        RealWriteReadinessError, match="RealWriteReadinessRequest"
    ):
        evaluate_real_write_readiness(object())  # type: ignore[arg-type]
    with pytest.raises(
        RealWriteReadinessError, match="RealWriteReadinessEvaluation"
    ):
        build_real_write_readiness_evidence_record(  # type: ignore[arg-type]
            object(),
            adapter_boundary_status="adapter_confirmed",
            real_read_gate_status="real_read_gate_confirmed",
            dry_run_status="dry_run_completed",
            ledger_status="ledger_confirmed",
            policy_status="policy_confirmed",
            approval_status="approval_confirmed",
        )


def test_gate_does_not_mutate_request_objects() -> None:
    request = _write_readiness_request(product_owner_authorized=True)
    before_mode = request.mode
    before_repo = request.repository_full_name

    evaluate_real_write_readiness(request)

    assert request.mode == before_mode
    assert request.repository_full_name == before_repo


# --- Full local pipeline integration ---


def test_local_pipeline_to_write_readiness_gate() -> None:
    canonical = load_default_github_api_fixture_snapshot()
    raw = RawRepoSnapshot(
        data=canonical,
        source_path=Path("local-github-like-fixture"),
    )
    snapshot = normalize_repo_snapshot(raw)
    findings = analyze_repo_snapshot(snapshot)
    proposals = FakeProposalProvider().propose(snapshot, findings)
    evaluations = evaluate_repo_proposals(proposals)
    inbox = build_approval_inbox(proposals, evaluations)
    decision = record_operator_decision(
        inbox[0],
        decision="approved_by_operator",
        decided_by="local-operator",
        rationale="Approved for local write-readiness gate test only.",
    )
    ledger_record = record_decision_to_ledger(
        decision,
        inbox[0],
        evidence_refs=("artifact-7.11-gate-test",),
        source_snapshot_id=snapshot.repository.name,
    )
    dry_run = dry_run_ledger_record(ledger_record, inbox[0])
    read_gate = evaluate_fake_default_real_read_gate()
    read_evidence = build_real_read_evidence_record(
        read_gate,
        adapter_boundary_status="adapter_used",
        raw_payload_status="local_fixture_payload",
        canonical_snapshot_status="mapped_locally",
        normalization_status="normalized_locally",
        pipeline_status="local_pipeline_completed",
        summary="Fake/default adapter path only.",
    )

    write_gate = evaluate_real_write_readiness(
        RealWriteReadinessRequest(
            mode="real_write_readiness_requested",
            repository_full_name="fixture-owner/fixture-repo",
            requested_by="local-operator",
            product_owner_authorized=True,
            authorization_reference="po-write-readiness-test",
            real_read_evidence_id=read_evidence.evidence_id,
            dry_run_id=dry_run.dry_run_id,
            ledger_record_id=ledger_record.ledger_record_id,
            decision_id=decision.decision_id,
            proposal_id=inbox[0].proposal_id,
            proposal_type=inbox[0].proposal_type,
            target_type=inbox[0].target_type,
            target_number=inbox[0].target_number,
            operator_decision="approved_by_operator",
            write_operation_type="future_issue_comment",
            adapter_boundary_confirmed=True,
            real_read_gate_confirmed=True,
            dry_run_confirmed=True,
            ledger_confirmed=True,
            policy_confirmed=True,
            approval_confirmed=True,
            writes_allowed=False,
            credential_source="server_side_environment_reference",
            secret_handling_confirmed=True,
            executor_runtime_enabled=False,
            evidence_expected=("write-readiness-gate-evidence",),
        )
    )
    write_evidence = build_real_write_readiness_evidence_record(
        write_gate,
        adapter_boundary_status="adapter_confirmed",
        real_read_gate_status="real_read_gate_confirmed",
        dry_run_status="dry_run_completed",
        ledger_status="ledger_confirmed",
        policy_status="policy_confirmed",
        approval_status="approval_confirmed",
        summary="Local write-readiness gate test evidence.",
    )

    assert snapshot.repository.name == "fixture-repo"
    assert findings
    assert proposals
    assert inbox
    assert dry_run.github_status == "not_called"
    assert read_evidence.pipeline_status == "local_pipeline_completed"
    assert write_gate.verdict == "real_write_preflight_allowed"
    assert write_gate.github_status == "write_preflight_only"
    assert write_evidence.write_status == "write_preflight_only"


def test_gate_works_without_github_token(monkeypatch) -> None:
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    evaluation = evaluate_fake_default_real_write_readiness_gate()
    assert evaluation.verdict == "fake_default_write_readiness_blocked"


def test_gate_works_without_openai_api_key(monkeypatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    evaluation = evaluate_fake_default_real_write_readiness_gate()
    assert evaluation.verdict == "fake_default_write_readiness_blocked"


def test_gate_works_without_anthropic_api_key(monkeypatch) -> None:
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    evaluation = evaluate_fake_default_real_write_readiness_gate()
    assert evaluation.verdict == "fake_default_write_readiness_blocked"


# --- Helper ---


def _write_readiness_request(
    *,
    product_owner_authorized: bool = False,
    write_operation_type: str = "future_issue_comment",
) -> RealWriteReadinessRequest:
    return RealWriteReadinessRequest(
        mode="real_write_readiness_requested",
        repository_full_name="fixture-owner/fixture-repo",
        requested_by="local-operator",
        product_owner_authorized=product_owner_authorized,
        authorization_reference="po-write-readiness-approval",
        real_read_evidence_id="a7v:read-evidence-id",
        dry_run_id="a7dr:dry-run-id",
        ledger_record_id="a7l:ledger-id",
        decision_id="a7d:decision-id",
        proposal_id="a7p:proposal-id",
        proposal_type="issue_comment",
        target_type="issue",
        target_number=42,
        operator_decision="approved_by_operator",
        write_operation_type=write_operation_type,
        adapter_boundary_confirmed=True,
        real_read_gate_confirmed=True,
        dry_run_confirmed=True,
        ledger_confirmed=True,
        policy_confirmed=True,
        approval_confirmed=True,
        writes_allowed=False,
        credential_source="server_side_environment_reference",
        secret_handling_confirmed=True,
        executor_runtime_enabled=False,
        evidence_expected=("write-readiness-gate-evidence",),
    )
