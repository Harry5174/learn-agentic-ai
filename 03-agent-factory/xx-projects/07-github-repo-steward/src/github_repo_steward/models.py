"""Typed internal records for local GitHub-like fixture snapshots."""

from __future__ import annotations

from dataclasses import dataclass


class RepoSnapshotValidationError(ValueError):
    """Raised when a local fixture snapshot is missing required data."""


class RepoProposalValidationError(ValueError):
    """Raised when a fake proposal draft violates local shape invariants."""


class ProposalPolicyEvaluationError(ValueError):
    """Raised when proposal policy evaluation cannot safely inspect input."""


class ApprovalInboxError(ValueError):
    """Raised when approval inbox intake receives inconsistent local data."""


class OperatorDecisionError(ValueError):
    """Raised when local operator decision input is malformed or inconsistent."""


class LedgerAuditError(ValueError):
    """Raised when local ledger/audit input is malformed or inconsistent."""


class DryRunExecutionError(ValueError):
    """Raised when local dry-run execution input is malformed or inconsistent."""


class GitHubReadAdapterError(ValueError):
    """Raised when local GitHub-like fixture adapter input is malformed."""


class RealReadGateError(ValueError):
    """Raised when real-read gate input is malformed or inconsistent."""


class RealWriteReadinessError(ValueError):
    """Raised when real-write readiness gate input is malformed or inconsistent."""


_SUPPORTED_WRITE_READINESS_MODES = frozenset(
    {"fake_default", "real_write_readiness_requested"}
)

_SUPPORTED_WRITE_READINESS_VERDICTS = frozenset(
    {
        "fake_default_write_readiness_blocked",
        "real_write_readiness_blocked",
        "real_write_preflight_allowed",
    }
)

_SUPPORTED_WRITE_READINESS_GITHUB_STATUS = frozenset(
    {"not_called", "write_preflight_only"}
)

_SUPPORTED_WRITE_READINESS_NETWORK_STATUS = frozenset(
    {"not_used", "blocked", "preflight_allowed"}
)

_SUPPORTED_WRITE_READINESS_WRITE_STATUS = frozenset(
    {"not_written", "writes_forbidden", "write_preflight_only"}
)

_SUPPORTED_WRITE_READINESS_SECRET_STATUS = frozenset(
    {
        "not_required_for_fake_default",
        "credentials_not_inspected",
        "credential_handling_required",
    }
)

_SUPPORTED_WRITE_READINESS_EXECUTOR_STATUS = frozenset(
    {"not_triggered", "blocked", "preflight_only"}
)

_SUPPORTED_WRITE_OPERATION_TYPES = frozenset(
    {"future_issue_comment", "future_pull_request_comment"}
)

_SUPPORTED_WRITE_READINESS_ADAPTER_BOUNDARY_STATUS = frozenset(
    {
        "adapter_confirmed",
        "adapter_not_confirmed",
        "blocked_before_adapter",
    }
)

_SUPPORTED_WRITE_READINESS_READ_GATE_STATUS = frozenset(
    {
        "real_read_gate_confirmed",
        "real_read_gate_not_confirmed",
        "blocked_before_read_gate",
    }
)

_SUPPORTED_WRITE_READINESS_DRY_RUN_STATUS = frozenset(
    {
        "dry_run_completed",
        "dry_run_not_completed",
        "dry_run_skipped",
        "blocked_before_dry_run",
    }
)

_SUPPORTED_WRITE_READINESS_LEDGER_STATUS = frozenset(
    {
        "ledger_confirmed",
        "ledger_not_confirmed",
        "blocked_before_ledger",
    }
)

_SUPPORTED_WRITE_READINESS_POLICY_STATUS = frozenset(
    {
        "policy_confirmed",
        "policy_not_confirmed",
        "blocked_before_policy",
    }
)

_SUPPORTED_WRITE_READINESS_APPROVAL_STATUS = frozenset(
    {
        "approval_confirmed",
        "approval_not_confirmed",
        "blocked_before_approval",
    }
)


