from __future__ import annotations

import socket

from github_repo_steward import (
    FakeProposalProvider,
    analyze_repo_snapshot,
    load_default_fixture_snapshot,
    normalize_repo_snapshot,
)


def test_fake_provider_does_not_require_common_secret_env_vars(monkeypatch) -> None:
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

    snapshot, findings = _default_snapshot_and_findings()
    proposals = FakeProposalProvider().propose(snapshot, findings)

    assert len(proposals) == 4


def test_fake_provider_does_not_open_network_sockets(monkeypatch) -> None:
    def fail_socket(*args: object, **kwargs: object) -> socket.socket:
        raise AssertionError("Fake provider must not open network sockets.")

    monkeypatch.setattr(socket, "socket", fail_socket)

    snapshot, findings = _default_snapshot_and_findings()
    proposals = FakeProposalProvider().propose(snapshot, findings)

    assert len(proposals) == 4


def _default_snapshot_and_findings():
    raw = load_default_fixture_snapshot()
    snapshot = normalize_repo_snapshot(raw)
    findings = analyze_repo_snapshot(snapshot)
    return snapshot, findings
