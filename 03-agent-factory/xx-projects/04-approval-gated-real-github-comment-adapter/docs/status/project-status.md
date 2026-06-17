# Project Status

**Artifact:** 5

**Title:** Artifact 5 - Approval-Gated Real GitHub Comment Adapter

**Current sprint:** A5.4 - Real-Mode Adversarial and Crash-Window Safety Suite

**Status:** A5.4 adversarial real-mode safety tests and minimal hardening are
implemented for the existing approval-gated GitHub issue-comment list/create
path. Fake client remains the default and real mode remains disabled by
default.

## Current State

Artifact 5 has been initialized from completed Artifact 4:

```text
03-agent-factory/xx-projects/03-durable-side-effect-ledger
```

The new Artifact 5 workspace is:

```text
03-agent-factory/xx-projects/04-approval-gated-real-github-comment-adapter
```

A5.0 defines the safety design for an approval-gated real GitHub issue-comment
adapter. A5.1 adds client/interface, token-provider, and real-mode
configuration boundaries without enabling the real adapter. A5.2 adds remote
marker/reconciliation logic with fake/mocked clients. A5.3 adds the explicit
server-configured real execution path. A5.4 attacks that boundary with mocked
adversarial tests and narrow safety fixes.

## A5.0 Adds

A5.0 adds documentation for:

- what Artifact 5 is
- what Artifact 5 is not
- why Artifact 4 is the baseline
- why local SQLite idempotency is insufficient for real GitHub execution
- GitHub/SQLite crash window
- remote idempotency marker format
- remote reconciliation behavior
- fail-closed behavior when marker lookup fails
- ambiguous marker fail-closed behavior
- real-mode boundary
- fake-client default behavior
- server-side token handling
- fine-grained token guidance
- repository allowlist requirements
- durable audit requirements
- real-mode testing strategy
- explicit non-goals
- known limitations
- A5.1/A5.4 onward roadmap

## A5.1 Adds

A5.1 adds:

- `GitHubTokenProvider`
- `EnvironmentGitHubTokenProvider`
- `MissingGitHubTokenError`
- `GitHubRealModeConfig`
- `DisabledRealGitHubIssueCommentClient`
- safe credentials-unavailable failure construction
- tests proving fake client remains default
- tests proving real mode remains disabled by default
- tests proving missing or blank token values fail closed
- tests proving token-like values stay out of produced audit/results/failures
- docs confirming no real GitHub execution or network behavior exists

## A5.2 Adds

A5.2 adds:

- deterministic remote idempotency marker builder/parser
- fake/mocked-only `RemoteIssueComment` listing boundary
- marker lookup outcomes for found, absent, mismatch, ambiguous, and lookup failed
- durable reconciliation for existing approved/executing local records
- durable audit events for marker lookup and remote reconciliation
- crash-window simulation proving marker recovery does not post
- tests proving unapproved planned records are not authorized by marker text

## A5.3 Adds

A5.3 adds:

- narrow real GitHub issue-comment client using standard-library HTTP
- list issue comments and create issue comment only
- bounded pagination for complete-enough marker lookup
- explicit timeout handling
- safe GitHub HTTP, timeout, transport, and malformed-response failure mapping
- server-side real-mode graph/service injection points
- repository allowlist enforcement before token loading and network calls
- durable approval binding check before token loading
- local already-succeeded duplicate suppression before token loading
- remote marker lookup before posting
- remote marker found reconciliation without posting
- marker absent posting with deterministic marker appended to the comment body
- external comment id/url persistence
- durable audit events for real-mode safety decisions
- tests proving token and Authorization header values stay out of results/audit
- disabled-by-default optional manual smoke test documentation

## A5.4 Adds

A5.4 adds:

- adversarial token/header leakage tests
- hostile transport exception redaction tests
- repository allowlist bypass tests
- request/model control-plane smuggling tests
- approval/hash mutation tests
- remote marker spoofing tests
- ambiguous, quoted, duplicated, malformed, and extra-field marker tests
- GitHub HTTP, timeout, malformed response, and incomplete lookup tests
- crash-window replay tests through existing executing durable records
- minimal hardening for body/hash binding and approval-binding consistency
- minimal hardening for status-specific HTTP 409/429 failures
- minimal hardening for remote listing failure redaction
- minimal hardening for ambiguous marker classification
- minimal hardening for timeout/replay handling without blind same-call retry
- documentation updates for A5.4 scope and limitations

## Runtime Status

The default runtime remains:

- local/demo
- fake-client-only
- approval-gated
- policy-checked
- durable-store capable through explicit dependency injection
- covered by fake/mocked automated tests

The copied fake-client GitHub issue-comment path remains the default behavior.
Real GitHub execution is available only through explicit trusted server-side
real-mode config, token provider, durable stores, approval binding store, and
real client dependencies.

## Not Implemented In A5.4

A5.4 does not add:

- OAuth/OIDC
- MCP
- frontend
- deployment
- PR creation
- branch creation
- issue creation
- repo file writes
- workflow dispatch
- multiple real tools
- automated live GitHub tests
- manual live smoke execution by default
- arbitrary repository support
- production-ready guarantees
- production-grade audit guarantees
- universal exactly-once guarantees

## Remote Idempotency Status

A5.4 uses the remote idempotency marker for real-mode lookup and reconciliation:

```html
<!-- agent_factory:v1 side_effect_id=<side_effect_id> args_hash=<validated_arguments_hash> -->
```

A5.4 real mode lists existing issue comments and searches for this exact marker
before any real post. Fake/mocked automated tests prove marker-found,
marker-absent, mismatch, ambiguous, quoted, duplicated, extra-field, and
lookup-failed behavior. If lookup fails, is ambiguous, or cannot prove
complete-enough listing, the harness fails closed.

The remote marker is not authorization. A5.4 reconciliation does not authorize
unapproved planned side effects and does not create local durable records from
remote marker text.

## Token Status

A5.1 adds a server-side environment token-provider boundary. A5.4 uses that
boundary only after local gates pass. The default local/demo fake-client path
does not load or use a GitHub token.

A5.4 real mode should use:

- server-side token loading only
- fine-grained GitHub token preferred
- single allowlisted test repository
- Issues repository permission: read and write
- short expiration
- no Contents permission
- no Actions/workflows permission
- no broad repo scope

Tokens must not come from request bodies, model output, tool arguments, logs,
audit rows, exception messages, or test snapshots.

## Validation Expectation

A5.4 should validate with:

```bash
uv run pytest
uv run ruff check .
find tests -maxdepth 1 -type f -name "test_*.py" | sort | wc -l
uv run pytest --collect-only -q
```

The automated suite must remain fake/mocked only and must not require a GitHub
token. The optional manual smoke test is documented but not run by default.