@dataclass(frozen=True)
class RealWriteReadinessRequest:
    mode: str
    repository_full_name: str
    requested_by: str
    product_owner_authorized: bool
    authorization_reference: str
    real_read_evidence_id: str
    dry_run_id: str
    ledger_record_id: str
    decision_id: str
    proposal_id: str
    proposal_type: str
    target_type: str
    target_number: int
    operator_decision: str
    write_operation_type: str
    adapter_boundary_confirmed: bool
    real_read_gate_confirmed: bool
    dry_run_confirmed: bool
    ledger_confirmed: bool
    policy_confirmed: bool
    approval_confirmed: bool
    writes_allowed: bool
    credential_source: str
    secret_handling_confirmed: bool
    executor_runtime_enabled: bool
    evidence_expected: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.mode not in _SUPPORTED_WRITE_READINESS_MODES:
            raise RealWriteReadinessError(
                f"Unsupported write-readiness mode: {self.mode}"
            )
        if not isinstance(self.repository_full_name, str):
            raise RealWriteReadinessError(
                "repository_full_name must be a string."
            )
        if not isinstance(self.requested_by, str) or not self.requested_by:
            raise RealWriteReadinessError("requested_by is required.")
        if not isinstance(self.product_owner_authorized, bool):
            raise RealWriteReadinessError(
                "product_owner_authorized must be a boolean."
            )
        if not isinstance(self.authorization_reference, str):
            raise RealWriteReadinessError(
                "authorization_reference must be a string."
            )
        for field_name in (
            "real_read_evidence_id",
            "dry_run_id",
            "ledger_record_id",
            "decision_id",
            "proposal_id",
            "proposal_type",
            "target_type",
            "operator_decision",
            "write_operation_type",
            "credential_source",
        ):
            if not isinstance(getattr(self, field_name), str):
                raise RealWriteReadinessError(
                    f"{field_name} must be a string."
                )
        if not isinstance(self.target_number, int) or self.target_number < 0:
            raise RealWriteReadinessError(
                "target_number must be a non-negative int."
            )
        for bool_field in (
            "adapter_boundary_confirmed",
            "real_read_gate_confirmed",
            "dry_run_confirmed",
            "ledger_confirmed",
            "policy_confirmed",
            "approval_confirmed",
            "writes_allowed",
            "secret_handling_confirmed",
            "executor_runtime_enabled",
        ):
            if not isinstance(getattr(self, bool_field), bool):
                raise RealWriteReadinessError(
                    f"{bool_field} must be a boolean."
                )
        if not isinstance(self.evidence_expected, tuple) or not all(
            isinstance(ref, str) for ref in self.evidence_expected
        ):
            raise RealWriteReadinessError(
                "evidence_expected must be a tuple of strings."
            )


@dataclass(frozen=True)
class RealWriteReadinessEvaluation:
    evaluation_id: str
    mode: str
    repository_full_name: str
    write_operation_type: str
    verdict: str
    reasons: tuple[str, ...]
    github_status: str
    network_status: str
    write_status: str
    secret_status: str
    executor_status: str
    safe_for_future_write_review: bool

    def __post_init__(self) -> None:
        if self.mode not in _SUPPORTED_WRITE_READINESS_MODES:
            raise RealWriteReadinessError(
                f"Unsupported write-readiness mode: {self.mode}"
            )
        if self.verdict not in _SUPPORTED_WRITE_READINESS_VERDICTS:
            raise RealWriteReadinessError(
                f"Unsupported write-readiness verdict: {self.verdict}"
            )
        if self.github_status not in _SUPPORTED_WRITE_READINESS_GITHUB_STATUS:
            raise RealWriteReadinessError(
                f"Unsupported GitHub status: {self.github_status}"
            )
        if (
            self.network_status
            not in _SUPPORTED_WRITE_READINESS_NETWORK_STATUS
        ):
            raise RealWriteReadinessError(
                f"Unsupported network status: {self.network_status}"
            )
        if self.write_status not in _SUPPORTED_WRITE_READINESS_WRITE_STATUS:
            raise RealWriteReadinessError(
                f"Unsupported write status: {self.write_status}"
            )
        if self.secret_status not in _SUPPORTED_WRITE_READINESS_SECRET_STATUS:
            raise RealWriteReadinessError(
                f"Unsupported secret status: {self.secret_status}"
            )
        if (
            self.executor_status
            not in _SUPPORTED_WRITE_READINESS_EXECUTOR_STATUS
        ):
            raise RealWriteReadinessError(
                f"Unsupported executor status: {self.executor_status}"
            )
        if not isinstance(self.reasons, tuple) or not all(
            isinstance(reason, str) for reason in self.reasons
        ):
            raise RealWriteReadinessError(
                "reasons must be a tuple of strings."
            )
        if not isinstance(self.safe_for_future_write_review, bool):
            raise RealWriteReadinessError(
                "safe_for_future_write_review must be a boolean."
            )
        if self.safe_for_future_write_review and (
            self.verdict != "real_write_preflight_allowed"
            or self.github_status != "write_preflight_only"
            or self.write_status != "write_preflight_only"
            or self.executor_status != "preflight_only"
        ):
            raise RealWriteReadinessError(
                "Only write-preflight-allowed evaluations may be safe for "
                "future write review."
            )
        if (
            self.verdict == "real_write_preflight_allowed"
            and self.mode != "real_write_readiness_requested"
        ):
            raise RealWriteReadinessError(
                "Only real_write_readiness_requested mode may be "
                "preflight allowed."
            )
        if (
            self.verdict == "fake_default_write_readiness_blocked"
            and self.mode != "fake_default"
        ):
            raise RealWriteReadinessError(
                "Only fake_default mode may use "
                "fake_default_write_readiness_blocked verdict."
            )


