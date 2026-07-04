"""Map local raw GitHub-like fixtures into the canonical snapshot shape."""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from github_repo_steward.models import (
    GitHubReadAdapterError,
    GitHubReadAdapterResult,
)

REQUIRED_ENDPOINTS = (
    "repository",
    "labels",
    "issues",
    "pulls",
)
OPTIONAL_ENDPOINTS = (
    "issue_comments",
    "pull_reviews",
    "check_runs",
    "statuses",
)
ENDPOINT_FILENAMES = {
    "repository": "repository.json",
    "labels": "labels.json",
    "issues": "issues.json",
    "pulls": "pulls.json",
    "issue_comments": "issue_comments.json",
    "pull_reviews": "pull_reviews.json",
    "check_runs": "check_runs.json",
    "statuses": "statuses.json",
}
def load_github_api_fixture_payloads(
    fixture_dir: Path | str | None = None,
) -> dict[str, object]:
    """Load local raw GitHub-like endpoint fixtures from disk."""

    source_dir = _default_fixture_dir() if fixture_dir is None else Path(fixture_dir)
    payloads: dict[str, object] = {}

    for endpoint_name in REQUIRED_ENDPOINTS:
        payloads[endpoint_name] = _load_endpoint(source_dir, endpoint_name)

    for endpoint_name in OPTIONAL_ENDPOINTS:
        endpoint_path = source_dir / ENDPOINT_FILENAMES[endpoint_name]
        if endpoint_path.exists():
            payloads[endpoint_name] = _load_endpoint(source_dir, endpoint_name)
        else:
            payloads[endpoint_name] = []

    return payloads


def map_github_api_payloads_to_canonical_snapshot(
    payloads: dict[str, object],
) -> dict[str, object]:
    """Map raw endpoint-shaped fixture payloads to canonical snapshot data."""

    _require_payload_mapping(payloads)
    repository = _map_repository(payloads)
    labels = _map_labels(_required_list(payloads, "labels"))
    issues = _map_issues(_required_list(payloads, "issues"))
    pulls = _map_pulls(
        _required_list(payloads, "pulls"),
        _optional_list(payloads, "pull_reviews"),
        _optional_list(payloads, "check_runs"),
        _optional_list(payloads, "statuses"),
    )
    comments = _map_comments(
        _optional_list(payloads, "issue_comments"),
        _optional_list(payloads, "pull_reviews"),
    )
    ci_statuses = _map_ci_statuses(
        _optional_list(payloads, "check_runs"),
        _optional_list(payloads, "statuses"),
    )

    return {
        "repository": repository,
        "labels": labels,
        "issues": issues,
        "pull_requests": pulls,
        "comments": comments,
        "ci_statuses": ci_statuses,
    }


def load_default_github_api_fixture_snapshot() -> dict[str, object]:
    """Load default raw fixtures and return canonical snapshot data."""

    return map_github_api_payloads_to_canonical_snapshot(
        load_github_api_fixture_payloads()
    )


def adapt_github_api_payloads(
    payloads: dict[str, object],
) -> GitHubReadAdapterResult:
    """Return structured local adapter metadata and canonical snapshot data."""

    canonical_snapshot = map_github_api_payloads_to_canonical_snapshot(payloads)
    repository = _require_mapping(canonical_snapshot["repository"], "repository")
    owner = _require_str(repository, "owner", "repository")
    name = _require_str(repository, "name", "repository")

    return GitHubReadAdapterResult(
        source="local_github_like_fixture",
        repository_full_name=f"{owner}/{name}",
        canonical_snapshot=canonical_snapshot,
        raw_endpoint_names=tuple(sorted(payloads)),
        warnings=(),
        adapter_status="mapped_locally",
        github_status="not_called",
        network_status="not_used",
    )


def _default_fixture_dir() -> Path:
    artifact_root = Path(__file__).resolve().parents[2]
    return artifact_root / "fixtures" / "github_api"


def _load_endpoint(source_dir: Path, endpoint_name: str) -> object:
    endpoint_path = source_dir / ENDPOINT_FILENAMES[endpoint_name]
    try:
        with endpoint_path.open("r", encoding="utf-8") as endpoint_file:
            return json.load(endpoint_file)
    except json.JSONDecodeError as exc:
        raise GitHubReadAdapterError(
            f"Raw GitHub-like fixture is not valid JSON: {endpoint_name}"
        ) from exc
    except OSError as exc:
        raise GitHubReadAdapterError(
            f"Raw GitHub-like fixture could not be loaded: {endpoint_name}"
        ) from exc


def _map_repository(payloads: Mapping[str, object]) -> dict[str, object]:
    repository = _required_mapping(payloads, "repository")
    owner = _required_mapping(repository, "owner")
    full_name = _require_str(repository, "full_name", "repository")
    owner_login = _require_str(owner, "login", "repository.owner")
    name = _require_str(repository, "name", "repository")
    default_branch = _require_str(
        repository,
        "default_branch",
        "repository",
    )
    snapshot_generated_at = _require_str(
        repository,
        "snapshot_generated_at",
        "repository",
    )
    if full_name != f"{owner_login}/{name}":
        raise GitHubReadAdapterError(
            "repository.full_name must match owner.login and name."
        )
    return {
        "owner": owner_login,
        "name": name,
        "default_branch": default_branch,
        "snapshot_generated_at": snapshot_generated_at,
    }


