"""Deterministic local evidence gate for real-write readiness evaluation."""

from __future__ import annotations

from github_repo_steward.models import (
    RealWriteReadinessError,
    RealWriteReadinessEvaluation,
    RealWriteReadinessEvidenceRecord,
    RealWriteReadinessRequest,
    _SUPPORTED_WRITE_OPERATION_TYPES,
)

FAKE_DEFAULT = "fake_default"
REAL_WRITE_READINESS_REQUESTED = "real_write_readiness_requested"
FAKE_DEFAULT_WRITE_READINESS_BLOCKED = "fake_default_write_readiness_blocked"
REAL_WRITE_READINESS_BLOCKED = "real_write_readiness_blocked"
REAL_WRITE_PREFLIGHT_ALLOWED = "real_write_preflight_allowed"
NOT_CALLED = "not_called"
WRITE_PREFLIGHT_ONLY = "write_preflight_only"
NOT_USED = "not_used"
BLOCKED = "blocked"
PREFLIGHT_ALLOWED = "preflight_allowed"
NOT_WRITTEN = "not_written"
WRITES_FORBIDDEN = "writes_forbidden"
WR_WRITE_PREFLIGHT_ONLY = "write_preflight_only"
NOT_REQUIRED_FOR_FAKE_DEFAULT = "not_required_for_fake_default"
CREDENTIALS_NOT_INSPECTED = "credentials_not_inspected"
CREDENTIAL_HANDLING_REQUIRED = "credential_handling_required"
NOT_TRIGGERED = "not_triggered"
EXECUTOR_BLOCKED = "blocked"
PREFLIGHT_ONLY = "preflight_only"


def evaluate_fake_default_real_write_readiness_gate() -> (
    RealWriteReadinessEvaluation
):
    """Evaluate the default fake/local mode write-readiness gate."""

    return evaluate_real_write_readiness(
        RealWriteReadinessRequest(
            mode=FAKE_DEFAULT,
            repository_full_name="local/fake-default",
            requested_by="local-operator",
            product_owner_authorized=False,
            authorization_reference="not-authorized-fake-default",
            real_read_evidence_id="",
            dry_run_id="",
            ledger_record_id="",
            decision_id="",
            proposal_id="",
            proposal_type="",
            target_type="",
            target_number=0,
            operator_decision="",
            write_operation_type="",
            adapter_boundary_confirmed=False,
            real_read_gate_confirmed=False,
            dry_run_confirmed=False,
            ledger_confirmed=False,
            policy_confirmed=False,
            approval_confirmed=False,
            writes_allowed=False,
            credential_source="none",
            secret_handling_confirmed=False,
            executor_runtime_enabled=False,
            evidence_expected=("fake-default-write-readiness-blocked",),
        )
    )


def evaluate_real_write_readiness(
    request: RealWriteReadinessRequest,
) -> RealWriteReadinessEvaluation:
    """Evaluate a local real-write readiness gate request.

    This gate does not call GitHub. It does not authenticate.
    It does not read .env. It does not perform writes.
    It does not trigger executor runtime.
    """

    _require_request(request)

    if request.mode == FAKE_DEFAULT:
        return _evaluate_fake_default(request)
    return _evaluate_real_write_readiness_requested(request)


def build_real_write_readiness_evidence_record(
    evaluation: RealWriteReadinessEvaluation,
    adapter_boundary_status: str,
    real_read_gate_status: str,
    dry_run_status: str,
    ledger_status: str,
    policy_status: str,
    approval_status: str,
    summary: str = "",
) -> RealWriteReadinessEvidenceRecord:
    """Build a deterministic local evidence record for a write-readiness
    gate evaluation."""

    _require_evaluation(evaluation)
    evidence_id = ":".join(
        (
            "a7w",
            evaluation.evaluation_id,
            adapter_boundary_status,
            real_read_gate_status,
            dry_run_status,
            ledger_status,
            policy_status,
            approval_status,
        )
    )

    return RealWriteReadinessEvidenceRecord(
        evidence_id=evidence_id,
        evaluation_id=evaluation.evaluation_id,
        repository_full_name=evaluation.repository_full_name,
        mode=evaluation.mode,
        write_operation_type=evaluation.write_operation_type,
        real_read_evidence_id="",
        dry_run_id="",
        ledger_record_id="",
        decision_id="",
        proposal_id="",
        adapter_boundary_status=adapter_boundary_status,
        real_read_gate_status=real_read_gate_status,
        dry_run_status=dry_run_status,
        ledger_status=ledger_status,
        policy_status=policy_status,
        approval_status=approval_status,
        github_status=evaluation.github_status,
        write_status=evaluation.write_status,
        executor_status=evaluation.executor_status,
        secret_status=evaluation.secret_status,
        summary=summary,
    )


