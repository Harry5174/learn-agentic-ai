# Artifact 7.9 Validation Summary

## Sprint Objective

Sprint 7.9 validates a local GitHub API read adapter contract for Artifact 07.
It maps committed raw GitHub-like endpoint fixture payloads into the canonical
internal snapshot dictionary shape consumed by the existing normalizer and local
pipeline.

Sprint 7.9 does not implement real GitHub reads, real GitHub writes, GitHub
authentication, GitHub App integration, GitHub OAuth integration, complete
GitHub API payload coverage, real GitHub integration, real LLM integration, real
executor runtime, durable persistence, or production readiness.

## Files Added

- `fixtures/github_api/repository.json`
- `fixtures/github_api/labels.json`
- `fixtures/github_api/issues.json`
- `fixtures/github_api/pulls.json`
- `fixtures/github_api/issue_comments.json`
- `fixtures/github_api/pull_reviews.json`
- `fixtures/github_api/check_runs.json`
- `fixtures/github_api/statuses.json`
- `src/github_repo_steward/github_read_adapter.py`
- `tests/test_github_read_adapter.py`
- `tests/test_github_read_adapter_determinism.py`
- `tests/test_github_read_adapter_no_side_effects.py`
- `docs/evidence/artifact-7.9-validation-summary.md`

## Files Modified

- `src/github_repo_steward/models.py`
- `src/github_repo_steward/__init__.py`
- `README.md`
- `docs/design.md`
- `docs/safety-boundaries.md`
- `docs/evidence/README.md`
- `tests/README.md`
- Parent artifact index: `../README.md`

## Raw GitHub-Like Fixtures Added

The local fixture set separates raw endpoint-like payload families:

- repository identity
- labels
- issues
- pulls
- issue comments
- pull reviews
- check runs
- statuses

The issues fixture includes an issue-like record with a `pull_request` marker so
the adapter can prove that pull requests from an issue-shaped endpoint are not
duplicated as canonical issues.

## Adapter Contract Added

- `GitHubReadAdapterError`
- `GitHubReadAdapterResult`
- `load_github_api_fixture_payloads`
- `map_github_api_payloads_to_canonical_snapshot`
- `load_default_github_api_fixture_snapshot`
- `adapt_github_api_payloads`

Every structured adapter result has:

- `adapter_status="mapped_locally"`
- `github_status="not_called"`
- `network_status="not_used"`

## Adapter Behavior Added

- Loads committed local raw GitHub-like fixture payloads.
- Maps raw endpoint-shaped payload dictionaries into the canonical internal
  snapshot shape.
- Preserves repository identity.
- Maps labels deterministically.
- Excludes issue-like records with `pull_request` markers from canonical issues.
- Maps pull endpoint records into canonical pull request records.
- Maps issue comments into canonical issue comments.
- Maps pull reviews into canonical pull request comments and review status.
- Maps check runs and statuses into canonical pull request CI/status summaries.
- Produces deterministic adapter output and order.
- Fails safely for missing repository payloads.
- Fails safely for missing pull payloads.
- Fails safely for malformed issue payloads.
- Fails safely for malformed pull request payloads.
- Does not mutate raw payloads.
- Does not call GitHub.
- Does not use network.
- Does not require secrets.
- Does not bypass the normalizer.

## Validation Commands Run

- `git status -sb`
- `git diff --check`
- Artifact 07 file inventory command from the sprint prompt.
- Token, credential-name, and live-host-pattern scan from the sprint prompt.
- Local-path scan from the sprint prompt.
- `git ls-files .env`
- Tracked Python cache checks from the sprint prompt.
- Artifact 07 pytest suite with bytecode and pytest cache disabled.
- Compile check with an isolated Python cache prefix outside the artifact tree.

## Test Results

- Artifact 07 pytest suite: 155 passed.
- Compile check: passed.
- Existing Sprint 7.1 through Sprint 7.8 tests remain preserved.

## Safety Scan Results

- `git diff --check` passed.
- `.env` remains untracked.
- No tracked `__pycache__` files.
- No tracked `.pyc` files.
- Local-path scan produced no matches.
- No real GitHub API call path was added.
- No GitHub authentication path was added.
- No GitHub SDK or provider dependency was added.
- No real LLM provider dependency was added.
- No real executor runtime was added.
- No file or database persistence was added beyond committed local fixture
  payload files.

Token and credential-name scan hits are intentional local guard-pattern, test,
and documentation strings. They are not secret values.

## What Sprint 7.9 Proves

- Local raw GitHub-like fixture payloads can be mapped into canonical internal
  snapshot-shaped data.
- Issue-like pull request markers are excluded from canonical issues.
- Pull endpoint records become canonical pull request records.
- Labels, comments, reviews, checks, and statuses are mapped deterministically.
- Mapped canonical snapshots normalize successfully.
- Mapped normalized snapshots pass through analyzer, fake proposal provider,
  policy guard, approval inbox, operator decision, ledger, and dry-run layers.
- Adapter output is deterministic.
- Adapter output order is deterministic.
- Adapter errors are safe and explicit.
- Adapter tests require no network.
- Adapter tests require no secrets.
- Adapter tests require no real GitHub provider.
- Prior Sprint 7.1 through Sprint 7.8 behavior remains covered by tests.

## What Sprint 7.9 Does Not Prove

- real GitHub reads
- real GitHub writes
- GitHub authentication
- GitHub App integration
- GitHub OAuth integration
- complete GitHub API payload coverage
- real GitHub integration
- real LLM integration
- real executor runtime
- production readiness

## Known Limitations

- Raw payloads are committed local fixtures only.
- Fixture coverage is intentionally narrow and contract-focused.
- The adapter does not authenticate.
- The adapter does not call live APIs.
- The adapter does not provide complete payload coverage.
- The adapter does not introduce real execution or persistence.

## Next Recommended Sprint

Artifact 7.10 - Real-Read Mode Evidence Gate, subject to Design Supervisor
approval.
