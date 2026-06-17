# Project Status

**Artifact:** 5

**Title:** Artifact 5 - Approval-Gated Real GitHub Comment Adapter

**Current sprint:** A5.0 - Real-Adapter Safety Spec, Token Scope, and Remote
Idempotency Design

**Status:** Baseline/specification sprint implemented in documentation only.

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
issue-comment adapter. It does not implement the real adapter.

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
- A5.1 onward roadmap

## Runtime Status

A5.0 does not change runtime behavior.

The inherited runtime remains:

- local/demo
- fake-client-only
- approval-gated
- policy-checked
- durable-store capable through explicit dependency injection
- covered by fake/mocked automated tests

The copied fake-client GitHub issue-comment path remains the default behavior.

## Not Implemented In A5.0

A5.0 does not add:

- real GitHub client implementation
- token provider implementation
- environment token loading
- HTTP/network code
- real GitHub API calls
- new runtime side-effect behavior
- remote marker runtime code
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

A5.0 specifies, but does not implement, the future remote idempotency marker:

```html
<!-- agent_factory:v1 side_effect_id=<side_effect_id> args_hash=<validated_arguments_hash> -->
```

Future real mode must list existing issue comments and search for this exact
marker before any real post. If the marker exists, the harness must not post
again and must reconcile local state. If lookup fails or is ambiguous, the
harness must fail closed.

## Token Status

A5.0 adds token guidance only. It does not load or use a GitHub token.

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

A5.0 should validate with:

```bash
uv run pytest
uv run ruff check .
find tests -maxdepth 1 -type f -name "test_*.py" | sort | wc -l
uv run pytest --collect-only -q
```

The automated suite must remain fake/mocked only and must not require a GitHub
token.
