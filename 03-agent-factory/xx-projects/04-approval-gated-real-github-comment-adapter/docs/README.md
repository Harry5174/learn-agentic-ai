# Artifact 5 Documentation

This directory is organized so Artifact 5 A5.1 is easy to review from GitHub
and easy for future IDE agents to navigate.

Artifact 5 - Approval-Gated Real GitHub Comment Adapter is initialized from the
completed Artifact 4 local/demo durable fake-client safety artifact.

A5.0 is the baseline/specification sprint. A5.1 adds safe client,
token-provider, and real-mode configuration boundaries only.

No real GitHub posting, HTTP/network code, real GitHub API call, or runtime
remote marker implementation exists in A5.1. The copied fake-client path remains
the default runtime behavior, and no CI-style validation requires a GitHub
token.

## Read First

- [Artifact 5 real GitHub comment adapter spec](specs/artifact-5-real-github-comment-adapter.md): A5.1 safety contract and non-goals.
- [Remote idempotency and reconciliation](architecture/remote-idempotency-reconciliation.md): GitHub/SQLite crash window, marker format, reconciliation, and fail-closed behavior.
- [Project status](status/project-status.md): current A5.1 status.
- [Known limitations](status/known-limitations.md): what A5.1 does not implement.
- [Roadmap](status/roadmap.md): A5.2 onward sequencing.
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
- minimum-privilege GitHub token guidance
- repository allowlist requirements
- durable audit requirements
- future real-mode testing strategy
- explicit non-goals
- known limitations
- A5.2 onward sprint roadmap

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

A5.1 does not add real GitHub runtime behavior.

The inherited runtime remains:

- local/demo
- fake-client-only
- approval-gated
- policy-checked
- durable-store capable through explicit dependency injection
- real mode disabled by default
- free of real GitHub API calls
- free of GitHub token requirements for default local/demo execution
- free of runtime remote marker lookup

Future real-mode work must be separately specified, implemented, tested, and
approved.
