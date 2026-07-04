from __future__ import annotations

from dataclasses import fields, replace
from pathlib import Path

import pytest

from github_repo_steward import (
    FakeProposalProvider,
    RawRepoSnapshot,
    RealReadEvidenceRecord,
    RealReadGateError,
    RealReadGateEvaluation,
    RealReadRequest,
    analyze_repo_snapshot,
    build_approval_inbox,
    build_real_read_evidence_record,
    dry_run_ledger_record,
    evaluate_fake_default_real_read_gate,
    evaluate_real_read_request,
    evaluate_repo_proposals,
    load_default_github_api_fixture_snapshot,
    normalize_repo_snapshot,
    record_decision_to_ledger,
    record_operator_decision,
)


def test_real_read_gate_models_contain_expected_local_fields_only() -> None:
    assert [field.name for field in fields(RealReadRequest)] == [
        "mode",
        "repository_full_name",
        "requested_by",
        "product_owner_authorized",
        "authorization_reference",
        "credential_source",
        "adapter_required",
        "write_operations_allowed",
        "network_access_requested",
        "evidence_expected",
    ]
    assert [field.name for field in fields(RealReadGateEvaluation)] == [
        "evaluation_id",
        "mode",
        "repository_full_name",
        "verdict",
        "reasons",
        "adapter_required",
        "github_status",
        "network_status",
        "write_status",
        "secret_status",
        "safe_to_attempt_real_read",
    ]
    assert [field.name for field in fields(RealReadEvidenceRecord)] == [
        "evidence_id",
        "evaluation_id",
        "repository_full_name",
        "mode",
        "adapter_boundary_status",
        "raw_payload_status",
        "canonical_snapshot_status",
        "normalization_status",
        "pipeline_status",
        "github_status",
        "write_status",
        "secret_status",
        "summary",
    ]
    forbidden_fields = {
        field.name
        for model in (
            RealReadRequest,
            RealReadGateEvaluation,
            RealReadEvidenceRecord,
        )
        for field in fields(model)
    }
    assert "github_write_token" not in forbidden_fields
    assert "comment_posted" not in forbidden_fields
    assert "label_applied" not in forbidden_fields
    assert "issue_closed" not in forbidden_fields
    assert "pr_merged" not in forbidden_fields
    assert "github_write_response" not in forbidden_fields


def test_fake_default_gate_evaluation_is_allowed_without_credentials() -> None:
    evaluation = evaluate_fake_default_real_read_gate()

    assert evaluation.evaluation_id == (
        "a7g:fake_default:local/fake-default:not-authorized-fake-default"
    )
    assert evaluation.verdict == "fake_default_allowed"
    assert evaluation.reasons == ()
    assert evaluation.github_status == "not_called"
    assert evaluation.network_status == "not_used"
    assert evaluation.write_status == "writes_forbidden"
    assert evaluation.secret_status == "not_required_for_fake_default"
    assert evaluation.safe_to_attempt_real_read is False


def test_real_read_without_product_owner_authorization_is_blocked() -> None:
    evaluation = evaluate_real_read_request(_real_read_request())

    assert evaluation.verdict == "real_read_blocked"
    assert "product_owner_authorization_required" in evaluation.reasons
    assert evaluation.github_status == "not_called"
    assert evaluation.network_status == "blocked"
    assert evaluation.safe_to_attempt_real_read is False


def test_real_read_without_repository_target_is_blocked() -> None:
    evaluation = evaluate_real_read_request(
        replace(
            _real_read_request(product_owner_authorized=True),
            repository_full_name="",
        )
    )

    assert evaluation.verdict == "real_read_blocked"
    assert "repository_full_name_required" in evaluation.reasons


def test_real_read_without_safe_credential_metadata_is_blocked() -> None:
    evaluation = evaluate_real_read_request(
        _real_read_request(
            product_owner_authorized=True,
            credential_source="request_body_token",
        )
    )

    assert evaluation.verdict == "real_read_blocked"
    assert "safe_credential_handling_required" in evaluation.reasons
    assert evaluation.secret_status == "credential_handling_required"


def test_real_read_without_adapter_boundary_is_blocked() -> None:
    evaluation = evaluate_real_read_request(
        _real_read_request(
            product_owner_authorized=True,
            adapter_required=False,
        )
    )

    assert evaluation.verdict == "real_read_blocked"
    assert "adapter_boundary_required" in evaluation.reasons


def test_real_read_with_write_operations_allowed_is_blocked() -> None:
    evaluation = evaluate_real_read_request(
        _real_read_request(
            product_owner_authorized=True,
            write_operations_allowed=True,
        )
    )

    assert evaluation.verdict == "real_read_blocked"
    assert "writes_forbidden" in evaluation.reasons
    assert evaluation.write_status == "writes_forbidden"


def test_real_read_with_safe_preflight_metadata_can_be_preflight_allowed() -> None:
    evaluation = evaluate_real_read_request(
        _real_read_request(product_owner_authorized=True)
    )

    assert evaluation.verdict == "real_read_preflight_allowed"
    assert evaluation.reasons == ()
    assert evaluation.github_status == "read_only_preflight_only"
    assert evaluation.network_status == "preflight_allowed"
    assert evaluation.write_status == "writes_forbidden"
    assert evaluation.secret_status == "credentials_not_inspected"
    assert evaluation.safe_to_attempt_real_read is True


