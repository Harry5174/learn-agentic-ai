# Artifact 5 Documentation

This directory is organized so Artifact 5 A5.3 is easy to review from GitHub
and easy for future IDE agents to navigate.

Artifact 5 - Approval-Gated Real GitHub Comment Adapter is initialized from the
completed Artifact 4 local/demo durable fake-client safety artifact.

A5.0 is the baseline/specification sprint. A5.1 adds safe client,
token-provider, and real-mode configuration boundaries. A5.2 adds remote
idempotency marker and reconciliation logic with fake/mocked clients. A5.3 adds
one approval-gated real GitHub issue-comment execution path behind explicit
server-side real-mode configuration.

The copied fake-client path remains the default runtime behavior. Real mode is
disabled by default, and no CI-style validation requires a GitHub token or live
GitHub network access.

## Read First

- [Artifact 5 real GitHub comment adapter spec](specs/artifact-5-real-github-comment-adapter.md): A5.3 safety contract and non-goals.
- [Remote idempotency and reconciliation](architecture/remote-idempotency-reconciliation.md): GitHub/SQLite crash window, marker format, reconciliation, and fail-closed behavior.
- [Manual real-mode smoke test](demos/manual-real-mode-smoke-test.md): optional disabled-by-default live smoke checklist.
- [Project status](status/project-status.md): current A5.3 status.
- [Known limitations](status/known-limitations.md): what A5.3 does not implement.
- [Roadmap](status/roadmap.md): A5.3 onward sequencing.
- [Artifact 4 vs Artifact 5](comparisons/artifact-4-vs-artifact-5.md): baseline comparison.
- [Interview notes](status/interview-notes.md): short explanation of the artifact.

## A5 Safety Topics

A5 docs cover:

- what Artifact 5 is
- what Artifact 5 is not
- why Artifact 4 is the baseline
- why local SQLite idempotency is insufficient for real GitHub execution
- GitHub/SQLite crash window
- remote idempotency marker format
- remote reconciliation behavior
- fail-closed behavior when marker lookup fails
- real-mode boundary
- fake-client default behavior
- server-side token handling requirements
- A5.1 token-provider and real-mode config boundaries
- A5.2 fake/mocked marker lookup and reconciliation boundaries
- A5.3 approval-gated real comment execution path
- marker is not authorization and does not bypass approval
- minimum-privilege GitHub token guidance
- repository allowlist requirements
- durable audit requirements
- real-mode testing strategy
- explicit non-goals
- known limitations
- A5.3 onward sprint roadmap

## Inherited Baseline Docs

The copied project still contains Artifact 4, Artifact 3, Artifact 2, and
Artifact 1 docs. Those pages are historical/source-baseline context unless an
A5 page says otherwise.

Useful inherited context:

- [Artifact 4 durable side-effect ledger spec](specs/artifact-4-durable-side-effect-ledger.md)
- [Persistence boundary](architecture/persistence-boundary.md)
- [Restart replay demo](demos/restart-replay-demo.md)
- [Durable audit demo](demos/durable-audit-demo.md)
- [Inherited GitHub comment demo](demos/github-comment-tool-demo.md)
- [Inherited adversarial GitHub side-effect safety](adversarial-github-side-effect-safety.md)

## Current Runtime Boundary

A5.3 adds one narrow real GitHub runtime path, but only when explicitly
configured by trusted server-side dependencies.

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

Automated tests remain mocked and must not require `.env`,
`AGENT_FACTORY_GITHUB_TOKEN`, or live GitHub access.
