from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass


ARTIFACT_04_MARKER_TEMPLATE = (
    "<!-- agent_factory:v1 side_effect_id={side_effect_id} "
    "args_hash={validated_arguments_hash} -->"
)
DEFAULT_TOKEN_ENV_NAME = "AGENT_FACTORY_GITHUB_TOKEN"
VALID_MODES = frozenset({"fake", "real", "docs"})
VALID_FRESH_SIDE_EFFECT_MODES = frozenset(
    {"fresh_issue", "new_unique_body", "explicit_reconciliation"}
)
NETWORK_CALLS_ATTEMPTED = 0
REDACTED_TOKEN_VALUE = "REDACTED"


@dataclass(frozen=True)
class PreflightRequest:
    mode: str
    repository: str
    issue_number: int
    allowed_repositories: Sequence[str]
    allowed_issues: Sequence[int]
    fresh_side_effect_mode: str | None
    real_mode_explicit: bool = False
    token_env_name: str = DEFAULT_TOKEN_ENV_NAME
    marker_template: str = ARTIFACT_04_MARKER_TEMPLATE


@dataclass(frozen=True)
class PreflightResult:
    preflight_status: str
    mode: str
    real_mode_explicit: bool
    ci_block_active: bool
    token_env_name: str
    token_present: bool
    allowlisted_repo: bool
    allowlisted_issue: bool
    fresh_side_effect_mode: str | None
    marker_format_verified: bool
    network_calls_attempted: int
    failure_reason: str | None = None

    def to_redacted_dict(self) -> dict[str, object]:
        result: dict[str, object] = {
            "preflight_status": self.preflight_status,
            "mode": self.mode,
            "real_mode_explicit": self.real_mode_explicit,
            "ci_block_active": self.ci_block_active,
            "token_env_name": self.token_env_name,
            "token_present": self.token_present,
            "allowlisted_repo": self.allowlisted_repo,
            "allowlisted_issue": self.allowlisted_issue,
            "fresh_side_effect_mode": self.fresh_side_effect_mode,
            "marker_format_verified": self.marker_format_verified,
            "network_calls_attempted": self.network_calls_attempted,
        }
        if self.token_present:
            result["token_value"] = REDACTED_TOKEN_VALUE
        if self.failure_reason is not None:
            result["failure_reason"] = self.failure_reason
        return result


def run_preflight(
    request: PreflightRequest,
    *,
    environ: Mapping[str, str],
) -> PreflightResult:
    token_present = _token_present(environ, request.token_env_name)
    ci_block_active = _truthy(environ.get("CI"))
    allowlisted_repo = request.repository in set(request.allowed_repositories)
    allowlisted_issue = request.issue_number in set(request.allowed_issues)
    marker_format_verified = request.marker_template == ARTIFACT_04_MARKER_TEMPLATE

    failure_reason = _failure_reason(
        request=request,
        token_present=token_present,
        ci_block_active=ci_block_active,
        allowlisted_repo=allowlisted_repo,
        allowlisted_issue=allowlisted_issue,
        marker_format_verified=marker_format_verified,
    )

    return PreflightResult(
        preflight_status="failed" if failure_reason else "passed",
        mode=request.mode,
        real_mode_explicit=request.real_mode_explicit,
        ci_block_active=ci_block_active,
        token_env_name=request.token_env_name,
        token_present=token_present,
        allowlisted_repo=allowlisted_repo,
        allowlisted_issue=allowlisted_issue,
        fresh_side_effect_mode=request.fresh_side_effect_mode,
        marker_format_verified=marker_format_verified,
        network_calls_attempted=NETWORK_CALLS_ATTEMPTED,
        failure_reason=failure_reason,
    )


def serialize_preflight_result(result: PreflightResult) -> str:
    return json.dumps(result.to_redacted_dict(), indent=2, sort_keys=True)


def build_expected_marker(*, side_effect_id: str, validated_arguments_hash: str) -> str:
    return ARTIFACT_04_MARKER_TEMPLATE.format(
        side_effect_id=_required_text(side_effect_id, "side_effect_id"),
        validated_arguments_hash=_required_text(
            validated_arguments_hash,
            "validated_arguments_hash",
        ),
    )


def _failure_reason(
    *,
    request: PreflightRequest,
    token_present: bool,
    ci_block_active: bool,
    allowlisted_repo: bool,
    allowlisted_issue: bool,
    marker_format_verified: bool,
) -> str | None:
    if request.mode not in VALID_MODES:
        return "unsupported_mode"
    if request.fresh_side_effect_mode is None:
        return "fresh_side_effect_mode_required"
    if request.fresh_side_effect_mode not in VALID_FRESH_SIDE_EFFECT_MODES:
        return "invalid_fresh_side_effect_mode"
    if not marker_format_verified:
        return "marker_format_not_verified"
    if request.mode in {"fake", "docs"}:
        return None
    if not request.real_mode_explicit:
        return "real_mode_explicit_opt_in_required"
    if ci_block_active:
        return "real_mode_preflight_blocked_in_ci"
    if not allowlisted_repo:
        return "repository_not_allowlisted"
    if not allowlisted_issue:
        return "issue_not_allowlisted"
    if not token_present:
        return "missing_token"
    return None


def _token_present(environ: Mapping[str, str], token_env_name: str) -> bool:
    return environ.get(token_env_name, "").strip() != ""


def _truthy(value: str | None) -> bool:
    return value is not None and value.strip().lower() in {"1", "true", "yes", "on"}


def _required_text(value: str, field_name: str) -> str:
    if not isinstance(value, str) or value.strip() == "":
        raise ValueError(f"{field_name} must be a non-empty string")
    return value.strip()
