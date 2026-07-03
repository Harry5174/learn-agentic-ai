from __future__ import annotations

from copy import deepcopy
from dataclasses import replace

from github_repo_steward import (
    analyze_repo_snapshot,
    load_default_fixture_snapshot,
    normalize_repo_snapshot,
)


def test_analyzer_output_is_deterministic_for_same_snapshot() -> None:
    raw = load_default_fixture_snapshot()
    snapshot = normalize_repo_snapshot(raw)

    first = analyze_repo_snapshot(snapshot)
    second = analyze_repo_snapshot(snapshot)

    assert first == second


def test_analyzer_output_order_is_stable_for_reordered_snapshot_records() -> None:
    raw = load_default_fixture_snapshot()
    snapshot = normalize_repo_snapshot(raw)
    reordered_snapshot = replace(
        snapshot,
        issues=tuple(reversed(snapshot.issues)),
        pull_requests=tuple(reversed(snapshot.pull_requests)),
        comments=tuple(reversed(snapshot.comments)),
        ci_statuses=tuple(reversed(snapshot.ci_statuses)),
    )

    assert analyze_repo_snapshot(reordered_snapshot) == analyze_repo_snapshot(snapshot)


def test_analyzer_does_not_mutate_normalized_snapshot() -> None:
    raw = load_default_fixture_snapshot()
    snapshot = normalize_repo_snapshot(raw)
    before = deepcopy(snapshot)

    analyze_repo_snapshot(snapshot)

    assert snapshot == before
