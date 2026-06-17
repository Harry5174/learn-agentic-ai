# Artifact 4 Documentation

This directory is organized so Artifact 4 is easy to review from GitHub and
easy for future IDE agents to navigate.

Artifact 4 demonstrates a local/demo approval-gated real GitHub issue-comment
adapter. The fake client remains the default. An explicitly configured real mode
can perform one repository-allowlisted GitHub issue-comment side effect after
validated scalar arguments, durable approval binding, local durable ledger
checks, remote idempotency marker lookup/reconciliation, server-side token
loading, and durable audit recording. Automated tests use fake/mocked clients
and include adversarial crash-window safety coverage.

## Read First

- [Artifact 4 real GitHub comment adapter spec](specs/artifact-4-real-github-comment-adapter.md): safety contract and non-goals.
- [Remote idempotency and reconciliation](architecture/remote-idempotency-reconciliation.md): GitHub/SQLite crash window, marker format, reconciliation, and fail-closed behavior.
- [Manual real-mode smoke test](demos/manual-real-mode-smoke-test.md): optional disabled-by-default live smoke checklist.
- [Project status](status/project-status.md): current A4.5 status.
- [Known limitations](status/known-limitations.md): what Artifact 4 does not implement.
- [Roadmap](status/roadmap.md): completed and future sprint sequencing.
- [Artifact 3 vs Artifact 4](comparisons/artifact-3-vs-artifact-4.md): baseline comparison.
- [Interview notes](status/interview-notes.md): short explanation of the artifact.

## A5 Safety Topics

A5 docs cover:

- what Artifact 4 is
- what Artifact 4 is not
- why Artifact 3 is the baseline
- why local SQLite idempotency is insufficient for real GitHub execution
- GitHub/SQLite crash window
- remote idempotency marker format
- remote reconciliation behavior
- fail-closed behavior when marker lookup fails
- real-mode boundary
- fake-client default behavior
- server-side token handling requirements
- A4.1 token-provider and real-mode config boundaries
- A4.2 fake/mocked marker lookup and reconciliation boundaries
- A4.3 approval-gated real comment execution path
- A4.4 adversarial safety tests and crash-window replay hardening
- A4.5 documentation, demo, and portfolio packaging
- marker is not authorization and does not bypass approval
- minimum-privilege GitHub token guidance
- repository allowlist requirements
- durable audit requirements
- real-mode testing strategy
- explicit non-goals
- known limitations

## Inherited Baseline Docs

The copied project still contains Artifact 3, Artifact 2, Artifact 1, and
Artifact 0 docs. Those pages are historical/source-baseline context unless an
A5 page says otherwise.

Useful inherited context:

- [Artifact 3 durable side-effect ledger spec](specs/artifact-3-durable-side-effect-ledger.md)
- [Persistence boundary](architecture/persistence-boundary.md)
- [Restart replay demo](demos/restart-replay-demo.md)
- [Durable audit demo](demos/durable-audit-demo.md)
- [Inherited GitHub comment demo](demos/github-comment-tool-demo.md)
- [Inherited adversarial GitHub side-effect safety](adversarial-github-side-effect-safety.md)

## Current Runtime Boundary

The default runtime remains:

- local/demo
- fake-client-only
- approval-gated
- policy-checked
- durable-store capable through explicit dependency injection
- real mode disabled by default
- free of real GitHub API calls unless explicit real-mode config is injected
- free of GitHub token requirements for default local/demo execution
- covered by fake/mocked remote marker reconciliation tests
- covered by adversarial real-mode safety tests

Automated tests remain mocked and must not require `.env`,
`AGENT_FACTORY_GITHUB_TOKEN`, or live GitHub access.
