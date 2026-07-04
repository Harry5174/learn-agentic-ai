# Artifact 07 Tests

Sprint 7.0 was docs-only.

Sprint 7.1 adds local runtime tests for fixture snapshot loading and
normalization.

Sprint 7.2 adds local runtime tests for deterministic analyzer findings.

Sprint 7.3 adds local runtime tests for non-executing fake proposal drafts.

Sprint 7.4 adds local runtime tests for deterministic proposal policy
evaluation.

Sprint 7.5 adds local runtime tests for pending approval inbox item creation
from policy-allowed proposal drafts.

Sprint 7.6 adds local runtime tests for operator approve/reject decision
records on pending approval inbox items.

Sprint 7.6R is documentation-only and adds no runtime tests.

Sprint 7.7 adds local runtime tests for ledger/audit records created from
operator decisions and matching approval inbox items.

Sprint 7.8 adds local runtime tests for dry-run execution results created from
ledger/audit records and matching approval inbox items.

Sprint 7.9 adds local runtime tests for raw GitHub-like fixture adapter
contracts that map endpoint-shaped payloads into canonical internal snapshot
data.

Sprint 7.10 adds local runtime tests for the real-read evidence gate.

Coverage by sprint:

- 7.0 placeholder tests
- 7.1 fixture/normalizer tests
- 7.2 analyzer tests
- 7.3 proposal-boundary/fake-provider tests
- 7.4 policy guard tests
- 7.5 approval inbox tests
- 7.6 operator decision tests
- 7.7 ledger/audit-record tests
- 7.8 dry-run executor tests
- 7.9 GitHub-like read adapter contract tests
- 7.10 real-read evidence gate tests

Future test coverage needed:

- future 7.11 real-write readiness tests

Current tests do not cover real executor runtime, live GitHub reads, real
GitHub writes, or real GitHub behavior.

Current tests cover:

- fixture repo loading
- repository identity normalization
- issue normalization
- pull request normalization
- label normalization
- comment normalization
- CI/status summary normalization
- deterministic stale metadata representation
- safe rejection of missing top-level fixture fields
- safe rejection of missing issue fields
- safe rejection of missing pull request fields
- local operation without `GITHUB_TOKEN`, `OPENAI_API_KEY`, or
  `ANTHROPIC_API_KEY`
- structured analyzer findings
- deterministic analyzer finding IDs
- deterministic analyzer finding order
- issue missing reproduction finding
- stale issue without recorded maintainer response finding
- pull request failing CI finding
- pull request waiting for review finding
- analyzer behavior with an empty normalized snapshot
- analyzer no-mutation behavior
- analyzer operation without network sockets
- proposal model shape
- proposal validation helper behavior
- fake proposal draft generation from analyzer findings
- deterministic proposal IDs
- deterministic proposal order
- fake provider no-mutation behavior
- fake provider operation without network sockets
- structured policy evaluation records
- safe fake proposal drafts allowed for future operator review
- policy evaluation IDs
- policy evaluation order
- blocked proposals with reasons
- blocking missing approval requirements
- blocking non-draft execution status
- blocking high-risk proposals
- blocking unsupported proposal and target types
- blocking empty draft bodies
- blocking draft text that claims completed actions
- blocking local token-like guard-pattern strings
- policy guard no-mutation behavior
- policy guard operation without network sockets
- structured approval inbox item records
- policy-allowed proposal drafts entering the inbox
- blocked proposal drafts being excluded from the inbox
- pending operator review status on all inbox items
- future operator approval required on all inbox items
- deterministic approval inbox item IDs
- deterministic approval inbox order
- safe failure for missing, duplicate, extra, or mismatched policy evaluations
- approval inbox no-mutation behavior
- approval inbox operation without network sockets
- structured operator decision records
- local approved decision records
- local rejected decision records
- decision records with `execution_status="not_executed"`
- decision records with `ledger_status="not_recorded"`
- rejected decision rationale requirement
- invalid decision value rejection
- missing operator identity rejection
- duplicate decision rejection
- unknown inbox item rejection
- deterministic operator decision IDs
- deterministic operator decision order
- operator decision no-mutation behavior
- operator decision operation without `GITHUB_TOKEN`, `OPENAI_API_KEY`, or
  `ANTHROPIC_API_KEY`
- operator decision operation without network sockets
- structured ledger/audit records
- approved operator decisions ledgered locally
- rejected operator decisions ledgered locally
- ledger records preserving decision, proposal, inbox, operator, and rationale
  values
- ledger records with `execution_status="not_executed"`
- ledger records with `github_status="not_called"`
- ledger records with `executor_status="not_triggered"`
- mismatched decision/inbox data rejection
- duplicate ledger decision rejection
- extra ledger evidence-reference rejection
- empty ledger batch behavior
- deterministic ledger record IDs
- deterministic ledger record order
- ledger no-mutation behavior for decision records and inbox items
- ledger operation without `GITHUB_TOKEN`, `OPENAI_API_KEY`, or
  `ANTHROPIC_API_KEY`
