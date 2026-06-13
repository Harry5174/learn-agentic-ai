# Interview Notes

## One-Minute Summary

Artifact 4 - Durable Side-Effect Ledger and Approval Binding is the next step after the completed Artifact 3 approval-gated GitHub tool harness.

Artifact 3 proved a local/demo fake-client GitHub issue-comment path with validated scalar arguments, repository policy, approval, in-memory side-effect idempotency, fake-client execution, and audit evidence.

Artifact 4 asks the next safety question:

```text
If the same approved side effect is replayed after process restart, can the harness prove it will not execute twice?
```

A4.0 does not implement that behavior yet. It creates the Artifact 4 baseline and defines the durable-state specification before implementation.

## What A4.0 Adds

A4.0 adds docs/specification only:

- Artifact 4 project identity
- durable-state mission
- SQLite storage decision for future work
- side-effect record schema
- approval binding schema
- durable audit event schema
- status lifecycle and transitions
- restart-replay semantics
- standalone SQLite persistence proof requirement
- persistence-boundary architecture

## What Remains Inherited

The copied runtime still inherits Artifact 3 fake-client local/demo behavior:

- one GitHub issue-comment skill path
- validated scalar arguments
- trusted repository allowlist policy
- explicit approval
- process-local side-effect ledger
- fake-client execution
- in-memory audit evidence

Real GitHub execution remains out of scope.

## Why Durable Approval Binding Matters

Approval must bind to the exact validated action.

Future execution must require:

```text
approval_status = approved
same side_effect_id
same validated_arguments_hash
```

That prevents an approval for one action from authorizing a mutated repository, issue number, comment body, tool, step, or side-effect ID.

## Why SQLite First

SQLite is the planned Artifact 4 persistence boundary because it is local, file-backed, deterministic in tests, and available through Python stdlib `sqlite3`.

A4.0 does not add SQLite code. Future work should first prove standalone persistence before graph/service integration.

## Strong Interview Framing

This is not a real GitHub automation tool and not production infrastructure.

It is a staged harness design showing how model-proposed side effects should be validated, approval-bound, recorded, replay-checked, and audited before any real external write is enabled.

A4.0 is the design checkpoint. Runtime durable persistence comes later only after review.

## Current Non-Implementation Line

A4.0 did not add SQLite implementation, durable ledger runtime code, durable approval binding runtime code, durable audit store runtime code, graph/service behavior changes, API behavior changes, a real GitHub client, token loading, OAuth/OIDC, MCP, frontend, deployment, or production-readiness claims.
