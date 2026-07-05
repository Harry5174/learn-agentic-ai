from __future__ import annotations

import builtins
import socket
from pathlib import Path

from github_repo_steward import (
    FakeProposalProvider,
    RawRepoSnapshot,
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
    load_github_api_fixture_payloads,
    map_github_api_payloads_to_canonical_snapshot,
    normalize_repo_snapshot,
    record_decision_to_ledger,
    record_operator_decision,
)


def test_write_readiness_gate_and_full_pipeline_work_without_secret_env_vars(
    monkeypatch,
) -> None:
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

    payloads = load_github_api_fixture_payloads()
    canonical = map_github_api_payloads_to_canonical_snapshot(payloads)
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
        rationale="Approved for local no-secret write-readiness test.",
    )
    ledger_record = record_decision_to_ledger(
        decision,
        inbox[0],
        evidence_refs=("artifact-7.11-no-secret-test",),
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
        summary="Fake/default adapter path; no live read attempted.",
    )

    write_gate = evaluate_real_write_readiness(
        RealWriteReadinessRequest(
            mode="real_write_readiness_requested",
            repository_full_name="fixture-owner/fixture-repo",
            requested_by="local-operator",
            product_owner_authorized=True,
            authorization_reference="po-no-secret-test",
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
            evidence_expected=("write-readiness-no-secret-test",),
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
        summary="No-secret write-readiness test evidence.",
    )

    assert write_gate.verdict == "real_write_preflight_allowed"
    assert write_gate.github_status == "write_preflight_only"
    assert write_evidence.write_status == "write_preflight_only"
    assert dry_run.github_status == "not_called"
    assert read_evidence.pipeline_status == "local_pipeline_completed"


def test_write_readiness_gate_does_not_open_network_sockets(
    monkeypatch,
) -> None:
    def fail_socket(*args: object, **kwargs: object) -> socket.socket:
        raise AssertionError(
            "Write-readiness gate must not open network sockets."
        )

    monkeypatch.setattr(socket, "socket", fail_socket)

    gate = evaluate_fake_default_real_write_readiness_gate()

    assert gate.github_status == "not_called"
    assert gate.network_status == "not_used"


def test_preflight_allowed_does_not_open_network_sockets(
    monkeypatch,
) -> None:
    def fail_socket(*args: object, **kwargs: object) -> socket.socket:
        raise AssertionError(
            "Write-readiness preflight gate must not call GitHub."
        )

    monkeypatch.setattr(socket, "socket", fail_socket)

    gate = evaluate_real_write_readiness(
        RealWriteReadinessRequest(
            mode="real_write_readiness_requested",
            repository_full_name="fixture-owner/fixture-repo",
            requested_by="local-operator",
            product_owner_authorized=True,
            authorization_reference="po-socket-test",
            real_read_evidence_id="a7v:socket-test",
            dry_run_id="a7dr:socket-test",
            ledger_record_id="a7l:socket-test",
            decision_id="a7d:socket-test",
            proposal_id="a7p:socket-test",
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
            evidence_expected=("socket-test",),
        )
    )
    evidence = build_real_write_readiness_evidence_record(
        gate,
        adapter_boundary_status="adapter_confirmed",
        real_read_gate_status="real_read_gate_confirmed",
        dry_run_status="dry_run_completed",
        ledger_status="ledger_confirmed",
        policy_status="policy_confirmed",
        approval_status="approval_confirmed",
    )

    assert gate.verdict == "real_write_preflight_allowed"
    assert evidence.github_status == "write_preflight_only"


def test_write_readiness_gate_does_not_open_files(monkeypatch) -> None:
    def fail_open(*args: object, **kwargs: object) -> object:
        raise AssertionError(
            "Write-readiness gate must not read files or .env."
        )

    monkeypatch.setattr(builtins, "open", fail_open)

    gate = evaluate_fake_default_real_write_readiness_gate()
    evidence = build_real_write_readiness_evidence_record(
        gate,
        adapter_boundary_status="adapter_not_confirmed",
        real_read_gate_status="real_read_gate_not_confirmed",
        dry_run_status="dry_run_not_completed",
        ledger_status="ledger_not_confirmed",
        policy_status="policy_not_confirmed",
        approval_status="approval_not_confirmed",
    )

    assert evidence.secret_status == "not_required_for_fake_default"


def test_gate_requires_no_network(monkeypatch) -> None:
    def fail_socket(*args: object, **kwargs: object) -> socket.socket:
        raise AssertionError("Gate must not require network.")

    monkeypatch.setattr(socket, "socket", fail_socket)
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

    gate = evaluate_fake_default_real_write_readiness_gate()

    assert gate.verdict == "fake_default_write_readiness_blocked"
    assert gate.github_status == "not_called"
