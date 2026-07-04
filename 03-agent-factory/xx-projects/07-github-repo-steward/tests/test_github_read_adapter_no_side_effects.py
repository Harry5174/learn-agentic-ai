from __future__ import annotations

import builtins
import socket
from pathlib import Path

from github_repo_steward import (
    FakeProposalProvider,
    RawRepoSnapshot,
    analyze_repo_snapshot,
    build_approval_inbox,
    dry_run_ledger_record,
    evaluate_repo_proposals,
    load_github_api_fixture_payloads,
    map_github_api_payloads_to_canonical_snapshot,
    normalize_repo_snapshot,
    record_decision_to_ledger,
    record_operator_decision,
)


def test_adapter_does_not_require_common_secret_env_vars(monkeypatch) -> None:
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
        rationale="Approved for local adapter no-secret test only.",
    )
    ledger_record = record_decision_to_ledger(
        decision,
        inbox[0],
        evidence_refs=("artifact-7.9-no-secret-test",),
        source_snapshot_id=snapshot.repository.name,
    )
    dry_run = dry_run_ledger_record(ledger_record, inbox[0])

    assert dry_run.dry_run_status == "dry_run_completed"
    assert dry_run.github_status == "not_called"
    assert dry_run.execution_status == "not_executed"


def test_adapter_mapping_does_not_open_network_sockets(monkeypatch) -> None:
    def fail_socket(*args: object, **kwargs: object) -> socket.socket:
        raise AssertionError("GitHub read adapter must not open network sockets.")

    payloads = load_github_api_fixture_payloads()
    monkeypatch.setattr(socket, "socket", fail_socket)

    canonical = map_github_api_payloads_to_canonical_snapshot(payloads)

    assert canonical["repository"]["name"] == "fixture-repo"  # type: ignore[index]


def test_adapter_mapping_does_not_open_files(monkeypatch) -> None:
    def fail_open(*args: object, **kwargs: object) -> object:
        raise AssertionError("GitHub read adapter mapping must not create files.")

    payloads = load_github_api_fixture_payloads()
    monkeypatch.setattr(builtins, "open", fail_open)

    canonical = map_github_api_payloads_to_canonical_snapshot(payloads)

    assert len(canonical["pull_requests"]) == 2  # type: ignore[arg-type]
