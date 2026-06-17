# Known Limitations

This file keeps Artifact 5 A5.4 honest.

A5.1 adds safe client/token/config boundaries for an approval-gated real GitHub
issue-comment adapter. A5.2 adds fake/mocked remote marker and reconciliation
logic. A5.3 adds one explicit server-configured real issue-comment execution
path. A5.4 adds adversarial tests and minimal safety hardening for that path.

## Not Implemented

A5.4 does not implement:

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
- automated live GitHub tests
- manual live smoke execution by default
- arbitrary repository support
- production-ready guarantees
- production-grade audit guarantees
- universal exactly-once guarantees

## Current Runtime Limit

The default runtime remains inherited from Artifact 4 and earlier artifacts. It
is local/demo and fake-client-only.

The fake-client GitHub issue-comment path can demonstrate validation, policy,
approval, durable side-effect records, durable approval bindings, durable audit
events, and restart/replay duplicate suppression when durable dependencies are
explicitly injected.

It does not perform a real GitHub API call unless trusted server-side real-mode
dependencies are explicitly injected.

A5.4 real mode is narrow: list issue comments, check the marker, and post one
issue comment only for an exact allowlisted repository after durable approval.
Request bodies, model output, tool arguments, and approval payloads cannot
enable real mode or provide tokens.

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

A5.4 applies marker lookup and reconciliation before posting. If marker lookup
fails, is ambiguous, or cannot prove complete-enough listing, the harness fails
closed and does not post.

The marker is not authorization and does not bypass approval. A5.4
reconciliation does not authorize unapproved planned side effects; it only
operates on existing approved/executing local durable records.

## No Production Claims

Artifact 5 A5.4 is not production-ready and does not claim production-grade
audit behavior.

It does not claim universal exactly-once execution. Remote marker lookup reduces
duplicate-post risk for the scoped GitHub issue-comment path, but real mode must
be described with precise crash-window and ambiguity boundaries.

Known remote limitations include bounded pagination, remote comment deletion,
and human-edited marker text. If marker lookup exceeds the configured page
bound, pagination cannot be parsed, a marker is missing after remote deletion,
or marker text is quoted/duplicated/malformed/edited in a way the harness cannot
classify as exactly one clean marker, the harness fails closed.

## Token Limitations

A5.1 adds a server-side token-provider boundary for real mode. The default
local/demo fake-client path does not load, validate, store, or use GitHub
tokens.

A5.4 real mode must not accept tokens from request bodies, model output, tool
arguments, logs, audit rows, exception messages, or test snapshots.

## Testing Limitations

The automated suite remains fake/mocked only.

A5.4 does not add:

- a live GitHub smoke execution by default
- a real token requirement
- CI that talks to GitHub
- real network assertions

Live testing must be separately approved and must use a single allowlisted test
repository with minimum privileges. The optional manual smoke guide is present
but was not run as part of A5.4 automated validation.
