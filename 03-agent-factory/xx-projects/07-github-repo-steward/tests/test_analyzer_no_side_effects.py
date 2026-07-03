from __future__ import annotations

import socket

from github_repo_steward import (
    analyze_repo_snapshot,
    load_default_fixture_snapshot,
    normalize_repo_snapshot,
)


def test_analyzer_does_not_require_common_secret_env_vars(monkeypatch) -> None:
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

    raw = load_default_fixture_snapshot()
    snapshot = normalize_repo_snapshot(raw)
    findings = analyze_repo_snapshot(snapshot)

    assert len(findings) == 4


def test_analyzer_does_not_open_network_sockets(monkeypatch) -> None:
    def fail_socket(*args: object, **kwargs: object) -> socket.socket:
        raise AssertionError("Analyzer must not open network sockets.")

    monkeypatch.setattr(socket, "socket", fail_socket)

    raw = load_default_fixture_snapshot()
    snapshot = normalize_repo_snapshot(raw)
    findings = analyze_repo_snapshot(snapshot)

    assert len(findings) == 4