def _map_labels(labels_payload: list[object]) -> list[dict[str, object]]:
    labels = []
    for index, value in enumerate(labels_payload):
        context = f"labels[{index}]"
        label = _require_mapping(value, context)
        labels.append(
            {
                "name": _require_str(label, "name", context),
                "description": _require_str(label, "description", context),
                "color": _optional_str(label, "color", context),
            }
        )
    return sorted(labels, key=lambda label: str(label["name"]))


def _map_issues(issues_payload: list[object]) -> list[dict[str, object]]:
    issues = []
    for index, value in enumerate(issues_payload):
        context = f"issues[{index}]"
        issue = _require_mapping(value, context)
        if "pull_request" in issue:
            continue
        issues.append(
            {
                "id": _require_int(issue, "id", context),
                "number": _require_int(issue, "number", context),
                "title": _require_str(issue, "title", context),
                "body": _require_str(issue, "body", context),
                "state": _require_str(issue, "state", context),
                "labels": _label_names(issue.get("labels", []), context),
                "author": _login_from_user(issue, context),
                "created_at": _require_str(issue, "created_at", context),
                "updated_at": _require_str(issue, "updated_at", context),
                "comments_count": _require_int(issue, "comments", context),
                "stale_days": _require_int(issue, "adapter_stale_days", context),
            }
        )
    return sorted(issues, key=lambda issue: int(issue["number"]))


def _map_pulls(
    pulls_payload: list[object],
    reviews_payload: list[object],
    check_runs_payload: list[object],
    statuses_payload: list[object],
) -> list[dict[str, object]]:
    review_status_by_number = _review_status_by_number(reviews_payload)
    ci_status_by_number = _ci_status_by_number(
        check_runs_payload,
        statuses_payload,
    )
    pulls = []
    for index, value in enumerate(pulls_payload):
        context = f"pulls[{index}]"
        pull = _require_mapping(value, context)
        number = _require_int(pull, "number", context)
        head = _required_mapping(pull, "head")
        base = _required_mapping(pull, "base")
        pulls.append(
            {
                "id": _require_int(pull, "id", context),
                "number": number,
                "title": _require_str(pull, "title", context),
                "body": _require_str(pull, "body", context),
                "state": _require_str(pull, "state", context),
                "labels": _label_names(pull.get("labels", []), context),
                "author": _login_from_user(pull, context),
                "created_at": _require_str(pull, "created_at", context),
                "updated_at": _require_str(pull, "updated_at", context),
                "branch": _require_str(head, "ref", f"{context}.head"),
                "base_branch": _require_str(base, "ref", f"{context}.base"),
                "review_status": review_status_by_number.get(
                    number,
                    "waiting_for_review",
                ),
                "ci_status": ci_status_by_number.get(number, "unknown"),
                "stale_days": _require_int(pull, "adapter_stale_days", context),
            }
        )
    return sorted(pulls, key=lambda pull: int(pull["number"]))


def _map_comments(
    issue_comments_payload: list[object],
    reviews_payload: list[object],
) -> list[dict[str, object]]:
    comments = []
    for index, value in enumerate(issue_comments_payload):
        context = f"issue_comments[{index}]"
        comment = _require_mapping(value, context)
        comments.append(
            {
                "id": _require_int(comment, "id", context),
                "target_type": "issue",
                "target_number": _require_int(comment, "issue_number", context),
                "author": _login_from_user(comment, context),
                "body": _require_str(comment, "body", context),
                "created_at": _require_str(comment, "created_at", context),
            }
        )
    for index, value in enumerate(reviews_payload):
        context = f"pull_reviews[{index}]"
        review = _require_mapping(value, context)
        body = _require_str(review, "body", context)
        if not body:
            continue
        comments.append(
            {
                "id": _require_int(review, "id", context),
                "target_type": "pull_request",
                "target_number": _require_int(
                    review,
                    "pull_request_number",
                    context,
                ),
                "author": _login_from_user(review, context),
                "body": body,
                "created_at": _require_str(review, "submitted_at", context),
            }
        )
    return sorted(
        comments,
        key=lambda comment: (
            str(comment["target_type"]),
            int(comment["target_number"]),
            int(comment["id"]),
        ),
    )


def _map_ci_statuses(
    check_runs_payload: list[object],
    statuses_payload: list[object],
) -> list[dict[str, object]]:
    status_by_number = _best_status_record_by_number(
        check_runs_payload,
        statuses_payload,
    )
    ci_statuses = []
    for target_number, status_record in sorted(status_by_number.items()):
        ci_statuses.append(
            {
                "target_type": "pull_request",
                "target_number": target_number,
                "status": status_record["status"],
                "conclusion": status_record["conclusion"],
                "updated_at": status_record["updated_at"],
            }
        )
    return ci_statuses


