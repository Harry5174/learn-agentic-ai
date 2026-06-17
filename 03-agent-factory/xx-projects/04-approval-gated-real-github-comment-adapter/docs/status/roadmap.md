# Roadmap

This roadmap is intentionally narrow. Artifact 5 should move toward one future
real external side effect without weakening the core thesis:

```text
The LLM proposes.
The harness decides.
```

## A5.0 - Real-Adapter Safety Spec, Token Scope, And Remote Idempotency Design

Status: implemented as documentation/specification only.

A5.0 creates the Artifact 5 workspace from completed Artifact 4 and defines:

- real-mode boundary
- fake-client default behavior
- server-side token handling requirements
- minimum-privilege token guidance
- repository allowlist requirements
- GitHub/SQLite crash window
- remote idempotency marker format
- remote reconciliation behavior
- fail-closed ambiguity behavior
- durable audit requirements
- future test strategy
- explicit non-goals

A5.0 does not add real GitHub execution, token loading, network code, runtime
remote marker lookup, or a live smoke test.

## A5.1 - Marker Contract And Mocked Reconciliation Tests

Recommended next step.

Possible scope:

- harness-owned marker construction contract
- marker parser or exact-match helper
- mocked remote comment shapes
- tests for marker found, not found, ambiguous, mismatch, and lookup failure
- fail-closed behavior tests
- no real GitHub client
- no token loading
- no network calls

## A5.2 - Remote Client Interface Boundary

Possible scope:

- define a narrow issue-comment listing/posting interface
- keep fake/mocked implementation as default
- add explicit real-mode-disabled behavior
- define external comment id/url persistence shape
- test that unsupported real mode fails closed
- no live GitHub API calls unless separately approved

## A5.3 - Server-Side Token Provider Design

Possible scope:

- token provider interface
- redaction rules
- token-source rejection tests
- docs for fine-grained token setup
- no tokens from request/model/tool/audit/logs
- no hardcoded token values

Implementation of environment token loading should require separate approval.

## A5.4 - Allowlisted Real Adapter Implementation

Possible future scope only after A5.1-A5.3 safety work is accepted:

- one real GitHub issue-comment adapter
- explicit real-mode configuration
- single allowlisted test repository
- remote marker lookup before post
- fail-closed ambiguity handling
- durable reconciliation and audit
- mocked automated tests remain default

## A5.5 - Separately Approved Manual Live Smoke Test

Possible future scope only after real mode exists:

- manually run against a single allowlisted test repository
- use a short-lived fine-grained token
- Issues permission: read and write
- no Contents permission
- no Actions/workflows permission
- no broad repo scope

No CI-style validation should require a GitHub token.

## Premature Work To Avoid

Do not add these as incidental cleanup:

- OAuth/OIDC
- MCP
- frontend
- deployment
- PR creation
- branch creation
- issue creation beyond the one future issue-comment path
- repo file writes
- workflow dispatch
- multiple real tools
- production-ready claims
- universal exactly-once claims