@dataclass(frozen=True)
class RealWriteReadinessEvidenceRecord:
    evidence_id: str
    evaluation_id: str
    repository_full_name: str
    mode: str
    write_operation_type: str
    real_read_evidence_id: str
    dry_run_id: str
    ledger_record_id: str
    decision_id: str
    proposal_id: str
    adapter_boundary_status: str
    real_read_gate_status: str
    dry_run_status: str
    ledger_status: str
    policy_status: str
    approval_status: str
    github_status: str
    write_status: str
    executor_status: str
    secret_status: str
    summary: str

    def __post_init__(self) -> None:
        if self.mode not in _SUPPORTED_WRITE_READINESS_MODES:
            raise RealWriteReadinessError(
                f"Unsupported evidence mode: {self.mode}"
            )
        if (
            self.adapter_boundary_status
            not in _SUPPORTED_WRITE_READINESS_ADAPTER_BOUNDARY_STATUS
        ):
            raise RealWriteReadinessError(
                "Unsupported adapter boundary status: "
                f"{self.adapter_boundary_status}"
            )
        if (
            self.real_read_gate_status
            not in _SUPPORTED_WRITE_READINESS_READ_GATE_STATUS
        ):
            raise RealWriteReadinessError(
                "Unsupported real-read gate status: "
                f"{self.real_read_gate_status}"
            )
        if (
            self.dry_run_status
            not in _SUPPORTED_WRITE_READINESS_DRY_RUN_STATUS
        ):
            raise RealWriteReadinessError(
                f"Unsupported dry-run status: {self.dry_run_status}"
            )
        if self.ledger_status not in _SUPPORTED_WRITE_READINESS_LEDGER_STATUS:
            raise RealWriteReadinessError(
                f"Unsupported ledger status: {self.ledger_status}"
            )
        if self.policy_status not in _SUPPORTED_WRITE_READINESS_POLICY_STATUS:
            raise RealWriteReadinessError(
                f"Unsupported policy status: {self.policy_status}"
            )
        if (
            self.approval_status
            not in _SUPPORTED_WRITE_READINESS_APPROVAL_STATUS
        ):
            raise RealWriteReadinessError(
                f"Unsupported approval status: {self.approval_status}"
            )
        if self.github_status not in _SUPPORTED_WRITE_READINESS_GITHUB_STATUS:
            raise RealWriteReadinessError(
                f"Unsupported GitHub status: {self.github_status}"
            )
        if self.write_status not in _SUPPORTED_WRITE_READINESS_WRITE_STATUS:
            raise RealWriteReadinessError(
                f"Unsupported write status: {self.write_status}"
            )
        if (
            self.executor_status
            not in _SUPPORTED_WRITE_READINESS_EXECUTOR_STATUS
        ):
            raise RealWriteReadinessError(
                f"Unsupported executor status: {self.executor_status}"
            )
        if self.secret_status not in _SUPPORTED_WRITE_READINESS_SECRET_STATUS:
            raise RealWriteReadinessError(
                f"Unsupported secret status: {self.secret_status}"
            )
        if not isinstance(self.summary, str):
            raise RealWriteReadinessError("summary must be a string.")


