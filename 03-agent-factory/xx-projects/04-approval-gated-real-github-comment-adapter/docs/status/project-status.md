# Project Status

**Artifact:** 5

**Title:** Artifact 5 — Approval-Gated Real GitHub Comment Adapter

**Current sprint:** A5.5 — Demo, Safety Notes, and Portfolio Packaging

**Status:** Artifact 5 is complete as a local/demo approval-gated real GitHub
issue-comment adapter. Documentation, demo guides, safety notes, and portfolio
packaging are finalized.

## Final Claim

Artifact 5 demonstrates a local/demo approval-gated real GitHub issue-comment
adapter. The fake client remains the default. An explicitly configured real mode
can perform one repository-allowlisted GitHub issue-comment side effect after
validated scalar arguments, durable approval binding, local durable ledger
checks, remote idempotency marker lookup/reconciliation, server-side token
loading, and durable audit recording. Automated tests use fake/mocked clients
and include adversarial crash-window safety coverage.

## Current State

Artifact 5 was initialized from completed Artifact 4:

```text
03-agent-factory/xx-projects/03-durable-side-effect-ledger
```

The Artifact 5 workspace is:

```text
03-agent-factory/xx-projects/04-approval-gated-real-github-comment-adapter
```

## Sprint History

### A5.0 — Real-Adapter Safety Spec, Token Scope, And Remote Idempotency Design

A5.0 defined the safety design: real-mode boundary, fake-client default,
server-side token handling, minimum-privilege token guidance, repository
allowlist requirements, GitHub/SQLite crash window, remote idempotency marker
format, remote reconciliation behavior, fail-closed ambiguity behavior, durable
audit requirements, future test strategy, and explicit non-goals.

### A5.1 — GitHub Client Interface And Server-Side Token Provider

A5.1 added `GitHubTokenProvider`, `EnvironmentGitHubTokenProvider`,
`MissingGitHubTokenError`, `GitHubRealModeConfig`,
`DisabledRealGitHubIssueCommentClient`, safe credentials-unavailable failure
construction, and tests proving fake client remains default, real mode remains
disabled by default, missing or blank token values fail closed, and token-like
values stay out of produced audit/results/failures.

### A5.2 — Remote Idempotency Marker And Reconciliation

A5.2 added deterministic remote idempotency marker builder/parser, fake/mocked
`RemoteIssueComment` listing boundary, marker lookup outcomes (found, absent,
mismatch, ambiguous, lookup failed), durable reconciliation for existing
approved/executing local records, durable audit events for marker lookup and
remote reconciliation, crash-window simulation proving marker recovery does not
post, and tests proving unapproved planned records are not authorized by marker
text.

### A5.3 — Approval-Gated Real Comment Execution Path

A5.3 added one narrow real GitHub issue-comment client using standard-library
HTTP, list issue comments and create issue comment only, bounded pagination for
complete-enough marker lookup, explicit timeout handling, safe GitHub HTTP
failure mapping, server-side real-mode graph/service injection points,
repository allowlist enforcement before token loading and network calls, durable
approval binding check before token loading, local already-succeeded duplicate
suppression before token loading, remote marker lookup before posting, remote
marker found reconciliation without posting, marker absent posting with
deterministic marker appended, external comment id/url persistence, durable
audit events for real-mode safety decisions, token redaction tests, and
disabled-by-default optional manual smoke test documentation.

### A5.4 — Real-Mode Adversarial And Crash-Window Safety Suite

A5.4 added adversarial token/header leakage tests, hostile transport exception
redaction tests, repository allowlist bypass tests, request/model control-plane
smuggling tests, approval/hash mutation tests, remote marker spoofing tests,
ambiguous/quoted/duplicated/malformed/extra-field marker tests, GitHub HTTP/
timeout/malformed-response/incomplete-lookup tests, crash-window replay tests
through existing executing durable records, minimal hardening for body/hash
binding, approval-binding consistency, status-specific HTTP failures, remote
listing failure redaction, ambiguous marker classification, and timeout/replay
handling without blind same-call retry.

### A5.5 — Demo, Safety Notes, And Portfolio Packaging

A5.5 packaged the completed Artifact 5 as a clear, interview-ready portfolio
artifact. README was rewritten as the portfolio entry point. Documentation
index, spec, architecture docs, project status, known limitations, roadmap,
interview notes, manual smoke-test guide, artifact comparison, and parent
workspace README were updated. No runtime behavior was changed.

## Runtime Status

The default runtime remains:

- local/demo
- fake-client-only
- approval-gated
- policy-checked
- durable-store capable through explicit dependency injection
- covered by fake/mocked automated tests

The fake-client GitHub issue-comment path remains the default behavior. Real
GitHub execution is available only through explicit trusted server-side
real-mode config, token provider, durable stores, approval binding store, and
real client dependencies.

## Not Implemented

Artifact 5 does not implement:

- OAuth/OIDC
- MCP
- frontend or operator console
- deployment
- PR creation, branch creation, issue creation, repo file writes, or workflow
  dispatch
- multiple real tools
- automated live GitHub tests
- manual live smoke execution by default
- arbitrary repository support
- broad GitHub automation
- production-ready guarantees
- production-grade audit guarantees
- universal exactly-once guarantees

## Remote Idempotency Status

The remote idempotency marker is used for real-mode lookup and reconciliation:

```html
<!-- agent_factory:v1 side_effect_id=<side_effect_id> args_hash=<validated_arguments_hash> -->
```

Real mode lists existing issue comments and searches for this exact marker
before any real post. Fake/mocked automated tests prove marker-found,
marker-absent, mismatch, ambiguous, quoted, duplicated, extra-field, and
lookup-failed behavior. If lookup fails, is ambiguous, or cannot prove
complete-enough listing, the harness fails closed.

The remote marker is not authorization. Reconciliation does not authorize
unapproved planned side effects and does not create local durable records from
remote marker text.

## Token Status

The server-side environment token-provider boundary loads
`AGENT_FACTORY_GITHUB_TOKEN` from the server-side environment only after local
gates pass. The default local/demo fake-client path does not load or use a
GitHub token.

Tokens must not come from request bodies, model output, tool arguments, logs,
audit rows, exception messages, or test snapshots.

## Validation

Artifact 5 validates with:

```bash
uv run pytest
uv run ruff check .
find tests -maxdepth 1 -type f -name "test_*.py" | sort | wc -l
uv run pytest --collect-only -q
```

The automated suite remains fake/mocked only and does not require a GitHub
token. The optional manual smoke test is documented but not run by default.
