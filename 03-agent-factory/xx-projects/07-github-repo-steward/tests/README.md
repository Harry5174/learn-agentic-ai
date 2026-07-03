# Artifact 07 Tests

Sprint 7.0 was docs-only.

Sprint 7.1 adds local runtime tests for fixture snapshot loading and
normalization.

Sprint 7.2 adds local runtime tests for deterministic analyzer findings.

Sprint 7.3 adds local runtime tests for non-executing fake proposal drafts.

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

Current tests do not cover:

- policy guard rejection
- approval inbox behavior
- ledger/audit recording
- dry-run executor
- no real side effects by default

Run the Sprint 7.2 tests from this artifact directory with:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src PYTEST_ADDOPTS="-p no:cacheprovider" python -m pytest tests
```

Do not treat the fixture loader, normalizer, analyzer, or fake proposal draft
tests as evidence that future policy, approval, ledger, executor, live GitHub,
or real LLM behavior exists. Each future behavior needs implementation plus
focused tests in the sprint that adds it.
