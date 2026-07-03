# Artifact 7.4 Validation Summary

## Scope

Sprint 7.4 validates deterministic local proposal policy evaluation for
Artifact 07. It does not validate approval routing, ledger recording,
execution, real GitHub access, GitHub API adapter correctness, real LLM
integration, or production readiness.

## Sprint Objective

Add a local deterministic policy guard that evaluates `RepoProposal` drafts and
returns structured `ProposalPolicyEvaluation` records. Safe drafts may be marked
`allowed_for_operator_review` for a future operator-review layer only. Unsafe
drafts are blocked with reasons.

## Files Added

- `src/github_repo_steward/policy_guard.py`
- `tests/test_policy_guard.py`
- `tests/test_policy_guard_determinism.py`
- `tests/test_policy_guard_no_side_effects.py`
- `docs/evidence/artifact-7.4-validation-summary.md`

## Files Modified

- `src/github_repo_steward/models.py`
- `src/github_repo_steward/__init__.py`
- `README.md`
- `docs/design.md`
- `docs/safety-boundaries.md`
- `docs/evidence/README.md`
- `tests/README.md`
- Parent artifact index: `../README.md`

## Policy Model Added

- `ProposalPolicyEvaluation`
- `ProposalPolicyEvaluationError`

Every policy evaluation requires future operator approval. A policy evaluation
may be safe for operator review only when its verdict is
`allowed_for_operator_review`. Blocked evaluations must include at least one
reason.

## Policy Guard Behavior Added

- Evaluates `RepoProposal` objects only.
- Produces stable evaluation IDs using `a7e:{proposal_id}`.
- Uses `a7e:missing-proposal-id` for missing proposal IDs.
- Produces deterministic evaluation order.
- Allows low- and medium-risk draft-only proposals for future operator review.
- Blocks unsafe or unsupported proposal drafts with reasons.
- Blocks draft bodies that claim completed repository actions.
- Blocks draft bodies containing local token-like guard-pattern strings.
- Does not approve proposals.
- Does not execute proposals.
- Does not mutate proposals.
- Does not write ledger entries.
- Does not enqueue approval inbox items.
- Does not call GitHub.
- Does not read `.env`.
- Does not require real LLM provider keys.

## Validation Commands Run

- `git status -sb`
- `git diff --check`
- `find 03-agent-factory/xx-projects/07-github-repo-steward -maxdepth 5 -type f | sort`
- `grep -RInE "GITHUB_TOKEN|OPENAI_API_KEY|ANTHROPIC_API_KEY|Authorization:|Bearer |ghp_|github_pat_" 03-agent-factory/xx-projects/07-github-repo-steward || true`
- Local-path scan from the sprint prompt.
- `git ls-files .env`
- `git ls-files "*__pycache__*"`
- `git ls-files "*.pyc"`
- `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src PYTEST_ADDOPTS="-p no:cacheprovider" python -m pytest tests`
- Compile check with an isolated Python cache prefix outside the artifact tree.

## Test Results

- Artifact 07 pytest suite: 61 passed.
- Compile check: passed.
- Existing Sprint 7.1, Sprint 7.2, and Sprint 7.3 tests remain preserved.

## Safety Scan Results

- `.env` remains untracked.
- No tracked `__pycache__` files.
- No tracked `.pyc` files.
- No real GitHub API path was added.
- No real LLM provider dependency was added.
- No approval inbox, ledger, executor, or GitHub API adapter runtime was added.

Safety-scan hits for strings such as `GITHUB_TOKEN=`, `Authorization:`,
`Bearer `, `ghp_`, and `github_pat_` are intentional local guard-pattern
literals used by the policy guard, tests, and documentation to prove
token-like proposal text is blocked. They are not secret values.

## What Sprint 7.4 Proves

- Proposal objects can be evaluated by deterministic local policy rules.
- Policy evaluation output is structured.
- Policy evaluation output is deterministic.
- Safe proposal drafts can be marked as allowed for future operator review.
- Unsafe proposal drafts can be blocked by policy.
- Policy guard does not approve proposals.
- Policy guard does not execute proposals.
- Policy guard does not mutate proposals.
- Policy guard works without network.
- Policy guard works without secrets.
- Policy guard works without real LLM provider keys.
- Policy guard does not call GitHub APIs.

## What Sprint 7.4 Does Not Prove

- Approval-gated runtime.
- Approval inbox runtime.
- Operator decision handling.
- Ledger/audit runtime.
- Dry-run execution.
- Real GitHub reads.
- Real GitHub writes.
- GitHub API adapter correctness.
- Real GitHub integration.
- Real LLM integration.
- Production readiness.

## Known Limitations

- Policy rules are local string and field checks only.
- `allowed_for_operator_review` is not approval.
- All proposals still require future operator approval.
- The canonical fixture is an internal model, not raw GitHub REST API data.
- Future real GitHub reads require a dedicated adapter sprint before any
  real-read or real-write claim.

## Next Recommended Sprint

Artifact 7.5 - Approval Inbox Integration, subject to Design Supervisor
approval.