@dataclass(frozen=True)
class RealReadRequest:
    mode: str
    repository_full_name: str
    requested_by: str
    product_owner_authorized: bool
    authorization_reference: str
    credential_source: str
    adapter_required: bool
    write_operations_allowed: bool
    network_access_requested: bool
    evidence_expected: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.mode not in {"fake_default", "real_read_requested"}:
            raise RealReadGateError(f"Unsupported real-read mode: {self.mode}")
        if not isinstance(self.repository_full_name, str):
            raise RealReadGateError("repository_full_name must be a string.")
        if not isinstance(self.requested_by, str) or not self.requested_by:
            raise RealReadGateError("requested_by is required.")
        if not isinstance(self.product_owner_authorized, bool):
            raise RealReadGateError(
                "product_owner_authorized must be a boolean."
            )
        if not isinstance(self.authorization_reference, str):
            raise RealReadGateError(
                "authorization_reference must be a string."
            )
        if not isinstance(self.credential_source, str):
            raise RealReadGateError("credential_source must be a string.")
        if not isinstance(self.adapter_required, bool):
            raise RealReadGateError("adapter_required must be a boolean.")
        if not isinstance(self.write_operations_allowed, bool):
            raise RealReadGateError(
                "write_operations_allowed must be a boolean."
            )
        if not isinstance(self.network_access_requested, bool):
            raise RealReadGateError(
                "network_access_requested must be a boolean."
            )
        if not isinstance(self.evidence_expected, tuple) or not all(
            isinstance(ref, str) for ref in self.evidence_expected
        ):
            raise RealReadGateError(
                "evidence_expected must be a tuple of strings."
            )


@dataclass(frozen=True)
class RealReadGateEvaluation:
    evaluation_id: str
    mode: str
    repository_full_name: str
    verdict: str
    reasons: tuple[str, ...]
    adapter_required: bool
    github_status: str
    network_status: str
    write_status: str
    secret_status: str
    safe_to_attempt_real_read: bool

    def __post_init__(self) -> None:
        if self.mode not in {"fake_default", "real_read_requested"}:
            raise RealReadGateError(f"Unsupported real-read mode: {self.mode}")
        if self.verdict not in {
            "fake_default_allowed",
            "real_read_blocked",
            "real_read_preflight_allowed",
        }:
            raise RealReadGateError(f"Unsupported gate verdict: {self.verdict}")
        if self.github_status not in {
            "not_called",
            "read_only_preflight_only",
        }:
            raise RealReadGateError(
                f"Unsupported GitHub status: {self.github_status}"
            )
        if self.network_status not in {
            "not_used",
            "blocked",
            "preflight_allowed",
        }:
            raise RealReadGateError(
                f"Unsupported network status: {self.network_status}"
            )
        if self.write_status != "writes_forbidden":
            raise RealReadGateError("Real-read gate must forbid writes.")
        if self.secret_status not in {
            "not_required_for_fake_default",
            "credentials_not_inspected",
            "credential_handling_required",
        }:
            raise RealReadGateError(
                f"Unsupported secret status: {self.secret_status}"
            )
        if not isinstance(self.reasons, tuple) or not all(
            isinstance(reason, str) for reason in self.reasons
        ):
            raise RealReadGateError("reasons must be a tuple of strings.")
        if not isinstance(self.adapter_required, bool):
            raise RealReadGateError("adapter_required must be a boolean.")
        if not isinstance(self.safe_to_attempt_real_read, bool):
            raise RealReadGateError(
                "safe_to_attempt_real_read must be a boolean."
            )
        if self.safe_to_attempt_real_read and (
            self.verdict != "real_read_preflight_allowed"
            or self.github_status != "read_only_preflight_only"
            or self.network_status != "preflight_allowed"
        ):
            raise RealReadGateError(
                "Only read-only preflight evaluations may be safe to attempt."
            )
        if (
            self.verdict == "real_read_preflight_allowed"
            and self.mode != "real_read_requested"
        ):
            raise RealReadGateError(
                "Only real_read_requested mode may be preflight allowed."
            )
        if self.verdict == "fake_default_allowed" and self.mode != "fake_default":
            raise RealReadGateError(
                "Only fake_default mode may be fake_default_allowed."
            )


