"""Normalize local fixture snapshots into typed internal records."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

from github_repo_steward.models import (
    CiStatusSummary,
    CommentRecord,
    IssueRecord,
    LabelRecord,
    NormalizedRepoSnapshot,
    PullRequestRecord,
    RepositoryIdentity,
    RepoSnapshotValidationError,
)
from github_repo_steward.repo_snapshot import RawRepoSnapshot

REPOSITORY_FIELDS = frozenset(
    {"owner", "name", "default_branch", "snapshot_generated_at"}
)
ISSUE_FIELDS = frozenset(
    {
        "id",
        "number",
        "title",
        "body",
        "state",
        "labels",
        "author",
        "created_at",
        "updated_at",
        "comments_count",
        "stale_days",
    }
)
PULL_REQUEST_FIELDS = frozenset(
    {
        "id",
        "number",
        "title",
        "body",
        "state",
        "labels",
        "author",
        "created_at",
        "updated_at",
        "branch",
        "base_branch",
        "review_status",
        "ci_status",
        "stale_days",
    }
)
LABEL_FIELDS = frozenset({"name", "description"})
COMMENT_FIELDS = frozenset(
    {"id", "target_type", "target_number", "author", "body", "created_at"}
)
CI_STATUS_FIELDS = frozenset(
    {"target_type", "target_number", "status", "conclusion", "updated_at"}
)


def normalize_repo_snapshot(raw: RawRepoSnapshot) -> NormalizedRepoSnapshot:
    """Convert raw local fixture data into typed normalized records."""

    data = raw.data
    repository = _normalize_repository(data["repository"])
    labels = tuple(
        _normalize_label(item, index) for index, item in enumerate(data["labels"])
    )
    issues = tuple(
        _normalize_issue(item, index) for index, item in enumerate(data["issues"])
    )
    pull_requests = tuple(
        _normalize_pull_request(item, index)
        for index, item in enumerate(data["pull_requests"])
    )
    comments = tuple(
        _normalize_comment(item, index) for index, item in enumerate(data["comments"])
    )
    ci_statuses = tuple(
        _normalize_ci_status(item, index)
        for index, item in enumerate(data["ci_statuses"])
    )

    return NormalizedRepoSnapshot(
        repository=repository,
        labels=labels,
        issues=issues,
        pull_requests=pull_requests,
        comments=comments,
        ci_statuses=ci_statuses,
    )


def _normalize_repository(value: Any) -> RepositoryIdentity:
    record = _require_mapping(value, "repository")
    _require_fields(record, REPOSITORY_FIELDS, "repository")
    return RepositoryIdentity(
        owner=_require_str(record, "owner", "repository"),
        name=_require_str(record, "name", "repository"),
        default_branch=_require_str(record, "default_branch", "repository"),
        snapshot_generated_at=_require_str(
            record, "snapshot_generated_at", "repository"
        ),
    )


def _normalize_label(value: Any, index: int) -> LabelRecord:
    context = f"labels[{index}]"
    record = _require_mapping(value, context)
    _require_fields(record, LABEL_FIELDS, context)
    color = record.get("color")
    if color is not None and not isinstance(color, str):
        raise RepoSnapshotValidationError(f"{context}.color must be a string or null.")
    return LabelRecord(
        name=_require_str(record, "name", context),
        description=_require_str(record, "description", context),
        color=color,
    )


def _normalize_issue(value: Any, index: int) -> IssueRecord:
    context = f"issues[{index}]"
    record = _require_mapping(value, context)
    _require_fields(record, ISSUE_FIELDS, context)
    return IssueRecord(
        id=_require_int(record, "id", context),
        number=_require_int(record, "number", context),
        title=_require_str(record, "title", context),
        body=_require_str(record, "body", context),
        state=_require_str(record, "state", context),
        labels=_normalize_labels(record["labels"], context),
        author=_require_str(record, "author", context),
        created_at=_require_str(record, "created_at", context),
        updated_at=_require_str(record, "updated_at", context),
        comments_count=_require_int(record, "comments_count", context),
        stale_days=_require_int(record, "stale_days", context),
    )


def _normalize_pull_request(value: Any, index: int) -> PullRequestRecord:
    context = f"pull_requests[{index}]"
    record = _require_mapping(value, context)
    _require_fields(record, PULL_REQUEST_FIELDS, context)
    return PullRequestRecord(
        id=_require_int(record, "id", context),
        number=_require_int(record, "number", context),
        title=_require_str(record, "title", context),
        body=_require_str(record, "body", context),
        state=_require_str(record, "state", context),
        labels=_normalize_labels(record["labels"], context),
        author=_require_str(record, "author", context),
        created_at=_require_str(record, "created_at", context),
        updated_at=_require_str(record, "updated_at", context),
        branch=_require_str(record, "branch", context),
        base_branch=_require_str(record, "base_branch", context),
        review_status=_require_str(record, "review_status", context),
        ci_status=_require_str(record, "ci_status", context),
        stale_days=_require_int(record, "stale_days", context),
    )


def _normalize_comment(value: Any, index: int) -> CommentRecord:
    context = f"comments[{index}]"
    record = _require_mapping(value, context)
    _require_fields(record, COMMENT_FIELDS, context)
    return CommentRecord(
        id=_require_int(record, "id", context),
        target_type=_require_str(record, "target_type", context),
        target_number=_require_int(record, "target_number", context),
        author=_require_str(record, "author", context),
        body=_require_str(record, "body", context),
        created_at=_require_str(record, "created_at", context),
    )


def _normalize_ci_status(value: Any, index: int) -> CiStatusSummary:
    context = f"ci_statuses[{index}]"
    record = _require_mapping(value, context)
    _require_fields(record, CI_STATUS_FIELDS, context)
    return CiStatusSummary(
        target_type=_require_str(record, "target_type", context),
        target_number=_require_int(record, "target_number", context),
        status=_require_str(record, "status", context),
        conclusion=_require_str(record, "conclusion", context),
        updated_at=_require_str(record, "updated_at", context),
    )


def _normalize_labels(value: Any, context: str) -> tuple[str, ...]:
    if not isinstance(value, Iterable) or isinstance(value, str | bytes):
        raise RepoSnapshotValidationError(
            f"{context}.labels must be a list of strings."
        )
    labels = []
    for index, label in enumerate(value):
        if not isinstance(label, str):
            raise RepoSnapshotValidationError(
                f"{context}.labels[{index}] must be a string."
            )
        labels.append(label)
    return tuple(labels)


def _require_mapping(value: Any, context: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise RepoSnapshotValidationError(f"{context} must be an object.")
    return value


def _require_fields(
    record: Mapping[str, Any], required_fields: frozenset[str], context: str
) -> None:
    missing_fields = sorted(required_fields.difference(record))
    if missing_fields:
        joined_fields = ", ".join(missing_fields)
        raise RepoSnapshotValidationError(
            f"{context} missing required field(s): {joined_fields}"
        )


def _require_str(record: Mapping[str, Any], field_name: str, context: str) -> str:
    value = record[field_name]
    if not isinstance(value, str):
        raise RepoSnapshotValidationError(f"{context}.{field_name} must be a string.")
    return value


def _require_int(record: Mapping[str, Any], field_name: str, context: str) -> int:
    value = record[field_name]
    if not isinstance(value, int) or isinstance(value, bool):
        raise RepoSnapshotValidationError(f"{context}.{field_name} must be an integer.")
    return value