def _evaluate_fake_default(
    request: RealWriteReadinessRequest,
) -> RealWriteReadinessEvaluation:
    reasons = ["fake_default_mode_blocks_real_write_readiness"]

    return RealWriteReadinessEvaluation(
        evaluation_id=_evaluation_id_for(request),
        mode=request.mode,
        repository_full_name=request.repository_full_name,
        write_operation_type=request.write_operation_type or "none",
        verdict=FAKE_DEFAULT_WRITE_READINESS_BLOCKED,
        reasons=tuple(reasons),
        github_status=NOT_CALLED,
        network_status=NOT_USED,
        write_status=NOT_WRITTEN,
        secret_status=NOT_REQUIRED_FOR_FAKE_DEFAULT,
        executor_status=NOT_TRIGGERED,
        safe_for_future_write_review=False,
    )


def _evaluate_real_write_readiness_requested(
    request: RealWriteReadinessRequest,
) -> RealWriteReadinessEvaluation:
    reasons: list[str] = []

    # Product Owner authorization
    if not request.product_owner_authorized:
        reasons.append("product_owner_authorization_required")

    # Required identity fields
    if not request.repository_full_name:
        reasons.append("repository_full_name_required")
    if not request.real_read_evidence_id:
        reasons.append("real_read_evidence_id_required")
    if not request.dry_run_id:
        reasons.append("dry_run_id_required")
    if not request.ledger_record_id:
        reasons.append("ledger_record_id_required")
    if not request.decision_id:
        reasons.append("decision_id_required")
    if not request.proposal_id:
        reasons.append("proposal_id_required")

    # Operator decision
    if request.operator_decision != "approved_by_operator":
        reasons.append("operator_decision_must_be_approved")

    # Write operation type
    if request.write_operation_type not in _SUPPORTED_WRITE_OPERATION_TYPES:
        reasons.append("unsupported_write_operation_type")

    # Safety boundary confirmations
    if not request.adapter_boundary_confirmed:
        reasons.append("adapter_boundary_confirmation_required")
    if not request.real_read_gate_confirmed:
        reasons.append("real_read_gate_confirmation_required")
    if not request.dry_run_confirmed:
        reasons.append("dry_run_confirmation_required")
    if not request.ledger_confirmed:
        reasons.append("ledger_confirmation_required")
    if not request.policy_confirmed:
        reasons.append("policy_confirmation_required")
    if not request.approval_confirmed:
        reasons.append("approval_confirmation_required")
    if not request.secret_handling_confirmed:
        reasons.append("secret_handling_confirmation_required")

    # Executor must be disabled for readiness-only evaluation
    if request.executor_runtime_enabled:
        reasons.append("executor_runtime_must_be_disabled")

    if reasons:
        return RealWriteReadinessEvaluation(
            evaluation_id=_evaluation_id_for(request),
            mode=request.mode,
            repository_full_name=request.repository_full_name,
            write_operation_type=request.write_operation_type or "none",
            verdict=REAL_WRITE_READINESS_BLOCKED,
            reasons=tuple(reasons),
            github_status=NOT_CALLED,
            network_status=BLOCKED,
            write_status=WRITES_FORBIDDEN,
            secret_status=(
                CREDENTIALS_NOT_INSPECTED
                if request.secret_handling_confirmed
                else CREDENTIAL_HANDLING_REQUIRED
            ),
            executor_status=NOT_TRIGGERED,
            safe_for_future_write_review=False,
        )

    # All preconditions met — metadata-only preflight allowed
    return RealWriteReadinessEvaluation(
        evaluation_id=_evaluation_id_for(request),
        mode=request.mode,
        repository_full_name=request.repository_full_name,
        write_operation_type=request.write_operation_type,
        verdict=REAL_WRITE_PREFLIGHT_ALLOWED,
        reasons=(),
        github_status=WRITE_PREFLIGHT_ONLY,
        network_status=PREFLIGHT_ALLOWED,
        write_status=WR_WRITE_PREFLIGHT_ONLY,
        secret_status=CREDENTIALS_NOT_INSPECTED,
        executor_status=PREFLIGHT_ONLY,
        safe_for_future_write_review=True,
    )


def _evaluation_id_for(request: RealWriteReadinessRequest) -> str:
    return (
        f"a7wg:{request.mode}:"
        f"{_id_part(request.repository_full_name, 'missing-repository')}:"
        f"{_id_part(request.authorization_reference, 'missing-authorization')}:"
        f"{_id_part(request.write_operation_type, 'no-write-op')}"
    )


def _id_part(value: str, fallback: str) -> str:
    return value if value else fallback


def _require_request(request: RealWriteReadinessRequest) -> None:
    if not isinstance(request, RealWriteReadinessRequest):
        raise RealWriteReadinessError(
            "Real-write readiness gate can only evaluate "
            "RealWriteReadinessRequest objects."
        )


def _require_evaluation(evaluation: RealWriteReadinessEvaluation) -> None:
    if not isinstance(evaluation, RealWriteReadinessEvaluation):
        raise RealWriteReadinessError(
            "Real-write readiness evidence requires a "
            "RealWriteReadinessEvaluation."
        )
