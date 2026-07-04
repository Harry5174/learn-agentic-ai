from __future__ import annotations

from copy import deepcopy

from github_repo_steward import (
    load_github_api_fixture_payloads,
    map_github_api_payloads_to_canonical_snapshot,
)


def test_adapter_output_is_deterministic() -> None:
    payloads = load_github_api_fixture_payloads()

    first = map_github_api_payloads_to_canonical_snapshot(payloads)
    second = map_github_api_payloads_to_canonical_snapshot(payloads)

    assert second == first


def test_adapter_output_order_is_stable_for_reordered_payload_lists() -> None:
    payloads = load_github_api_fixture_payloads()
    reordered = deepcopy(payloads)
    for endpoint_name in (
        "labels",
        "issues",
        "pulls",
        "issue_comments",
        "pull_reviews",
        "check_runs",
        "statuses",
    ):
        reordered[endpoint_name] = list(reversed(reordered[endpoint_name]))  # type: ignore[arg-type]

    canonical = map_github_api_payloads_to_canonical_snapshot(payloads)
    reordered_canonical = map_github_api_payloads_to_canonical_snapshot(reordered)

    assert reordered_canonical == canonical
    assert [issue["number"] for issue in canonical["issues"]] == [11, 12]
    assert [pull["number"] for pull in canonical["pull_requests"]] == [21, 22]
    assert [label["name"] for label in canonical["labels"]] == [
        "bug",
        "enhancement",
        "needs-info",
        "stale",
    ]


def test_adapter_does_not_mutate_raw_payloads() -> None:
    payloads = load_github_api_fixture_payloads()
    before = deepcopy(payloads)

    map_github_api_payloads_to_canonical_snapshot(payloads)

    assert payloads == before
