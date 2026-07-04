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