def _review_status_by_number(reviews_payload: list[object]) -> dict[int, str]:
    statuses: dict[int, str] = {}
    for index, value in enumerate(reviews_payload):
        context = f"pull_reviews[{index}]"
        review = _require_mapping(value, context)
        number = _require_int(review, "pull_request_number", context)
        state = _require_str(review, "state", context).upper()
        if state == "APPROVED":
            statuses[number] = "approved"
        elif number not in statuses and state in {"COMMENTED", "CHANGES_REQUESTED"}:
            statuses[number] = "changes_requested"
    return statuses


def _ci_status_by_number(
    check_runs_payload: list[object],
    statuses_payload: list[object],
) -> dict[int, str]:
    status_by_number = _best_status_record_by_number(
        check_runs_payload,
        statuses_payload,
    )
    ci_statuses: dict[int, str] = {}
    for number, status_record in status_by_number.items():
        conclusion = status_record["conclusion"]
        ci_statuses[number] = "passing" if conclusion == "success" else "failing"
    return ci_statuses


def _best_status_record_by_number(
    check_runs_payload: list[object],
    statuses_payload: list[object],
) -> dict[int, dict[str, str]]:
    records: dict[int, dict[str, str]] = {}
    for index, value in enumerate(statuses_payload):
        context = f"statuses[{index}]"
        status = _require_mapping(value, context)
        number = _require_int(status, "pull_request_number", context)
        state = _require_str(status, "state", context)
        records[number] = {
            "status": "completed",
            "conclusion": "success" if state == "success" else "failure",
            "updated_at": _require_str(status, "updated_at", context),
        }
    for index, value in enumerate(check_runs_payload):
        context = f"check_runs[{index}]"
        check_run = _require_mapping(value, context)
        number = _require_int(check_run, "pull_request_number", context)
        records[number] = {
            "status": _require_str(check_run, "status", context),
            "conclusion": _require_str(check_run, "conclusion", context),
            "updated_at": _require_str(check_run, "completed_at", context),
        }
    return records


def _label_names(value: object, context: str) -> list[str]:
    if not isinstance(value, list):
        raise GitHubReadAdapterError(f"{context}.labels must be a list.")
    labels = []
    for index, item in enumerate(value):
        label = _require_mapping(item, f"{context}.labels[{index}]")
        labels.append(_require_str(label, "name", f"{context}.labels[{index}]"))
    return sorted(labels)


def _login_from_user(record: Mapping[str, object], context: str) -> str:
    user = _required_mapping(record, "user")
    return _require_str(user, "login", f"{context}.user")


def _require_payload_mapping(payloads: object) -> None:
    if not isinstance(payloads, dict):
        raise GitHubReadAdapterError("GitHub-like payloads must be a dict.")
    missing = sorted(set(REQUIRED_ENDPOINTS).difference(payloads))
    if missing:
        joined = ", ".join(missing)
        raise GitHubReadAdapterError(
            f"Missing required GitHub-like payload(s): {joined}"
        )


def _required_mapping(
    payloads: Mapping[str, object],
    endpoint_name: str,
) -> Mapping[str, object]:
    value = payloads.get(endpoint_name)
    if not isinstance(value, Mapping):
        raise GitHubReadAdapterError(f"{endpoint_name} must be an object.")
    return value


def _required_list(
    payloads: Mapping[str, object],
    endpoint_name: str,
) -> list[object]:
    value = payloads.get(endpoint_name)
    if not isinstance(value, list):
        raise GitHubReadAdapterError(f"{endpoint_name} must be a list.")
    return value


def _optional_list(
    payloads: Mapping[str, object],
    endpoint_name: str,
) -> list[object]:
    value = payloads.get(endpoint_name, [])
    if not isinstance(value, list):
        raise GitHubReadAdapterError(f"{endpoint_name} must be a list.")
    return value


def _require_mapping(value: object, context: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise GitHubReadAdapterError(f"{context} must be an object.")
    return value


def _require_str(
    record: Mapping[str, object],
    field_name: str,
    context: str,
) -> str:
    value = record.get(field_name)
    if not isinstance(value, str):
        raise GitHubReadAdapterError(f"{context}.{field_name} must be a string.")
    return value


def _optional_str(
    record: Mapping[str, object],
    field_name: str,
    context: str,
) -> str | None:
    value = record.get(field_name)
    if value is not None and not isinstance(value, str):
        raise GitHubReadAdapterError(
            f"{context}.{field_name} must be a string or null."
        )
    return value


def _require_int(
    record: Mapping[str, object],
    field_name: str,
    context: str,
) -> int:
    value = record.get(field_name)
    if not isinstance(value, int) or isinstance(value, bool):
        raise GitHubReadAdapterError(
            f"{context}.{field_name} must be an integer."
        )
    return value
