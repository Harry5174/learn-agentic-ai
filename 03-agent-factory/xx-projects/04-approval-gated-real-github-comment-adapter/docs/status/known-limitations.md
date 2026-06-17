# Known Limitations

This file keeps Artifact 5 A5.2 honest.

A5.1 adds safe client/token/config boundaries for a future approval-gated real
GitHub issue-comment adapter. A5.2 adds fake/mocked remote marker and
reconciliation logic, but it does not implement that adapter.

## Not Implemented

A5.2 does not implement:

- live real GitHub client execution
- HTTP/network code
- real GitHub API calls
- live remote marker lookup
- real GitHub remote reconciliation
- real mode enablement
- manual live smoke test
- OAuth/OIDC
- MCP
- frontend
- deployment
- PR creation
- branch creation
- issue creation
- repo file writes
- workflow dispatch
- multiple real GitHub tools

## Current Runtime Limit

The current runtime remains inherited from Artifact 4 and earlier artifacts.
It is local/demo and fake-client-only.

The fake-client GitHub issue-comment path can demonstrate validation, policy,
approval, durable side-effect records, durable approval bindings, durable audit
events, and restart/replay duplicate suppression when durable dependencies are
explicitly injected.

It does not perform a real GitHub API call.

A5.2 remote marker reconciliation uses fake/mocked listers only. It does not
call GitHub, does not post real comments, and does not enable real mode.

## SQLite Is Not Enough For Future Real Execution

SQLite-backed idempotency remains necessary, but it is insufficient by itself
for real GitHub execution because SQLite and GitHub cannot commit atomically.

The required crash window is:

```text
1. GitHub comment POST succeeds.
2. Process crashes before SQLite records succeeded.
3. Service restarts.
4. Local ledger is not succeeded.
5. Replay attempts execution.
6. Without remote marker lookup, duplicate real comment may be posted.
```

A5.2 adds the marker lookup and reconciliation logic with fake/mocked clients
only. Future real mode must still add live remote lookup and real posting only
after separate approval.

The marker is not authorization and does not bypass approval. A5.2
reconciliation does not authorize unapproved planned side effects; it only
operates on existing approved/executing local durable records.

## No Production Claims

Artifact 5 A5.2 is not production-ready.

It does not claim universal exactly-once execution. Future remote marker lookup
reduces duplicate-post risk for the scoped GitHub issue-comment path, but even
future real mode must be described with precise crash-window and ambiguity
boundaries.

## Token Limitations

A5.1 adds a server-side token-provider boundary for future real mode. The
default local/demo fake-client path does not load, validate, store, or use
GitHub tokens.

Future real mode must not accept tokens from request bodies, model output, tool
arguments, logs, audit rows, exception messages, or test snapshots.

## Testing Limitations

The automated suite remains fake/mocked only.

A5.2 does not add:

- a live GitHub smoke test
- a real token requirement
- CI that talks to GitHub
- real network assertions

Future live testing must be separately approved after real mode exists and must
use a single allowlisted test repository with minimum privileges.
