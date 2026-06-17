# Project Status

**Artifact:** 5

**Title:** Artifact 5 - Approval-Gated Real GitHub Comment Adapter

**Current sprint:** A5.2 - Remote Idempotency Marker and Reconciliation

**Status:** Fake/mocked remote marker reconciliation implemented. Real GitHub
execution remains disabled and unwired.

## Current State

Artifact 5 has been initialized from completed Artifact 4:

```text
03-agent-factory/xx-projects/03-durable-side-effect-ledger
```

The new Artifact 5 workspace is:

```text
03-agent-factory/xx-projects/04-approval-gated-real-github-comment-adapter
```

A5.0 defines the safety design for a future approval-gated real GitHub
issue-comment adapter. A5.1 adds client/interface, token-provider, and
real-mode configuration boundaries without enabling the real adapter. A5.2 adds
remote marker/reconciliation logic with fake/mocked clients only.

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
- future real-mode testing strategy
- explicit non-goals
- known limitations
- A5.1/A5.2 onward roadmap

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

## Runtime Status

A5.2 does not enable real GitHub runtime behavior.

The inherited runtime remains:

- local/demo
- fake-client-only
- approval-gated
- policy-checked
- durable-store capable through explicit dependency injection
- covered by fake/mocked automated tests
- remote marker reconciliation tested with fake/mocked listers only

The copied fake-client GitHub issue-comment path remains the default behavior.

## Not Implemented In A5.2

A5.2 does not add:

- live real GitHub client execution
- HTTP/network code
- real GitHub API calls
- new runtime side-effect behavior
- live remote marker lookup
- real GitHub remote reconciliation
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
- manual live smoke test

## Remote Idempotency Status

A5.2 implements the remote idempotency marker for fake/mocked reconciliation:

```html
<!-- agent_factory:v1 side_effect_id=<side_effect_id> args_hash=<validated_arguments_hash> -->
```

Future real mode must list existing issue comments and search for this exact
marker before any real post. In A5.2, fake/mocked lookup proves marker-found,
marker-absent, mismatch, ambiguous, and lookup-failed behavior. If lookup fails
or is ambiguous, the harness fails closed.

The remote marker is not authorization. A5.2 reconciliation does not authorize
unapproved planned side effects and does not create local durable records from
remote marker text.

## Token Status

A5.1 adds a server-side environment token-provider boundary. The default
local/demo fake-client path does not load or use a GitHub token.

Future real mode should use:

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

A5.2 should validate with:

```bash
uv run pytest
uv run ruff check .
find tests -maxdepth 1 -type f -name "test_*.py" | sort | wc -l
uv run pytest --collect-only -q
```

The automated suite must remain fake/mocked only and must not require a GitHub
token.
