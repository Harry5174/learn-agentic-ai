from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

import pytest

from app.github.remote_marker import build_remote_idempotency_marker


HELPER_PATH = Path(__file__).resolve().parents[1] / "tools" / "preflight_gate.py"
ALLOWED_REPOSITORY = "Harry5174/artifact-5-github-comment-test"
ALLOWED_ISSUE = 1
DUMMY_TOKEN = "dummy-token-value-that-must-not-appear"


def load_helper() -> ModuleType:
    spec = importlib.util.spec_from_file_location("a5_preflight_gate", HELPER_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


preflight_gate = load_helper()


def preflight_request(**overrides):  # noqa: ANN003, ANN201
    values = {
        "mode": "real",
        "repository": ALLOWED_REPOSITORY,
        "issue_number": ALLOWED_ISSUE,
        "allowed_repositories": (ALLOWED_REPOSITORY,),
        "allowed_issues": (ALLOWED_ISSUE,),
        "fresh_side_effect_mode": "fresh_issue",
        "real_mode_explicit": True,
    }
    values.update(overrides)
    return preflight_gate.PreflightRequest(**values)


def run_request(request, environ=None):  # noqa: ANN001, ANN201
    return preflight_gate.run_preflight(request, environ=environ or {})


def serialized(result) -> str:  # noqa: ANN001
    return preflight_gate.serialize_preflight_result(result)


def test_fake_mode_passes_without_token() -> None:
    result = run_request(
        preflight_request(mode="fake", real_mode_explicit=False),
        environ={},
    )

    assert result.preflight_status == "passed"
    assert result.token_present is False
    assert result.network_calls_attempted == 0


def test_real_mode_fails_without_explicit_opt_in() -> None:
    result = run_request(
        preflight_request(real_mode_explicit=False),
        environ={preflight_gate.DEFAULT_TOKEN_ENV_NAME: DUMMY_TOKEN},
    )

    assert result.preflight_status == "failed"
    assert result.failure_reason == "real_mode_explicit_opt_in_required"
    assert result.network_calls_attempted == 0


def test_real_mode_fails_in_ci() -> None:
    result = run_request(
        preflight_request(),
        environ={
            "CI": "true",
            preflight_gate.DEFAULT_TOKEN_ENV_NAME: DUMMY_TOKEN,
        },
    )

    assert result.preflight_status == "failed"
    assert result.ci_block_active is True
    assert result.failure_reason == "real_mode_preflight_blocked_in_ci"
    assert result.network_calls_attempted == 0


@pytest.mark.parametrize("mode", ["fake", "docs"])
def test_ci_fake_and_docs_validation_are_allowed(mode: str) -> None:
    result = run_request(
        preflight_request(mode=mode, real_mode_explicit=False),
        environ={"CI": "true"},
    )

    assert result.preflight_status == "passed"
    assert result.ci_block_active is True
    assert result.network_calls_attempted == 0


def test_real_mode_reports_token_present_without_exposing_value() -> None:
    result = run_request(
        preflight_request(),
        environ={preflight_gate.DEFAULT_TOKEN_ENV_NAME: DUMMY_TOKEN},
    )
    payload = result.to_redacted_dict()
    output = serialized(result)

    assert result.preflight_status == "passed"
    assert payload["token_env_name"] == "AGENT_FACTORY_GITHUB_TOKEN"
    assert payload["token_present"] is True
    assert payload["token_value"] == "REDACTED"
    assert DUMMY_TOKEN not in output


def test_missing_token_fails_safely_for_real_preflight() -> None:
    result = run_request(preflight_request(), environ={})

    assert result.preflight_status == "failed"
    assert result.failure_reason == "missing_token"
    assert result.token_present is False
    assert "token_value" not in result.to_redacted_dict()
    assert result.network_calls_attempted == 0


def test_allowlisted_repo_and_issue_pass() -> None:
    result = run_request(
        preflight_request(),
        environ={preflight_gate.DEFAULT_TOKEN_ENV_NAME: DUMMY_TOKEN},
    )

    assert result.preflight_status == "passed"
    assert result.allowlisted_repo is True
    assert result.allowlisted_issue is True


def test_non_allowlisted_repo_fails_before_network() -> None:
    result = run_request(
        preflight_request(repository="Harry5174/not-allowed"),
        environ={preflight_gate.DEFAULT_TOKEN_ENV_NAME: DUMMY_TOKEN},
    )

    assert result.preflight_status == "failed"
    assert result.failure_reason == "repository_not_allowlisted"
    assert result.network_calls_attempted == 0


def test_non_allowlisted_issue_fails_before_network() -> None:
    result = run_request(
        preflight_request(issue_number=2),
        environ={preflight_gate.DEFAULT_TOKEN_ENV_NAME: DUMMY_TOKEN},
    )

    assert result.preflight_status == "failed"
    assert result.failure_reason == "issue_not_allowlisted"
    assert result.network_calls_attempted == 0


@pytest.mark.parametrize(
    "preflight_case",
    [
        preflight_request(mode="fake", real_mode_explicit=False),
        preflight_request(real_mode_explicit=False),
        preflight_request(),
        preflight_request(repository="Harry5174/not-allowed"),
        preflight_request(issue_number=2),
        preflight_request(fresh_side_effect_mode=None),
        preflight_request(fresh_side_effect_mode="unsafe"),
    ],
)
def test_network_calls_attempted_remains_zero_in_all_preflight_paths(
    preflight_case,  # noqa: ANN001
) -> None:
    result = run_request(
        preflight_case,
        environ={preflight_gate.DEFAULT_TOKEN_ENV_NAME: DUMMY_TOKEN},
    )

    assert result.network_calls_attempted == 0


def test_fresh_side_effect_mode_is_required() -> None:
    result = run_request(
        preflight_request(fresh_side_effect_mode=None),
        environ={preflight_gate.DEFAULT_TOKEN_ENV_NAME: DUMMY_TOKEN},
    )

    assert result.preflight_status == "failed"
    assert result.failure_reason == "fresh_side_effect_mode_required"


def test_invalid_fresh_side_effect_mode_fails() -> None:
    result = run_request(
        preflight_request(fresh_side_effect_mode="reuse_existing_marker"),
        environ={preflight_gate.DEFAULT_TOKEN_ENV_NAME: DUMMY_TOKEN},
    )

    assert result.preflight_status == "failed"
    assert result.failure_reason == "invalid_fresh_side_effect_mode"


def test_marker_format_matches_artifact_04_backed_builder() -> None:
    side_effect_id = "side-effect-123"
    args_hash = "args-hash-456"

    helper_marker = preflight_gate.build_expected_marker(
        side_effect_id=side_effect_id,
        validated_arguments_hash=args_hash,
    )
    artifact_04_marker = build_remote_idempotency_marker(
        side_effect_id=side_effect_id,
        validated_arguments_hash=args_hash,
    )

    assert helper_marker == artifact_04_marker
    assert helper_marker == (
        "<!-- agent_factory:v1 side_effect_id=side-effect-123 "
        "args_hash=args-hash-456 -->"
    )


def test_preflight_report_never_includes_token_authorization_or_env_contents() -> None:
    result = run_request(
        preflight_request(),
        environ={
            preflight_gate.DEFAULT_TOKEN_ENV_NAME: DUMMY_TOKEN,
            "CI": "false",
        },
    )
    output = serialized(result)

    assert DUMMY_TOKEN not in output
    assert "Authorization" not in output
    assert "Bearer" not in output
    assert ".env" not in output