- ledger operation without network sockets
- ledger operation without file creation
- structured dry-run execution result records
- approved ledgered decisions producing `dry_run_completed` results
- rejected ledgered decisions producing `dry_run_skipped` no-op results
- dry-run results preserving ledger, decision, proposal, inbox, and target
  values
- dry-run results with `execution_status="not_executed"`
- dry-run results with `github_status="not_called"`
- dry-run results with `external_side_effect_status="none"`
- dry-run results with
  `ledger_record_status="verified_local_audit_record"`
- mismatched ledger/inbox data rejection
- duplicate dry-run ledger record rejection
- missing dry-run inbox reference rejection
- empty dry-run batch behavior
- deterministic dry-run result IDs
- deterministic dry-run result order
- dry-run no-mutation behavior for ledger records and inbox items
- dry-run operation without `GITHUB_TOKEN`, `OPENAI_API_KEY`, or
  `ANTHROPIC_API_KEY`
- dry-run operation without network sockets
- dry-run operation without file creation
- raw GitHub-like fixture payload loading
- structured GitHub read adapter result records
- raw fixture mapping into canonical snapshot dictionaries
- issue-like pull request marker exclusion from canonical issues
- pull request endpoint mapping into canonical pull request records
- deterministic label mapping
- deterministic issue comment mapping
- deterministic pull review/comment mapping
- deterministic check/status summary mapping
- mapped snapshot normalization
- mapped normalized snapshot analyzer behavior
- mapped normalized snapshot fake proposal behavior
- mapped normalized snapshot policy guard behavior
- mapped normalized snapshot approval inbox behavior
- mapped normalized snapshot operator decision behavior
- mapped normalized snapshot ledger behavior
- mapped normalized snapshot dry-run behavior
- adapter deterministic output and order
- adapter no-mutation behavior for raw payloads
- adapter operation without `GITHUB_TOKEN`, `OPENAI_API_KEY`, or
  `ANTHROPIC_API_KEY`
- adapter operation without network sockets
- adapter safe failure for missing repository payloads
- adapter safe failure for missing pull payloads
- adapter safe failure for malformed issue payloads
- adapter safe failure for malformed pull request payloads
- structured real-read request records
- structured real-read gate evaluation records
- structured real-read evidence records
- fake/default gate allowance without credentials
- real-read request blocking without Product Owner authorization
- real-read request blocking without repository target
- real-read request blocking without safe credential metadata
- real-read request blocking without adapter boundary
- real-read request blocking when writes are allowed
- read-only preflight allowed metadata without GitHub calls
- evidence records for fake/default adapter path
- evidence records for blocked real-read path
- deterministic gate evaluation IDs
- deterministic gate evidence IDs
- gate no-mutation behavior for requests and evaluations
- gate operation without `GITHUB_TOKEN`, `OPENAI_API_KEY`, or
  `ANTHROPIC_API_KEY`
- gate operation without network sockets
- gate operation without file reads

Current tests do not cover:

- real executor runtime
- live GitHub reads
- real GitHub writes
- GitHub authentication
- real LLM integration
- no real side effects by default

Run the current Artifact 07 tests from this artifact directory with:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src PYTEST_ADDOPTS="-p no:cacheprovider" python -m pytest tests
```

Do not treat the fixture loader, normalizer, analyzer, or fake proposal draft
tests as evidence that future approval, ledger, executor, live GitHub, or real
LLM behavior exists. Do not treat policy guard tests as evidence of approval
decisions, ledger runtime, dry-run executor runtime, or real GitHub
integration. Do not treat approval inbox tests as evidence of operator
approval/rejection decisions, ledger runtime, dry-run executor runtime, or real
GitHub integration. Do not treat operator decision tests as evidence of
ledger/audit runtime, dry-run executor runtime, or real GitHub integration. Do
not treat ledger/audit-record tests as evidence of durable persistence, dry-run
executor runtime, executor runtime, GitHub adapter behavior, or real GitHub
integration. Do not treat dry-run executor tests as evidence of real execution,
real executor runtime, durable persistence, GitHub adapter behavior, or real
GitHub integration. Do not treat GitHub-like read adapter tests as evidence of
live GitHub reads, GitHub authentication, complete GitHub API coverage, real
GitHub behavior, real executor runtime, durable persistence, or real LLM
integration. Do not treat real-read evidence gate tests as evidence of live
GitHub reads, live GitHub authentication, GitHub write readiness, real executor
runtime, durable persistence, or real LLM integration. Each future behavior
needs implementation plus focused tests in the sprint that adds it.
