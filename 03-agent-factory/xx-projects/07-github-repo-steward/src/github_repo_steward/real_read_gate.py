"""Deterministic local evidence gate for optional real-read mode."""

from __future__ import annotations

from github_repo_steward.models import (
    RealReadEvidenceRecord,
    RealReadGateError,
    RealReadGateEvaluation,
    RealReadRequest,
)

FAKE_DEFAULT = "fake_default"
REAL_READ_REQUESTED = "real_read_requested"
FAKE_DEFAULT_ALLOWED = "fake_default_allowed"
REAL_READ_BLOCKED = "real_read_blocked"
REAL_READ_PREFLIGHT_ALLOWED = "real_read_preflight_allowed"
NOT_CALLED = "not_called"
READ_ONLY_PREFLIGHT_ONLY = "read_only_preflight_only"
NOT_USED = "not_used"
BLOCKED = "blocked"
PREFLIGHT_ALLOWED = "preflight_allowed"
WRITES_FORBIDDEN = "writes_forbidden"
NOT_REQUIRED_FOR_FAKE_DEFAULT = "not_required_for_fake_default"
CREDENTIALS_NOT_INSPECTED = "credentials_not_inspected"
CREDENTIAL_HANDLING_REQUIRED = "credential_handling_required"

SAFE_REAL_READ_CREDENTIAL_SOURCES = frozenset(
    {
        "server_side_environment_reference",
        "product_owner_managed_read_token",
        "approved_secret_manager_reference",
    }
)


def evaluate_fake_default_real_read_gate() -> RealReadGateEvaluation:
    """Evaluate the default local/fake mode gate request."""

    return evaluate_real_read_request(
        RealReadRequest(
            mode=FAKE_DEFAULT,
            repository_full_name="local/fake-default",
            requested_by="local-operator",
            product_owner_authorized=False,
            authorization_reference="not-authorized-fake-default",
            credential_source="none",
            adapter_required=True,
            write_operations_allowed=False,
            network_access_requested=False,
            evidence_expected=("fake-default-adapter-path",),
        )
    )


def evaluate_real_read_request(
    request: RealReadRequest,
) -> RealReadGateEvaluation:
    """Evaluate a local real-read gate request without calling GitHub."""

    _require_request(request)

    if request.mode == FAKE_DEFAULT:
        return _evaluate_fake_default(request)
    return _evaluate_real_read_requested(request)


def build_real_read_evidence_record(
    evaluation: RealReadGateEvaluation,
    adapter_boundary_status: str,
    raw_payload_status: str,
    canonical_snapshot_status: str,
    normalization_status: str,
    pipeline_status: str,
    summary: str = "",
) -> RealReadEvidenceRecord:
    """Build a deterministic local evidence record for a gate evaluation."""

    _require_evaluation(evaluation)
    evidence_id = ":".join(
        (
            "a7v",
            evaluation.evaluation_id,
            adapter_boundary_status,
            raw_payload_status,
            canonical_snapshot_status,
            normalization_status,
            pipeline_status,
        )
    )

    return RealReadEvidenceRecord(
        evidence_id=evidence_id,
        evaluation_id=evaluation.evaluation_id,
        repository_full_name=evaluation.repository_full_name,
        mode=evaluation.mode,
        adapter_boundary_status=adapter_boundary_status,
        raw_payload_status=raw_payload_status,
        canonical_snapshot_status=canonical_snapshot_status,
        normalization_status=normalization_status,
        pipeline_status=pipeline_status,
        github_status=evaluation.github_status,
        write_status=evaluation.write_status,
        secret_status=evaluation.secret_status,
        summary=summary,
    )


def _evaluate_fake_default(request: RealReadRequest) -> RealReadGateEvaluation:
    reasons = []
    if not request.adapter_required:
        reasons.append("adapter_boundary_required")
    if request.write_operations_allowed:
        reasons.append("writes_forbidden")
    if request.network_access_requested:
        reasons.append("fake_default_must_not_request_network")

    verdict = FAKE_DEFAULT_ALLOWED if not reasons else REAL_READ_BLOCKED
    network_status = NOT_USED if not reasons else BLOCKED

    return RealReadGateEvaluation(
        evaluation_id=_evaluation_id_for(request),
        mode=request.mode,
        repository_full_name=request.repository_full_name,
        verdict=verdict,
        reasons=tuple(reasons),
        adapter_required=request.adapter_required,
        github_status=NOT_CALLED,
        network_status=network_status,
        write_status=WRITES_FORBIDDEN,
        secret_status=NOT_REQUIRED_FOR_FAKE_DEFAULT,
        safe_to_attempt_real_read=False,
    )


def _evaluate_real_read_requested(
    request: RealReadRequest,
) -> RealReadGateEvaluation:
    reasons = []
    if not request.product_owner_authorized:
        reasons.append("product_owner_authorization_required")
    if not request.repository_full_name:
        reasons.append("repository_full_name_required")
    if request.credential_source not in SAFE_REAL_READ_CREDENTIAL_SOURCES:
        reasons.append("safe_credential_handling_required")
    if not request.adapter_required:
        reasons.append("adapter_boundary_required")
    if request.write_operations_allowed:
        reasons.append("writes_forbidden")
    if not request.network_access_requested:
        reasons.append("read_only_network_preflight_required")

    if reasons:
        return RealReadGateEvaluation(
            evaluation_id=_evaluation_id_for(request),
            mode=request.mode,
            repository_full_name=request.repository_full_name,
            verdict=REAL_READ_BLOCKED,
            reasons=tuple(reasons),
            adapter_required=request.adapter_required,
            github_status=NOT_CALLED,
            network_status=BLOCKED,
            write_status=WRITES_FORBIDDEN,
            secret_status=(
                CREDENTIALS_NOT_INSPECTED
                if request.credential_source in SAFE_REAL_READ_CREDENTIAL_SOURCES
                else CREDENTIAL_HANDLING_REQUIRED
            ),
            safe_to_attempt_real_read=False,
        )

    return RealReadGateEvaluation(
        evaluation_id=_evaluation_id_for(request),
        mode=request.mode,
        repository_full_name=request.repository_full_name,
        verdict=REAL_READ_PREFLIGHT_ALLOWED,
        reasons=(),
        adapter_required=request.adapter_required,
        github_status=READ_ONLY_PREFLIGHT_ONLY,
        network_status=PREFLIGHT_ALLOWED,
        write_status=WRITES_FORBIDDEN,
        secret_status=CREDENTIALS_NOT_INSPECTED,
        safe_to_attempt_real_read=True,
    )


def _evaluation_id_for(request: RealReadRequest) -> str:
    return (
        f"a7g:{request.mode}:"
        f"{_id_part(request.repository_full_name, 'missing-repository')}:"
        f"{_id_part(request.authorization_reference, 'missing-authorization')}"
    )


def _id_part(value: str, fallback: str) -> str:
    return value if value else fallback


def _require_request(request: RealReadRequest) -> None:
    if not isinstance(request, RealReadRequest):
        raise RealReadGateError(
            "Real-read gate can only evaluate RealReadRequest objects."
        )


def _require_evaluation(evaluation: RealReadGateEvaluation) -> None:
    if not isinstance(evaluation, RealReadGateEvaluation):
        raise RealReadGateError(
            "Real-read evidence requires a RealReadGateEvaluation."
        )
