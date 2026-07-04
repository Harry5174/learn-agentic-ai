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
