# Artifact 07 Tests

Sprint 7.0 was docs-only.

Sprint 7.1 adds local runtime tests for fixture snapshot loading and
normalization.

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

Current tests do not cover:

- deterministic repo analysis
- fake proposal provider
- policy guard rejection
- approval inbox behavior
- ledger/audit recording
- dry-run executor
- no real side effects by default

Run the Sprint 7.1 tests from this artifact directory with:

```bash
PYTHONPATH=src python -m pytest tests
```

Do not treat the fixture loader and normalizer tests as evidence that future
stewardship behavior exists. Each future behavior needs implementation plus
focused tests in the sprint that adds it.
