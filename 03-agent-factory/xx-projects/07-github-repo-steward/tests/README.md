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

Future test coverage needed:

- future 7.9 GitHub adapter tests

Current tests do not cover real executor runtime, GitHub adapter, or real
GitHub behavior.

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

Current tests do not cover:

- real executor runtime
- GitHub API read adapter
- real GitHub reads
- real GitHub writes
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
GitHub integration. Each future behavior needs implementation plus focused
tests in the sprint that adds it.
