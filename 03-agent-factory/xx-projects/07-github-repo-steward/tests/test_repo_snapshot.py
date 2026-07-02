from __future__ import annotations

import json

import pytest

from github_repo_steward import (
    RepoSnapshotValidationError,
    load_default_fixture_snapshot,
    load_fixture_snapshot,
)


def test_default_fake_fixture_loads_successfully() -> None:
    raw = load_default_fixture_snapshot()

    assert raw.source_path.name == "fake_repo_snapshot.json"
    assert raw.data["repository"]["owner"] == "fixture-owner"
    assert len(raw.data["issues"]) == 3
    assert len(raw.data["pull_requests"]) == 2


def test_missing_required_top_level_field_fails_safely(tmp_path) -> None:
    fixture_path = tmp_path / "missing-issues.json"
    fixture_path.write_text(
        json.dumps(
            {
                "repository": {},
                "labels": [],
                "pull_requests": [],
                "comments": [],
                "ci_statuses": [],
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(RepoSnapshotValidationError, match="issues"):
        load_fixture_snapshot(fixture_path)


def test_non_object_fixture_fails_safely(tmp_path) -> None:
    fixture_path = tmp_path / "list.json"
    fixture_path.write_text("[]", encoding="utf-8")

    with pytest.raises(RepoSnapshotValidationError, match="JSON object"):
        load_fixture_snapshot(fixture_path)