def test_real_read_preflight_allowed_is_not_proof_of_real_read() -> None:
    evaluation = evaluate_real_read_request(
        _real_read_request(product_owner_authorized=True)
    )
    evidence = build_real_read_evidence_record(
        evaluation,
        adapter_boundary_status="adapter_required_but_not_used",
        raw_payload_status="live_payload_not_captured",
        canonical_snapshot_status="not_available",
        normalization_status="not_available",
        pipeline_status="not_run",
        summary="Preflight allowed only; no live GitHub read was attempted.",
    )

    assert evidence.github_status == "read_only_preflight_only"
    assert evidence.raw_payload_status == "live_payload_not_captured"
    assert evidence.pipeline_status == "not_run"


def test_evidence_record_can_represent_fake_default_adapter_path() -> None:
    evaluation = evaluate_fake_default_real_read_gate()

    evidence = build_real_read_evidence_record(
        evaluation,
        adapter_boundary_status="adapter_used",
        raw_payload_status="local_fixture_payload",
        canonical_snapshot_status="mapped_locally",
        normalization_status="normalized_locally",
        pipeline_status="local_pipeline_completed",
        summary="Fake/default adapter path only; no live GitHub read attempted.",
    )

    assert evidence.evidence_id == (
        "a7v:a7g:fake_default:local/fake-default:"
        "not-authorized-fake-default:adapter_used:local_fixture_payload:"
        "mapped_locally:normalized_locally:local_pipeline_completed"
    )
    assert evidence.github_status == "not_called"
    assert evidence.write_status == "writes_forbidden"
    assert evidence.secret_status == "not_required_for_fake_default"


def test_evidence_record_can_represent_blocked_real_read_path() -> None:
    evaluation = evaluate_real_read_request(_real_read_request())

    evidence = build_real_read_evidence_record(
        evaluation,
        adapter_boundary_status="blocked_before_adapter",
        raw_payload_status="blocked_no_raw_payload",
        canonical_snapshot_status="not_mapped_blocked",
        normalization_status="not_normalized_blocked",
        pipeline_status="blocked_before_pipeline",
        summary="Blocked before live read because authorization was absent.",
    )

    assert evidence.mode == "real_read_requested"
    assert evidence.github_status == "not_called"
    assert evidence.raw_payload_status == "blocked_no_raw_payload"


def test_gate_invariants_reject_live_write_or_bypass_claims() -> None:
    evaluation = evaluate_fake_default_real_read_gate()

    with pytest.raises(RealReadGateError, match="forbid writes"):
        replace(evaluation, write_status="writes_allowed")
    with pytest.raises(RealReadGateError, match="preflight"):
        replace(evaluation, safe_to_attempt_real_read=True)
    with pytest.raises(RealReadGateError, match="adapter boundary"):
        build_real_read_evidence_record(
            evaluation,
            adapter_boundary_status="blocked_before_adapter",
            raw_payload_status="local_fixture_payload",
            canonical_snapshot_status="mapped_locally",
            normalization_status="normalized_locally",
            pipeline_status="local_pipeline_completed",
        )


def test_malformed_gate_inputs_fail_safely() -> None:
    with pytest.raises(RealReadGateError, match="Unsupported real-read mode"):
        RealReadRequest(
            mode="live_write_requested",
            repository_full_name="owner/repo",
            requested_by="operator",
            product_owner_authorized=False,
            authorization_reference="none",
            credential_source="none",
            adapter_required=True,
            write_operations_allowed=False,
            network_access_requested=False,
            evidence_expected=(),
        )
    with pytest.raises(RealReadGateError, match="RealReadRequest"):
        evaluate_real_read_request(object())  # type: ignore[arg-type]
    with pytest.raises(RealReadGateError, match="RealReadGateEvaluation"):
        build_real_read_evidence_record(  # type: ignore[arg-type]
            object(),
            adapter_boundary_status="adapter_used",
            raw_payload_status="local_fixture_payload",
            canonical_snapshot_status="mapped_locally",
            normalization_status="normalized_locally",
            pipeline_status="local_pipeline_completed",
        )


def test_local_github_like_fixture_adapter_path_reaches_gate_evidence() -> None:
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
        rationale="Approved for local real-read gate test only.",
    )
    ledger_record = record_decision_to_ledger(
        decision,
        inbox[0],
        evidence_refs=("artifact-7.10-gate-test",),
        source_snapshot_id=snapshot.repository.name,
    )
    dry_run = dry_run_ledger_record(ledger_record, inbox[0])
    gate = evaluate_fake_default_real_read_gate()
    evidence = build_real_read_evidence_record(
        gate,
        adapter_boundary_status="adapter_used",
        raw_payload_status="local_fixture_payload",
        canonical_snapshot_status="mapped_locally",
        normalization_status="normalized_locally",
        pipeline_status="local_pipeline_completed",
        summary="Fake/default adapter path only; no live GitHub read attempted.",
    )

    assert snapshot.repository.name == "fixture-repo"
    assert findings
    assert proposals
    assert inbox
    assert dry_run.github_status == "not_called"
    assert evidence.pipeline_status == "local_pipeline_completed"


def _real_read_request(
    *,
    product_owner_authorized: bool = False,
    credential_source: str = "server_side_environment_reference",
    adapter_required: bool = True,
    write_operations_allowed: bool = False,
) -> RealReadRequest:
    return RealReadRequest(
        mode="real_read_requested",
        repository_full_name="fixture-owner/fixture-repo",
        requested_by="local-operator",
        product_owner_authorized=product_owner_authorized,
        authorization_reference="po-live-read-approval",
        credential_source=credential_source,
        adapter_required=adapter_required,
        write_operations_allowed=write_operations_allowed,
        network_access_requested=True,
        evidence_expected=("read-only-payload-shape", "adapter-boundary"),
    )
