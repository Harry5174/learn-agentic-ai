# Artifact 7.5 Validation Summary

## Scope

Sprint 7.5 validates local approval inbox integration for policy-allowed
proposal drafts. It does not validate operator approval decision handling,
operator rejection handling, ledger recording, execution, real GitHub access,
GitHub API adapter correctness, real LLM integration, or production readiness.

## Sprint Objective

Add deterministic local approval inbox intake that converts policy-allowed
`RepoProposal` drafts and matching `ProposalPolicyEvaluation` records into
structured `ApprovalInboxItem` records. Every item remains pending future
operator review.

## Files Added

- `src/github_repo_steward/approval_inbox.py`
- `tests/test_approval_inbox.py`
- `tests/test_approval_inbox_determinism.py`
- `tests/test_approval_inbox_no_side_effects.py`
- `docs/evidence/artifact-7.5-validation-summary.md`

## Files Modified

- `src/github_repo_steward/models.py`
- `src/github_repo_steward/__init__.py`
- `README.md`
- `docs/design.md`
- `docs/safety-boundaries.md`
- `docs/evidence/README.md`
- `tests/README.md`
- Parent artifact index: `../README.md`

## Approval Inbox Model Added

- `ApprovalInboxItem`
- `ApprovalInboxError`

Every inbox item remains `pending_operator_review`. Every inbox item requires
future operator approval. Every inbox item must be created from
`allowed_for_operator_review`. Blocked policy evaluations must not become inbox
items.

## Approval Inbox Behavior Added

- Builds pending inbox items from matched proposal and policy evaluation pairs.
- Produces stable inbox item IDs using `a7i:{proposal_id}:{evaluation_id}`.
- Produces deterministic inbox order.
- Accepts only `allowed_for_operator_review` policy evaluations.
- Safely excludes blocked policy evaluations from inbox intake.
- Fails safely for missing, duplicate, extra, or mismatched evaluations.
- Does not approve proposals.
- Does not reject proposals.
- Does not execute proposals.
- Does not mutate proposals or evaluations.
- Does not write ledger entries.
- Does not call GitHub.
- Does not read `.env`.
- Does not require real LLM provider keys.

## Validation Commands Run

- `git status -sb`
- `git diff --check`
- Artifact 07 file inventory.
- Token-pattern scan from the sprint prompt.
- Local-path scan from the sprint prompt.
- `git ls-files .env`
- `git ls-files "*__pycache__*"`
- `git ls-files "*.pyc"`
- Artifact 07 pytest suite with bytecode and pytest cache disabled.
- Compile check with an isolated Python cache prefix outside the artifact tree.

## Test Results

- Artifact 07 pytest suite: 81 passed.
- Compile check: passed.
- Existing Sprint 7.1, Sprint 7.2, Sprint 7.3, and Sprint 7.4 tests remain
  preserved.

## Safety Scan Results

- `.env` remains untracked.
- No tracked `__pycache__` files.
- No tracked `.pyc` files.
- No real GitHub API path was added.
- No GitHub API adapter was added.
- No real LLM provider dependency was added.
- No operator approval decision handling was added.
- No ledger or executor runtime was added.

Safety-scan hits for strings such as `GITHUB_TOKEN=`, `Authorization:`,
`Bearer `, `ghp_`, and `github_pat_` are intentional local guard-pattern or
environment-variable-name literals used by the policy guard, tests, and
documentation. They are not secret values.

## What Sprint 7.5 Proves

- Policy-allowed proposal drafts can be converted into approval inbox items.
- Blocked proposals are not accepted into the approval inbox.
- Approval inbox items are structured.
- Approval inbox item IDs are deterministic.
- Approval inbox order is deterministic.
- Every inbox item remains pending future operator review.
- Inbox integration does not approve proposals.
- Inbox integration does not reject proposals.
- Inbox integration does not execute proposals.
- Inbox integration does not write ledger/audit records.
- Inbox integration works without network.
- Inbox integration works without secrets.
- Inbox integration works without real LLM provider keys.
- Inbox integration does not call GitHub APIs.

## What Sprint 7.5 Does Not Prove

- Operator approval decision handling.
- Operator rejection handling.
- Approval-gated execution.
- Ledger/audit runtime.
- Dry-run execution.
- Real GitHub reads.
- Real GitHub writes.
- GitHub API adapter correctness.
- Real GitHub integration.
- Real LLM integration.
- Production readiness.

## Known Limitations

- Inbox items are local pending-review records only.
- `pending_operator_review` is not approval.
- No operator identity, approval, rejection, decision binding, ledger, audit, or
  executor path exists in Sprint 7.5.
- The canonical fixture is an internal model, not raw GitHub REST API data.
- Future real GitHub reads require a dedicated adapter sprint before any
  real-read or real-write claim.

## Next Recommended Sprint

Artifact 7.6 - Operator Decision Handling, subject to Design Supervisor
approval.
