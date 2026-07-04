"""Local fixture intake for Artifact 07 GitHub Repo Steward."""

from github_repo_steward.approval_inbox import (
    build_approval_inbox,
    build_approval_inbox_item,
)
from github_repo_steward.analyzer import analyze_repo_snapshot
from github_repo_steward.dry_run_executor import (
    dry_run_ledger_record,
    dry_run_ledger_records,
)
from github_repo_steward.fake_proposal_provider import FakeProposalProvider
from github_repo_steward.github_read_adapter import (
    adapt_github_api_payloads,
    load_default_github_api_fixture_snapshot,
    load_github_api_fixture_payloads,
    map_github_api_payloads_to_canonical_snapshot,
)
from github_repo_steward.ledger import (
    record_decision_to_ledger,
    record_decisions_to_ledger,
)
from github_repo_steward.models import (
    ApprovalInboxError,
    ApprovalInboxItem,
    CiStatusSummary,
    CommentRecord,
    DryRunExecutionError,
    DryRunExecutionResult,
    GitHubReadAdapterError,
    GitHubReadAdapterResult,
    IssueRecord,
    LabelRecord,
    LedgerAuditError,
    LedgerAuditRecord,
    NormalizedRepoSnapshot,
    OperatorDecisionError,
    OperatorDecisionRecord,
    ProposalPolicyEvaluation,
    ProposalPolicyEvaluationError,
    PullRequestRecord,
    RealReadEvidenceRecord,
    RealReadGateError,
    RealReadGateEvaluation,
    RealReadRequest,
    RepoFinding,
    RepoProposal,
    RepoProposalValidationError,
    RepositoryIdentity,
    RepoSnapshotValidationError,
)
from github_repo_steward.normalizer import normalize_repo_snapshot
from github_repo_steward.operator_decisions import (
    record_operator_decision,
    record_operator_decisions,
)
from github_repo_steward.policy_guard import (
    evaluate_repo_proposal,
    evaluate_repo_proposals,
)
from github_repo_steward.proposal_provider import (
    ProposalProvider,
    validate_repo_proposal,
)
from github_repo_steward.real_read_gate import (
    build_real_read_evidence_record,
    evaluate_fake_default_real_read_gate,
    evaluate_real_read_request,
)
from github_repo_steward.repo_snapshot import (
    RawRepoSnapshot,
    load_default_fixture_snapshot,
    load_fixture_snapshot,
)

__all__ = [
    "ApprovalInboxError",
    "ApprovalInboxItem",
    "CiStatusSummary",
    "CommentRecord",
    "DryRunExecutionError",
    "DryRunExecutionResult",
    "FakeProposalProvider",
    "GitHubReadAdapterError",
    "GitHubReadAdapterResult",
    "IssueRecord",
    "LabelRecord",
    "LedgerAuditError",
    "LedgerAuditRecord",
    "NormalizedRepoSnapshot",
    "OperatorDecisionError",
    "OperatorDecisionRecord",
    "ProposalPolicyEvaluation",
    "ProposalPolicyEvaluationError",
    "ProposalProvider",
    "PullRequestRecord",
    "RealReadEvidenceRecord",
    "RealReadGateError",
    "RealReadGateEvaluation",
    "RealReadRequest",
    "RepoFinding",
    "RepoProposal",
    "RepoProposalValidationError",
    "RawRepoSnapshot",
    "RepositoryIdentity",
    "RepoSnapshotValidationError",
    "adapt_github_api_payloads",
    "analyze_repo_snapshot",
    "build_approval_inbox",
    "build_approval_inbox_item",
    "build_real_read_evidence_record",
    "dry_run_ledger_record",
    "dry_run_ledger_records",
    "evaluate_fake_default_real_read_gate",
    "evaluate_real_read_request",
    "evaluate_repo_proposal",
    "evaluate_repo_proposals",
    "load_default_github_api_fixture_snapshot",
    "load_default_fixture_snapshot",
    "load_fixture_snapshot",
    "load_github_api_fixture_payloads",
    "map_github_api_payloads_to_canonical_snapshot",
    "normalize_repo_snapshot",
    "record_decision_to_ledger",
    "record_decisions_to_ledger",
    "record_operator_decision",
    "record_operator_decisions",
    "validate_repo_proposal",
]
