# Roadmap

This roadmap is intentionally narrow. Artifact 5 demonstrates one safely
controlled real external side effect without weakening the core thesis:

```text
The LLM proposes.
The harness decides.
```

## A5.0 — Real-Adapter Safety Spec, Token Scope, And Remote Idempotency Design

Status: complete.

A5.0 created the Artifact 5 workspace from completed Artifact 4 and defined the
real-mode boundary, fake-client default, server-side token handling requirements,
minimum-privilege token guidance, repository allowlist requirements,
GitHub/SQLite crash window, remote idempotency marker format, remote
reconciliation behavior, fail-closed ambiguity behavior, durable audit
requirements, future test strategy, and explicit non-goals.

## A5.1 — GitHub Client Interface And Server-Side Token Provider

Status: complete.

A5.1 added safe client interface, server-side environment token-provider
boundary, missing-token fail-closed behavior, real-mode config boundary,
disabled real-client boundary, and token redaction/source-rejection tests.

## A5.2 — Remote Idempotency Marker And Reconciliation

Status: complete.

A5.2 added deterministic marker builder/parser, fake/mocked remote comment
listing, marker lookup outcomes (found, absent, mismatch, ambiguous, lookup
failed), durable reconciliation for existing approved/executing local records,
and proof that marker text does not authorize unapproved planned side effects.

## A5.3 — Approval-Gated Real Comment Execution Path

Status: complete.

A5.3 added one narrow real GitHub issue-comment client using standard-library
HTTP, bounded pagination, repository allowlist enforcement, remote marker lookup
before posting, marker-found reconciliation, marker-absent posting with
deterministic marker appended, external comment id/url persistence, and durable
audit for real-mode safety decisions.

## A5.4 — Real-Mode Adversarial And Crash-Window Safety Suite

Status: complete.

A5.4 added adversarial token/header leakage tests, hostile transport exception
redaction, repository allowlist bypass tests, request/model control-plane
smuggling tests, approval/hash mutation tests, marker spoofing and ambiguity
tests, HTTP/timeout/malformed-response failure tests, crash-window replay
through executing durable records, and narrow safety hardening.

## A5.5 — Demo, Safety Notes, And Portfolio Packaging

Status: complete.

A5.5 packaged the completed Artifact 5 as a clear, interview-ready portfolio
artifact. Documentation, demo guides, safety notes, known limitations, and
portfolio framing were updated. No runtime behavior was changed.

## Future — Optional Manual Real-Mode Smoke Test

Possible future scope only if the Product Owner explicitly approves it:

- manually run against a single allowlisted test repository
- use a short-lived fine-grained token
- Issues permission: read and write
- no Contents permission
- no Actions/workflows permission
- no broad repo scope

No CI-style validation should require a GitHub token.

## Future — Evidence Review And Narrow Hardening

Possible future scope after the current artifact is accepted:

- review real-mode evidence and audit rows
- clarify any remaining operator docs
- harden the single issue-comment path only if needed
- keep fake client as the default
- avoid expanding into general GitHub automation

## Premature Work To Avoid

Do not add these as incidental cleanup:

- OAuth/OIDC
- MCP
- frontend
- deployment
- PR creation
- branch creation
- issue creation beyond the one issue-comment path
- repo file writes
- workflow dispatch
- multiple real tools
- production-ready claims
- universal exactly-once claims
