"""Local fixture intake for Artifact 07 GitHub Repo Steward."""

from github_repo_steward.approval_inbox import (
    build_approval_inbox,
    build_approval_inbox_item,
)
from github_repo_steward.analyzer import analyze_repo_snapshot
from github_repo_steward.fake_proposal_provider import FakeProposalProvider
from github_repo_steward.models import (
    ApprovalInboxError,
    ApprovalInboxItem,
    CiStatusSummary,
    CommentRecord,
    IssueRecord,
    LabelRecord,
    NormalizedRepoSnapshot,
    OperatorDecisionError,
    OperatorDecisionRecord,
    ProposalPolicyEvaluation,
    ProposalPolicyEvaluationError,
    PullRequestRecord,
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
    "FakeProposalProvider",
    "IssueRecord",
    "LabelRecord",
    "NormalizedRepoSnapshot",
    "OperatorDecisionError",
    "OperatorDecisionRecord",
    "ProposalPolicyEvaluation",
    "ProposalPolicyEvaluationError",
    "ProposalProvider",
    "PullRequestRecord",
    "RepoFinding",
    "RepoProposal",
    "RepoProposalValidationError",
    "RawRepoSnapshot",
    "RepositoryIdentity",
    "RepoSnapshotValidationError",
    "analyze_repo_snapshot",
    "build_approval_inbox",
    "build_approval_inbox_item",
    "evaluate_repo_proposal",
    "evaluate_repo_proposals",
    "load_default_fixture_snapshot",
    "load_fixture_snapshot",
    "normalize_repo_snapshot",
    "record_operator_decision",
    "record_operator_decisions",
    "validate_repo_proposal",
]
