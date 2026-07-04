from __future__ import annotations

import builtins
import socket

from github_repo_steward import (
    ApprovalInboxItem,
    FakeProposalProvider,
    OperatorDecisionRecord,
    analyze_repo_snapshot,
    build_approval_inbox,
    evaluate_repo_proposals,
    load_default_fixture_snapshot,
    normalize_repo_snapshot,
    record_decision_to_ledger,
    record_operator_decision,
)


def test_ledger_does_not_require_common_secret_env_vars(monkeypatch) -> None:
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
        rationale="Approved for local ledger-record test only.",
    )
    ledger_record = record_decision_to_ledger(
        decision,
        inbox[0],
        evidence_refs=("artifact-7.7-no-secret-test",),
        source_snapshot_id=snapshot.repository.name,
    )

    assert ledger_record.record_type == "operator_decision_audit"
    assert ledger_record.execution_status == "not_executed"
    assert ledger_record.github_status == "not_called"
    assert ledger_record.executor_status == "not_triggered"


def test_ledger_does_not_open_network_sockets(monkeypatch) -> None:
    def fail_socket(*args: object, **kwargs: object) -> socket.socket:
        raise AssertionError("Ledger audit must not open network sockets.")

    inbox, decision = _default_inbox_and_decision()
    monkeypatch.setattr(socket, "socket", fail_socket)

    ledger_record = record_decision_to_ledger(decision, inbox[0])

    assert ledger_record.github_status == "not_called"
    assert ledger_record.executor_status == "not_triggered"


def test_ledger_does_not_open_files(monkeypatch) -> None:
    def fail_open(*args: object, **kwargs: object) -> object:
        raise AssertionError("Ledger audit must not create files.")

    inbox, decision = _default_inbox_and_decision()
    monkeypatch.setattr(builtins, "open", fail_open)

    ledger_record = record_decision_to_ledger(decision, inbox[0])

    assert ledger_record.record_status == "recorded_locally"
    assert ledger_record.execution_status == "not_executed"


def _default_inbox_and_decision() -> tuple[
    list[ApprovalInboxItem],
    OperatorDecisionRecord,
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
        rationale="Approved for local ledger-record test only.",
    )
    return inbox, decision
