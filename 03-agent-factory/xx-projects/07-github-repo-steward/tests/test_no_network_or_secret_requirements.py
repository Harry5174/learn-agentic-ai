from __future__ import annotations

from github_repo_steward import load_default_fixture_snapshot, normalize_repo_snapshot


def test_loader_and_normalizer_do_not_require_common_secret_env_vars(
    monkeypatch,
) -> None:
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

    raw = load_default_fixture_snapshot()
    snapshot = normalize_repo_snapshot(raw)

    assert snapshot.repository.owner == "fixture-owner"
    assert len(snapshot.issues) == 3
    assert len(snapshot.pull_requests) == 2
