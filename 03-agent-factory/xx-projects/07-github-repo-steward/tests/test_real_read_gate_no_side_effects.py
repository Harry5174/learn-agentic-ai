from __future__ import annotations

import builtins
import socket
from pathlib import Path

from github_repo_steward import (
    FakeProposalProvider,
    RawRepoSnapshot,
    RealReadRequest,
    analyze_repo_snapshot,
    build_approval_inbox,
    build_real_read_evidence_record,
    dry_run_ledger_record,
    evaluate_fake_default_real_read_gate,
    evaluate_real_read_request,
    evaluate_repo_proposals,
    load_github_api_fixture_payloads,
    map_github_api_payloads_to_canonical_snapshot,
    normalize_repo_snapshot,
    record_decision_to_ledger,
    record_operator_decision,
)


def test_gate_and_fake_default_adapter_path_work_without_secret_env_vars(
    monkeypatch,
) -> None:
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

    gate = evaluate_fake_default_real_read_gate()
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
        rationale="Approved for local real-read gate no-secret test only.",
    )
    ledger_record = record_decision_to_ledger(
        decision,
        inbox[0],
        evidence_refs=("artifact-7.10-no-secret-test",),
        source_snapshot_id=snapshot.repository.name,
    )
    dry_run = dry_run_ledger_record(ledger_record, inbox[0])
    evidence = build_real_read_evidence_record(
        gate,
        adapter_boundary_status="adapter_used",
        raw_payload_status="local_fixture_payload",
        canonical_snapshot_status="mapped_locally",
        normalization_status="normalized_locally",
        pipeline_status="local_pipeline_completed",
        summary="Fake/default adapter path only; no live GitHub read attempted.",
    )

    assert gate.verdict == "fake_default_allowed"
    assert gate.github_status == "not_called"
    assert gate.network_status == "not_used"
    assert dry_run.dry_run_status == "dry_run_completed"
    assert evidence.github_status == "not_called"
    assert evidence.pipeline_status == "local_pipeline_completed"


def test_gate_evaluation_does_not_open_network_sockets(monkeypatch) -> None:
    def fail_socket(*args: object, **kwargs: object) -> socket.socket:
        raise AssertionError("Real-read gate must not open network sockets.")

    monkeypatch.setattr(socket, "socket", fail_socket)

    gate = evaluate_fake_default_real_read_gate()

    assert gate.github_status == "not_called"
    assert gate.network_status == "not_used"


def test_preflight_allowed_does_not_open_network_sockets(monkeypatch) -> None:
    def fail_socket(*args: object, **kwargs: object) -> socket.socket:
        raise AssertionError("Real-read preflight gate must not call GitHub.")

    monkeypatch.setattr(socket, "socket", fail_socket)

    gate = evaluate_real_read_request(
        RealReadRequest(
            mode="real_read_requested",
            repository_full_name="fixture-owner/fixture-repo",
            requested_by="local-operator",
            product_owner_authorized=True,
            authorization_reference="po-read-only-preflight",
            credential_source="server_side_environment_reference",
            adapter_required=True,
            write_operations_allowed=False,
            network_access_requested=True,
            evidence_expected=("read-only-payload-shape",),
        )
    )
    evidence = build_real_read_evidence_record(
        gate,
        adapter_boundary_status="adapter_required_but_not_used",
        raw_payload_status="live_payload_not_captured",
        canonical_snapshot_status="not_available",
        normalization_status="not_available",
        pipeline_status="not_run",
    )

    assert gate.verdict == "real_read_preflight_allowed"
    assert evidence.github_status == "read_only_preflight_only"
    assert evidence.raw_payload_status == "live_payload_not_captured"


def test_gate_evaluation_does_not_open_files(monkeypatch) -> None:
    def fail_open(*args: object, **kwargs: object) -> object:
        raise AssertionError("Real-read gate must not read files or .env.")

    monkeypatch.setattr(builtins, "open", fail_open)

    gate = evaluate_fake_default_real_read_gate()
    evidence = build_real_read_evidence_record(
        gate,
        adapter_boundary_status="adapter_used",
        raw_payload_status="local_fixture_payload",
        canonical_snapshot_status="mapped_locally",
        normalization_status="normalized_locally",
        pipeline_status="local_pipeline_completed",
    )

    assert evidence.secret_status == "not_required_for_fake_default"
