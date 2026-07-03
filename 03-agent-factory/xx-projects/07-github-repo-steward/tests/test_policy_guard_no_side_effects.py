from __future__ import annotations

import socket

from github_repo_steward import (
    FakeProposalProvider,
    analyze_repo_snapshot,
    evaluate_repo_proposals,
    load_default_fixture_snapshot,
    normalize_repo_snapshot,
)


def test_policy_guard_does_not_require_common_secret_env_vars(monkeypatch) -> None:
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

    raw = load_default_fixture_snapshot()
    snapshot = normalize_repo_snapshot(raw)
    findings = analyze_repo_snapshot(snapshot)
    proposals = FakeProposalProvider().propose(snapshot, findings)
    evaluations = evaluate_repo_proposals(proposals)

    assert len(evaluations) == 4
    assert {evaluation.verdict for evaluation in evaluations} == {
        "allowed_for_operator_review"
    }


def test_policy_guard_does_not_open_network_sockets(monkeypatch) -> None:
    def fail_socket(*args: object, **kwargs: object) -> socket.socket:
        raise AssertionError("Policy guard must not open network sockets.")

    monkeypatch.setattr(socket, "socket", fail_socket)

    raw = load_default_fixture_snapshot()
    snapshot = normalize_repo_snapshot(raw)
    findings = analyze_repo_snapshot(snapshot)
    proposals = FakeProposalProvider().propose(snapshot, findings)
    evaluations = evaluate_repo_proposals(proposals)

    assert len(evaluations) == 4