@dataclass(frozen=True)
class RealReadEvidenceRecord:
    evidence_id: str
    evaluation_id: str
    repository_full_name: str
    mode: str
    adapter_boundary_status: str
    raw_payload_status: str
    canonical_snapshot_status: str
    normalization_status: str
    pipeline_status: str
    github_status: str
    write_status: str
    secret_status: str
    summary: str

    def __post_init__(self) -> None:
        if self.mode not in {"fake_default", "real_read_requested"}:
            raise RealReadGateError(f"Unsupported evidence mode: {self.mode}")
        if self.adapter_boundary_status not in {
            "adapter_used",
            "blocked_before_adapter",
            "adapter_required_but_not_used",
        }:
            raise RealReadGateError(
                "Unsupported adapter boundary status: "
                f"{self.adapter_boundary_status}"
            )
        if self.raw_payload_status not in {
            "local_fixture_payload",
            "blocked_no_raw_payload",
            "live_payload_not_captured",
            "live_payload_captured",
        }:
            raise RealReadGateError(
                f"Unsupported raw payload status: {self.raw_payload_status}"
            )
        if self.canonical_snapshot_status not in {
            "mapped_locally",
            "not_mapped_blocked",
            "not_available",
        }:
            raise RealReadGateError(
                "Unsupported canonical snapshot status: "
                f"{self.canonical_snapshot_status}"
            )
        if self.normalization_status not in {
            "normalized_locally",
            "not_normalized_blocked",
            "not_available",
        }:
            raise RealReadGateError(
                f"Unsupported normalization status: {self.normalization_status}"
            )
        if self.pipeline_status not in {
            "local_pipeline_completed",
            "blocked_before_pipeline",
            "not_run",
        }:
            raise RealReadGateError(
                f"Unsupported pipeline status: {self.pipeline_status}"
            )
        if self.github_status not in {
            "not_called",
            "read_only_preflight_only",
        }:
            raise RealReadGateError(
                f"Unsupported GitHub status: {self.github_status}"
            )
        if self.write_status != "writes_forbidden":
            raise RealReadGateError("Real-read evidence must forbid writes.")
        if self.secret_status not in {
            "not_required_for_fake_default",
            "credentials_not_inspected",
            "credential_handling_required",
        }:
            raise RealReadGateError(
                f"Unsupported secret status: {self.secret_status}"
            )
        if self.mode == "fake_default" and (
            self.pipeline_status == "local_pipeline_completed"
            and self.adapter_boundary_status != "adapter_used"
        ):
            raise RealReadGateError(
                "Completed fake/default evidence must use the adapter boundary."
            )
        if not isinstance(self.summary, str):
            raise RealReadGateError("summary must be a string.")


@dataclass(frozen=True)
class OperatorDecisionRecord:
    decision_id: str
    inbox_item_id: str
    proposal_id: str
    decision: str
    decided_by: str
    rationale: str
    status: str
    execution_status: str
    ledger_status: str

    def __post_init__(self) -> None:
        if self.decision not in {
            "approved_by_operator",
            "rejected_by_operator",
        }:
            raise OperatorDecisionError(
                f"Unsupported operator decision: {self.decision}"
            )
        if self.status != "local_decision_recorded":
            raise OperatorDecisionError(
                "Operator decision status must be local_decision_recorded."
            )
        if self.execution_status != "not_executed":
            raise OperatorDecisionError(
                "Operator decisions must never mark proposals as executed."
            )
        if self.ledger_status != "not_recorded":
            raise OperatorDecisionError(
                "Operator decisions must not mark ledger records as written."
            )
        if not self.decided_by:
            raise OperatorDecisionError("decided_by is required.")
        if self.decision == "rejected_by_operator" and not self.rationale:
            raise OperatorDecisionError(
                "rejected_by_operator decisions require a rationale."
            )


