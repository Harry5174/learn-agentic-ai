# Known Limitations

This file keeps Artifact 4 honest.

## Status

Artifact 4 is a local/demo artifact. It is not production-ready.

The fake client remains the default. Real mode is disabled by default.
Automated tests use fake/mocked clients and do not call GitHub or require
credentials. The manual smoke test was not run in A5.5.

## Not Implemented

Artifact 4 does not implement:

- OAuth/OIDC
- MCP
- frontend or operator console
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
- broad GitHub automation
- production-ready guarantees
- production-grade audit guarantees
- universal exactly-once guarantees

## Operational Constraints

- **One issue-comment operation only.** The real adapter supports list and
  create for GitHub issue comments. No other GitHub operation is implemented.
- **One allowlisted repository for manual test.** The prepared manual test
  target is `Harry5174/artifact-5-github-comment-test`. No arbitrary repository
  support exists.
- **Real mode disabled by default.** Real mode requires explicit trusted
  server-side configuration injection. Request bodies, model output, and tool
  arguments cannot enable real mode or provide tokens.
- **Manual smoke test not run unless separately approved.** The optional manual
  smoke-test guide is documented but requires explicit Product Owner approval
  before any live execution.

## No Distributed Transaction With GitHub

SQLite-backed idempotency remains necessary, but it is insufficient by itself
for real GitHub execution because SQLite and GitHub cannot commit atomically.
There is no distributed transaction between the two systems.

The required crash window is:

```text
1. GitHub comment POST succeeds.
2. Process crashes before SQLite records succeeded.
3. Service restarts.
4. Local ledger is not succeeded.
5. Replay attempts execution.
6. Without remote marker lookup, duplicate real comment may be posted.
```

The adapter applies marker lookup and reconciliation before posting. If marker
lookup fails, is ambiguous, or cannot prove complete-enough listing, the harness
fails closed and does not post.

The marker is not authorization and does not bypass approval. Reconciliation
operates only on existing approved/executing local durable records.

## No Universal Exactly-Once Guarantee

Artifact 4 does not claim universal exactly-once execution. Remote marker lookup
reduces duplicate-post risk for the scoped GitHub issue-comment path, but the
following limitations remain:

- **Remote marker can be deleted or edited by humans.** If a human deletes or
  edits the marker text on GitHub, the harness may not detect a prior post.
- **GitHub availability and rate limits can block execution.** GitHub API
  failures, rate limits, and timeouts are handled with fail-closed behavior but
  can prevent the adapter from completing execution or lookup.
- **Bounded pagination limitation.** If the issue has more comments than the
  configured page bound allows, marker lookup may be incomplete. The harness
  fails closed when pagination completeness is uncertain.

## No Production Claims

Artifact 4 is not production-ready and does not claim production-grade audit
behavior. It is a local/demo safety artifact demonstrating staged progression
from fake-client to one real external side effect.

## Token Limitations

The server-side token-provider boundary loads `AGENT_FACTORY_GITHUB_TOKEN` from
the server-side environment. The default local/demo fake-client path does not
load, validate, store, or use GitHub tokens.

Real mode must not accept tokens from request bodies, model output, tool
arguments, logs, audit rows, exception messages, or test snapshots.

## Testing Limitations

The automated suite remains fake/mocked only.

Artifact 4 does not add:

- a live GitHub smoke execution by default
- a real token requirement
- CI that talks to GitHub
- real network assertions

Live testing must be separately approved and must use a single allowlisted test
repository with minimum privileges. The optional manual smoke guide is present
but was not run as part of A5.5 validation.
