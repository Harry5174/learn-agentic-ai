from __future__ import annotations

from dataclasses import replace

from github_repo_steward import (
    RealWriteReadinessRequest,
    build_real_write_readiness_evidence_record,
    evaluate_fake_default_real_write_readiness_gate,
    evaluate_real_write_readiness,
)


def _complete_request(
    *, product_owner_authorized: bool = True
) -> RealWriteReadinessRequest:
    return RealWriteReadinessRequest(
        mode="real_write_readiness_requested",
        repository_full_name="fixture-owner/fixture-repo",
        requested_by="local-operator",
        product_owner_authorized=product_owner_authorized,
        authorization_reference="po-write-readiness-det-test",
        real_read_evidence_id="a7v:det-read-evidence-id",
        dry_run_id="a7dr:det-dry-run-id",
        ledger_record_id="a7l:det-ledger-id",
        decision_id="a7d:det-decision-id",
        proposal_id="a7p:det-proposal-id",
        proposal_type="issue_comment",
        target_type="issue",
        target_number=42,
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
        evidence_expected=("det-test",),
    )


def test_fake_default_evaluation_ids_are_deterministic() -> None:
    a = evaluate_fake_default_real_write_readiness_gate()
    b = evaluate_fake_default_real_write_readiness_gate()

    assert a.evaluation_id == b.evaluation_id
    assert a.evaluation_id


def test_real_write_readiness_evaluation_ids_are_deterministic() -> None:
    request = _complete_request()
    a = evaluate_real_write_readiness(request)
    b = evaluate_real_write_readiness(request)

    assert a.evaluation_id == b.evaluation_id
    assert a.evaluation_id


def test_blocked_evaluation_ids_are_deterministic() -> None:
    request = _complete_request(product_owner_authorized=False)
    a = evaluate_real_write_readiness(request)
    b = evaluate_real_write_readiness(request)

    assert a.evaluation_id == b.evaluation_id
    assert a.verdict == "real_write_readiness_blocked"


def test_evidence_ids_are_deterministic() -> None:
    evaluation = evaluate_real_write_readiness(_complete_request())
    a = build_real_write_readiness_evidence_record(
        evaluation,
        adapter_boundary_status="adapter_confirmed",
        real_read_gate_status="real_read_gate_confirmed",
        dry_run_status="dry_run_completed",
        ledger_status="ledger_confirmed",
        policy_status="policy_confirmed",
        approval_status="approval_confirmed",
        summary="Determinism test.",
    )
    b = build_real_write_readiness_evidence_record(
        evaluation,
        adapter_boundary_status="adapter_confirmed",
        real_read_gate_status="real_read_gate_confirmed",
        dry_run_status="dry_run_completed",
        ledger_status="ledger_confirmed",
        policy_status="policy_confirmed",
        approval_status="approval_confirmed",
        summary="Determinism test.",
    )

    assert a.evidence_id == b.evidence_id
    assert a.evidence_id


def test_evaluation_ids_change_with_different_repositories() -> None:
    req_a = _complete_request()
    req_b = replace(req_a, repository_full_name="other/repo")

    a = evaluate_real_write_readiness(req_a)
    b = evaluate_real_write_readiness(req_b)

    assert a.evaluation_id != b.evaluation_id


def test_evaluation_ids_change_with_different_write_operation_types() -> None:
    req_a = _complete_request()
    req_b = replace(
        req_a, write_operation_type="future_pull_request_comment"
    )

    a = evaluate_real_write_readiness(req_a)
    b = evaluate_real_write_readiness(req_b)

    assert a.evaluation_id != b.evaluation_id


def test_fake_default_evidence_ids_are_deterministic() -> None:
    evaluation = evaluate_fake_default_real_write_readiness_gate()
    a = build_real_write_readiness_evidence_record(
        evaluation,
        adapter_boundary_status="adapter_not_confirmed",
        real_read_gate_status="real_read_gate_not_confirmed",
        dry_run_status="dry_run_not_completed",
        ledger_status="ledger_not_confirmed",
        policy_status="policy_not_confirmed",
        approval_status="approval_not_confirmed",
    )
    b = build_real_write_readiness_evidence_record(
        evaluation,
        adapter_boundary_status="adapter_not_confirmed",
        real_read_gate_status="real_read_gate_not_confirmed",
        dry_run_status="dry_run_not_completed",
        ledger_status="ledger_not_confirmed",
        policy_status="policy_not_confirmed",
        approval_status="approval_not_confirmed",
    )

    assert a.evidence_id == b.evidence_id
    assert a.evidence_id