@dataclass(frozen=True)
class LedgerAuditRecord:
    ledger_record_id: str
    decision_id: str
    inbox_item_id: str
    proposal_id: str
    decision: str
    decided_by: str
    decision_rationale: str
    record_type: str
    record_status: str
    execution_status: str
    github_status: str
    executor_status: str
    source_snapshot_id: str
    evidence_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.decision not in {
            "approved_by_operator",
            "rejected_by_operator",
        }:
            raise LedgerAuditError(
                f"Unsupported operator decision: {self.decision}"
            )
        if self.record_type != "operator_decision_audit":
            raise LedgerAuditError(
                "Ledger audit records must be operator_decision_audit."
            )
        if self.record_status != "recorded_locally":
            raise LedgerAuditError(
                "Ledger audit records must be recorded_locally."
            )
        if self.execution_status != "not_executed":
            raise LedgerAuditError(
                "Ledger audit records must not claim execution."
            )
        if self.github_status != "not_called":
            raise LedgerAuditError(
                "Ledger audit records must not claim GitHub calls."
            )
        if self.executor_status != "not_triggered":
            raise LedgerAuditError(
                "Ledger audit records must not claim executor work."
            )
        if not self.decision_id:
            raise LedgerAuditError("decision_id is required.")
        if not self.inbox_item_id:
            raise LedgerAuditError("inbox_item_id is required.")
        if not self.proposal_id:
            raise LedgerAuditError("proposal_id is required.")
        if not self.decided_by:
            raise LedgerAuditError("decided_by is required.")
        if not isinstance(self.source_snapshot_id, str):
            raise LedgerAuditError("source_snapshot_id must be a string.")
        if not isinstance(self.evidence_refs, tuple) or not all(
            isinstance(ref, str) for ref in self.evidence_refs
        ):
            raise LedgerAuditError("evidence_refs must be a tuple of strings.")


@dataclass(frozen=True)
class DryRunExecutionResult:
    dry_run_id: str
    ledger_record_id: str
    decision_id: str
    inbox_item_id: str
    proposal_id: str
    proposal_type: str
    target_type: str
    target_number: int
    decision: str
    planned_action: str
    dry_run_status: str
    execution_status: str
    github_status: str
    external_side_effect_status: str
    ledger_record_status: str
    evidence_refs: tuple[str, ...]
    summary: str

    def __post_init__(self) -> None:
        if self.dry_run_status not in {
            "dry_run_completed",
            "dry_run_skipped",
        }:
            raise DryRunExecutionError(
                f"Unsupported dry-run status: {self.dry_run_status}"
            )
        if self.execution_status != "not_executed":
            raise DryRunExecutionError(
                "Dry-run results must never claim execution."
            )
        if self.github_status != "not_called":
            raise DryRunExecutionError(
                "Dry-run results must never claim GitHub calls."
            )
        if self.external_side_effect_status != "none":
            raise DryRunExecutionError(
                "Dry-run results must never claim external side effects."
            )
        if self.ledger_record_status != "verified_local_audit_record":
            raise DryRunExecutionError(
                "Dry-run results require verified local audit records."
            )
        if self.decision not in {
            "approved_by_operator",
            "rejected_by_operator",
        }:
            raise DryRunExecutionError(
                f"Unsupported operator decision: {self.decision}"
            )
        if not isinstance(self.target_number, int) or self.target_number < 1:
            raise DryRunExecutionError("target_number must be a positive int.")
        if not isinstance(self.evidence_refs, tuple) or not all(
            isinstance(ref, str) for ref in self.evidence_refs
        ):
            raise DryRunExecutionError(
                "evidence_refs must be a tuple of strings."
            )


@dataclass(frozen=True)
class GitHubReadAdapterResult:
    source: str
    repository_full_name: str
    canonical_snapshot: dict[str, object]
    raw_endpoint_names: tuple[str, ...]
    warnings: tuple[str, ...]
    adapter_status: str
    github_status: str
    network_status: str

    def __post_init__(self) -> None:
        if self.adapter_status != "mapped_locally":
            raise GitHubReadAdapterError(
                "GitHub read adapter status must be mapped_locally."
            )
        if self.github_status != "not_called":
            raise GitHubReadAdapterError(
                "GitHub read adapter must never claim GitHub calls."
            )
        if self.network_status != "not_used":
            raise GitHubReadAdapterError(
                "GitHub read adapter must never claim network use."
            )
        if not isinstance(self.canonical_snapshot, dict):
            raise GitHubReadAdapterError(
                "canonical_snapshot must be a dictionary."
            )
        if not isinstance(self.raw_endpoint_names, tuple) or not all(
            isinstance(name, str) for name in self.raw_endpoint_names
        ):
            raise GitHubReadAdapterError(
                "raw_endpoint_names must be a tuple of strings."
            )
        if not isinstance(self.warnings, tuple) or not all(
            isinstance(warning, str) for warning in self.warnings
        ):
            raise GitHubReadAdapterError(
                "warnings must be a tuple of strings."
            )


