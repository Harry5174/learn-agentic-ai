from __future__ import annotations

import builtins
import socket

from github_repo_steward import (
    ApprovalInboxItem,
    FakeProposalProvider,
    LedgerAuditRecord,
    analyze_repo_snapshot,
    build_approval_inbox,
    dry_run_ledger_record,
    evaluate_repo_proposals,
    load_default_fixture_snapshot,
    normalize_repo_snapshot,
    record_decision_to_ledger,
    record_operator_decision,
)


def test_dry_run_does_not_require_common_secret_env_vars(monkeypatch) -> None:
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

    raw = load_default_fixture_snapshot()
    snapshot = normalize_repo_snapshot(raw)
    findings = analyze_repo_snapshot(snapshot)
    proposals = FakeProposalProvider().propose(snapshot, findings)
    evaluations = evaluate_repo_proposals(proposals)
    inbox = build_approval_inbox(proposals, evaluations)
    decision = record_operator_decision(
        inbox[0],
        decision="approved_by_operator",
        decided_by="local-operator",
        rationale="Approved for local dry-run test only.",
    )
    ledger_record = record_decision_to_ledger(
        decision,
        inbox[0],
        evidence_refs=("artifact-7.8-no-secret-test",),
        source_snapshot_id=snapshot.repository.name,
    )

    dry_run = dry_run_ledger_record(ledger_record, inbox[0])

    assert dry_run.dry_run_status == "dry_run_completed"
    assert dry_run.execution_status == "not_executed"
    assert dry_run.github_status == "not_called"
    assert dry_run.external_side_effect_status == "none"


def test_dry_run_does_not_open_network_sockets(monkeypatch) -> None:
    def fail_socket(*args: object, **kwargs: object) -> socket.socket:
        raise AssertionError("Dry-run executor must not open network sockets.")

    inbox, ledger_record = _default_inbox_and_ledger_record()
    monkeypatch.setattr(socket, "socket", fail_socket)

    dry_run = dry_run_ledger_record(ledger_record, inbox[0])

    assert dry_run.github_status == "not_called"
    assert dry_run.execution_status == "not_executed"


def test_dry_run_does_not_open_files(monkeypatch) -> None:
    def fail_open(*args: object, **kwargs: object) -> object:
        raise AssertionError("Dry-run executor must not create files.")

    inbox, ledger_record = _default_inbox_and_ledger_record()
    monkeypatch.setattr(builtins, "open", fail_open)

    dry_run = dry_run_ledger_record(ledger_record, inbox[0])

    assert dry_run.ledger_record_status == "verified_local_audit_record"
    assert dry_run.external_side_effect_status == "none"


def _default_inbox_and_ledger_record() -> tuple[
    list[ApprovalInboxItem],
    LedgerAuditRecord,
]:
    raw = load_default_fixture_snapshot()
    snapshot = normalize_repo_snapshot(raw)
    findings = analyze_repo_snapshot(snapshot)
    proposals = FakeProposalProvider().propose(snapshot, findings)
    evaluations = evaluate_repo_proposals(proposals)
    inbox = build_approval_inbox(proposals, evaluations)
    decision = record_operator_decision(
        inbox[0],
        decision="approved_by_operator",
        decided_by="local-operator",
        rationale="Approved for local dry-run test only.",
    )
    ledger_record = record_decision_to_ledger(decision, inbox[0])
    return inbox, ledger_record
