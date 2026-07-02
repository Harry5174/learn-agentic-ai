"""Load local fake GitHub-like repository snapshots from JSON fixtures."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from github_repo_steward.models import RepoSnapshotValidationError

REQUIRED_TOP_LEVEL_FIELDS = frozenset(
    {
        "repository",
        "labels",
        "issues",
        "pull_requests",
        "comments",
        "ci_statuses",
    }
)


@dataclass(frozen=True)
class RawRepoSnapshot:
    data: dict[str, Any]
    source_path: Path


def load_default_fixture_snapshot() -> RawRepoSnapshot:
    """Load the committed local fixture snapshot."""

    artifact_root = Path(__file__).resolve().parents[2]
    return load_fixture_snapshot(artifact_root / "fixtures" / "fake_repo_snapshot.json")


def load_fixture_snapshot(path: str | Path) -> RawRepoSnapshot:
    """Load and minimally validate a local JSON fixture snapshot."""

    source_path = Path(path)
    try:
        with source_path.open("r", encoding="utf-8") as fixture_file:
            data = json.load(fixture_file)
    except json.JSONDecodeError as exc:
        raise RepoSnapshotValidationError(
            f"Fixture snapshot is not valid JSON: {source_path}"
        ) from exc
    except OSError as exc:
        raise RepoSnapshotValidationError(
            f"Fixture snapshot could not be loaded: {source_path}"
        ) from exc

    if not isinstance(data, dict):
        raise RepoSnapshotValidationError("Fixture snapshot must be a JSON object.")

    missing_fields = sorted(REQUIRED_TOP_LEVEL_FIELDS.difference(data))
    if missing_fields:
        joined_fields = ", ".join(missing_fields)
        raise RepoSnapshotValidationError(
            f"Fixture snapshot missing required top-level field(s): {joined_fields}"
        )

    return RawRepoSnapshot(data=data, source_path=source_path)