@dataclass(frozen=True)
class ProposalPolicyEvaluation:
    evaluation_id: str
    proposal_id: str
    verdict: str
    reasons: tuple[str, ...]
    risk_level: str
    requires_operator_approval: bool
    safe_for_operator_review: bool

    def __post_init__(self) -> None:
        if self.verdict not in {
            "allowed_for_operator_review",
            "blocked_by_policy",
        }:
            raise ProposalPolicyEvaluationError(
                f"Unsupported policy verdict: {self.verdict}"
            )
        if self.requires_operator_approval is not True:
            raise ProposalPolicyEvaluationError(
                "requires_operator_approval must always be True."
            )
        if (
            self.safe_for_operator_review
            and self.verdict != "allowed_for_operator_review"
        ):
            raise ProposalPolicyEvaluationError(
                "Only allowed proposals may be safe for operator review."
            )
        if self.verdict == "blocked_by_policy" and not self.reasons:
            raise ProposalPolicyEvaluationError(
                "Blocked policy evaluations must include at least one reason."
            )


@dataclass(frozen=True)
class ApprovalInboxItem:
    inbox_item_id: str
    proposal_id: str
    evaluation_id: str
    proposal_type: str
    target_type: str
    target_number: int
    title: str
    draft_body: str
    risk_level: str
    status: str
    requires_operator_approval: bool
    created_from_policy_verdict: str
    policy_reasons: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.status != "pending_operator_review":
            raise ApprovalInboxError(
                "Approval inbox items must remain pending_operator_review."
            )
        if self.requires_operator_approval is not True:
            raise ApprovalInboxError(
                "Approval inbox items must require operator approval."
            )
        if self.created_from_policy_verdict != "allowed_for_operator_review":
            raise ApprovalInboxError(
                "Approval inbox items must come from allowed policy evaluations."
            )
        if self.policy_reasons:
            raise ApprovalInboxError(
                "Approval inbox items must not carry blocked policy reasons."
            )


@dataclass(frozen=True)
class RepositoryIdentity:
    owner: str
    name: str
    default_branch: str
    snapshot_generated_at: str


@dataclass(frozen=True)
class LabelRecord:
    name: str
    description: str
    color: str | None = None


@dataclass(frozen=True)
class IssueRecord:
    id: int
    number: int
    title: str
    body: str
    state: str
    labels: tuple[str, ...]
    author: str
    created_at: str
    updated_at: str
    comments_count: int
    stale_days: int


@dataclass(frozen=True)
class PullRequestRecord:
    id: int
    number: int
    title: str
    body: str
    state: str
    labels: tuple[str, ...]
    author: str
    created_at: str
    updated_at: str
    branch: str
    base_branch: str
    review_status: str
    ci_status: str
    stale_days: int


@dataclass(frozen=True)
class CommentRecord:
    id: int
    target_type: str
    target_number: int
    author: str
    body: str
    created_at: str


@dataclass(frozen=True)
class CiStatusSummary:
    target_type: str
    target_number: int
    status: str
    conclusion: str
    updated_at: str


@dataclass(frozen=True)
class RepoFinding:
    finding_id: str
    finding_type: str
    severity: str
    target_type: str
    target_number: int
    title: str
    summary: str
    evidence: tuple[str, ...]


@dataclass(frozen=True)
class RepoProposal:
    proposal_id: str
    source_finding_id: str
    proposal_type: str
    target_type: str
    target_number: int
    title: str
    draft_body: str
    rationale: str
    risk_level: str
    requires_approval: bool
    execution_status: str


@dataclass(frozen=True)
class NormalizedRepoSnapshot:
    repository: RepositoryIdentity
    labels: tuple[LabelRecord, ...]
    issues: tuple[IssueRecord, ...]
    pull_requests: tuple[PullRequestRecord, ...]
    comments: tuple[CommentRecord, ...]
    ci_statuses: tuple[CiStatusSummary, ...]
