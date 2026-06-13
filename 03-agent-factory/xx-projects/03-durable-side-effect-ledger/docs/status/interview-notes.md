# Interview Notes

## One-Minute Summary

Artifact 4 - Durable Side-Effect Ledger and Approval Binding is the next step after the completed Artifact 3 approval-gated GitHub tool harness.

Artifact 3 proved a local/demo fake-client GitHub issue-comment path with validated scalar arguments, repository policy, approval, in-memory side-effect idempotency, fake-client execution, and audit evidence.

Artifact 4 asks the next safety question:

```text
If the same approved side effect is replayed after process restart, can the harness prove it will not execute twice?
```

A4.1 implements a SQLite-backed side-effect ledger. A4.2 implements durable approval binding. A4.3 integrates both stores into the fake-client GitHub comment execution path and proves restart/replay duplicate suppression after durable success has been recorded.

## What A4.1 Adds

A4.1 adds the SQLite-backed `DurableSideEffectLedger`:

- `side_effect_records` table with full lifecycle
- domain-driven status transitions (planned, approved, executing, succeeded, failed, skipped_duplicate, rejected, blocked)
- terminal state protection
- re-instantiation persistence test

## What A4.2 Adds

A4.2 adds the SQLite-backed `DurableApprovalBindingStore`:

- `approval_bindings` table with UNIQUE constraint on `side_effect_id`
- `ApprovalBindingStatus` enum (pending, approved, rejected, expired) separate from `DurableSideEffectStatus`
- `ApprovalBindingRecord` model
- domain-level approval-to-side-effect matching on run_id, skill_id, step_id, tool_name, and validated_arguments_hash
- one approval binding per side_effect_id enforced for V1
- approve/reject update both approval_bindings and side_effect_records in a single SQLite transaction
- expired approval does not mutate side-effect status (documented design decision)
- `assert_approved_for_action` pure read check for exact side_effect_id + validated_arguments_hash
- 9 controlled domain error types
- re-instantiation persistence test for approval bindings

A4.2 does not implement durable audit store. A4.2 does not integrate with graph/service execution. A4.2 does not provide full restart-safe side-effect execution. A4.2 does not execute fake client. A4.2 does not execute real GitHub calls.

## What A4.3 Adds

A4.3 adds restart-replay integration for the local/demo fake-client GitHub comment path:

- optional durable dependency injection into the graph/service execution context
- durable side-effect lookup before fake-client execution
- `DurableApprovalBindingStore.assert_approved_for_action` before first fake-client execution
- approved status requirement before `executing`
- fake-client execution through `FakeGitHubIssueCommentClient` only
- succeeded or failed execution evidence persisted in SQLite
- fresh store/context/fake-client object replay proof against the same SQLite file
- already-succeeded replay returns duplicate-suppressed evidence without calling the fake client
- already-succeeded replay preserves `side_effect_records.status = succeeded`
- persisted `executing` is treated as unsafe to retry
- failed terminal records do not auto-retry

A4.3 does not implement durable audit store. A4.3 does not add real GitHub execution, GitHub token loading, or production-grade exactly-once execution.

## What Remains Inherited

The copied runtime still inherits Artifact 3 fake-client local/demo behavior:

- one GitHub issue-comment skill path
- validated scalar arguments
- trusted repository allowlist policy
- explicit approval
- process-local side-effect ledger by default unless durable stores are explicitly injected
- fake-client execution
- in-memory audit evidence

Real GitHub execution remains out of scope.

## Why Durable Approval Binding Matters

Approval must bind to the exact validated action.

Execution must require:

```text
approval_status = approved
same side_effect_id
same validated_arguments_hash
```

That prevents an approval for one action from authorizing a mutated repository, issue number, comment body, tool, step, or side-effect ID.

A4.2 proves this invariant at the store level. A4.3 enforces it in the fake-client GitHub comment execution path before the fake client can be called.

## Why SQLite First

SQLite is the planned Artifact 4 persistence boundary because it is local, file-backed, deterministic in tests, and available through Python stdlib `sqlite3`.

A4.1 added SQLite code for the side-effect ledger. A4.2 adds SQLite code for approval bindings. A4.3 proves those stores can suppress duplicate fake-client execution after fresh objects are recreated with the same SQLite file.

## Strong Interview Framing

This is not a real GitHub automation tool and not production infrastructure.

It is a staged harness design showing how model-proposed side effects should be validated, approval-bound, recorded, replay-checked, and audited before any real external write is enabled.

A4.3 demonstrates restart-replay duplicate suppression for the local/demo fake-client GitHub comment path using SQLite-backed side-effect and approval records.

A4.3 does not prove production-grade exactly-once semantics across every crash window. If the fake client succeeds but the process dies before durable success is marked, that interrupted attempt remains outside the A4.3 proof.

## Current Non-Implementation Line

A4.3 did not add durable audit store runtime code, API behavior changes, a real GitHub client, token loading, OAuth/OIDC, MCP, frontend, deployment, production-readiness claims, or universal exactly-once claims.
