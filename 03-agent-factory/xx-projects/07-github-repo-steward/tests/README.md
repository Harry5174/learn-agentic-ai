# Artifact 07 Tests

Sprint 7.0 was docs-only.

Sprint 7.1 adds local runtime tests for fixture snapshot loading and
normalization.

Sprint 7.2 adds local runtime tests for deterministic analyzer findings.

Sprint 7.3 adds local runtime tests for non-executing fake proposal drafts.

Sprint 7.4 adds local runtime tests for deterministic proposal policy
evaluation.

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

Current tests do not cover:

- approval inbox behavior
- ledger/audit recording
- dry-run executor
- no real side effects by default

Run the current Artifact 07 tests from this artifact directory with:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src PYTEST_ADDOPTS="-p no:cacheprovider" python -m pytest tests
```

Do not treat the fixture loader, normalizer, analyzer, or fake proposal draft
tests as evidence that future approval, ledger, executor, live GitHub, or real
LLM behavior exists. Do not treat policy guard tests as evidence of approval
decisions, approval inbox runtime, ledger runtime, dry-run executor runtime, or
real GitHub integration. Each future behavior needs implementation plus focused
tests in the sprint that adds it.
