# Project Status

## Project

**Title:** Artifact 4 - Durable Side-Effect Ledger and Approval Binding

**Copied baseline:** Artifact 3 - Approval-Gated GitHub Tool Harness

**A4.1 status:** SQLite Side-Effect Ledger implemented.

**A4.2 status:** Durable Approval Binding implemented.

**A4.3 status:** Restart-Replay Integration implemented.

**A4.3.1 status:** Modularization and Runtime Boundary Cleanup implemented.

**A4.4 status:** Durable Audit Store and Adversarial Persistence Suite implemented.

**Principle:** The LLM proposes. The harness validates, authorizes, approval-gates, executes, and audits.

**Safety invariant:** Side-effect execution must require a matching persisted approval binding for the same `side_effect_id` and `validated_arguments_hash` before any replay-safe durable execution proof can be accepted.

## Current Artifact Status

Artifact 4 is currently at A4.4. It started with A4.0, a copied baseline from completed Artifact 3.

The current Artifact 4 folder is:

```text
03-agent-factory/xx-projects/03-durable-side-effect-ledger
```

The source baseline folder is:

```text
03-agent-factory/xx-projects/02-approval-gated-github-tool-harness
```

A4.1 implements the `DurableSideEffectLedger` backed by a SQLite boundary. It defines the `side_effect_records` table and validates proper status transitions without making the database available to the graph/service yet.

A4.2 implements the `DurableApprovalBindingStore` backed by SQLite. It defines the `approval_bindings` table, persists approval decisions against exact `side_effect_id` and `validated_arguments_hash`, and enforces one binding per side effect in V1. Approve and reject transitions update both the approval binding and the side-effect record in a single SQLite transaction. Expired approvals do not mutate side-effect status.

A4.3 integrates the durable ledger and durable approval binding into the fake-client GitHub comment execution path through explicit runtime injection. A4.3 proves restart/replay duplicate suppression after durable success exists by recreating fresh store/context/fake-client objects against the same SQLite file.

A4.3.1 modularized the restart/replay implementation and graph/tool boundaries without adding runtime behavior.

A4.4 implements local/demo durable audit events and adversarial persistence tests. It adds `durable_audit_events`, `DurableAuditStore`, optional runtime audit-store injection, and restart-surviving evidence for successful execution, duplicate suppression, blocked attempts, and fake-client failure. The default API startup still does not require a SQLite file.

Real GitHub execution remains out of scope.

## Implemented In A4.1

A4.1 implements the first slice of durable state:
- `DurableSideEffectLedger` using SQLite
- `side_effect_records` schema
- Domain-driven transition rules (terminal state protection)
- Fresh repository re-instantiation persistence test

- Artifact 4 README and docs index
- durable-state spec
- persistence-boundary architecture doc
- Artifact 3 vs Artifact 4 comparison
- project status, roadmap, limitations, and interview notes
- parent/root artifact indexes

A4.1 keeps runtime graph/service behavior unchanged.

## Implemented In A4.2

A4.2 implements durable approval binding:
- `DurableApprovalBindingStore` using SQLite
- `approval_bindings` schema with UNIQUE constraint on `side_effect_id`
- `ApprovalBindingStatus` enum (pending, approved, rejected, expired) separate from `DurableSideEffectStatus`
- `ApprovalBindingRecord` model
- Domain-level approval-to-side-effect matching (run_id, skill_id, step_id, tool_name, validated_arguments_hash)
- One approval binding per side_effect_id enforced for V1
- Approval status lifecycle with terminal state protection
- `assert_approved_for_action` pure read check for exact side_effect_id + validated_arguments_hash
- Approve/reject update both approval_bindings and side_effect_records in a single SQLite transaction
- Expired approval does not mutate side-effect record status
- Re-instantiation persistence test for approval bindings
- 9 controlled domain error types
- No fake-client execution, no real GitHub execution, no graph/service integration

## Implemented In A4.3

A4.3 implements restart-replay integration:

- optional durable store dependencies in the GitHub comment execution context
- optional durable store injection through `SkillGraphService` and graph construction
- durable execution path for `post_github_issue_comment`
- deterministic `validated_arguments_hash` and `side_effect_id` reuse
- durable side-effect lookup before fake-client execution
- already-succeeded replay returns duplicate-suppressed evidence without calling the fake client
- already-succeeded replay preserves `side_effect_records.status = succeeded`
- durable approval assertion for exact `side_effect_id` + `validated_arguments_hash` before first fake-client execution
- approved status requirement before `executing`
- `executing` persisted status treated as unsafe to retry
- fake-client failure marks the durable side effect `failed`
- failed terminal records do not auto-retry
- fresh SQLite-backed store/context/fake-client object tests

A4.3 does not implement durable audit store, real GitHub execution, GitHub token loading, a second GitHub tool, or production-grade exactly-once execution.

## Implemented In A4.3.1

A4.3.1 implements behavior-preserving modularization:

- split restart/replay tests by behavior
- extracted durable GitHub comment execution and result-shaping helpers
- extracted selected graph routing, metadata, policy, validation, and execution-context helpers
- preserved fake-client-only restart/replay behavior and explicit durable dependency injection

A4.3.1 does not add durable audit store, real GitHub execution, token loading, API behavior changes, or production-grade exactly-once claims.

## Implemented In A4.4

A4.4 implements durable local/demo audit evidence and adversarial persistence tests:

- `durable_audit_events` SQLite table
- `DurableAuditStore` using Python stdlib `sqlite3`
- durable audit event model and event-type enum
- deterministic audit listing with `ORDER BY created_at, event_id`
- targeted metadata safety checks that reject known unsafe keys and token-like values
- optional `durable_audit_store` runtime dependency on `ToolExecutionContext`
- durable audit events for successful execution: execution_requested, approval_authorized, execution_started, fake_client_called, execution_succeeded
- durable audit events for duplicate replay: execution_requested, duplicate_suppressed
- durable audit events for blocked attempts: execution_requested, execution_blocked
- durable audit events for fake-client failure: execution_requested, approval_authorized, execution_started, fake_client_called, execution_failed
- fail-closed behavior when required pre-execution audit evidence cannot be written
- adversarial persistence tests for approval mismatch, side-effect status, restart/replay, failure, metadata safety, and fake-client-only boundaries

A4.4 does not add real GitHub execution, GitHub token loading, a second GitHub tool, API startup changes, production-grade audit, compliance audit, or universal exactly-once claims.

## Inherited Runtime Baseline

The default copied runtime still inherits completed Artifact 3 behavior:

- validated scalar tool arguments
- one approval-gated GitHub issue-comment skill path
- trusted repository allowlist policy
- explicit approval
- deterministic `validated_arguments_hash`
- deterministic `side_effect_id`
- process-local `InMemorySideEffectLedger` unless durable stores are explicitly injected
- `FakeGitHubIssueCommentClient` simulated execution
- in-memory audit evidence
- adversarial tests for the fake-client side-effect boundary

This behavior is local/demo only and fake-client-only.

## Current Persistence Status

The SQLite-backed durable stores are integrated into the fake-client GitHub comment path through explicit dependency injection:

- `DurableSideEffectLedger` persists side-effect records in SQLite
- `DurableApprovalBindingStore` persists approval bindings in SQLite
- `DurableAuditStore` persists local/demo audit events in SQLite when explicitly injected
- Durable stores survive re-instantiation using the same SQLite file
- Approve/reject update both stores atomically in a single transaction
- A4.3 execution requires an approved binding for the exact side effect before the fake client can be called
- A4.3 replay after durable success does not call the fake client again
- A4.4 durable audit events survive fresh store re-instantiation and explain execution, duplicate, blocked, and failed outcomes

Still inherited from Artifact 3/default runtime:

- graph checkpoints use in-memory state
- task/run state is process-local
- default app startup uses process-local side-effect ledger behavior
- durable audit events are only persisted when `DurableAuditStore` is explicitly injected

A4.3 does not turn the default API into a durable SQLite-backed product surface.

## Future Durable-State Target

Current A4.4 durable execution proof:

```text
SkillGraphService
-> DurableApprovalBindingStore
-> DurableSideEffectLedger
-> DurableAuditStore
-> SQLite
-> FakeGitHubIssueCommentClient
```

SQLite is the persistence boundary for the local/demo proof. Fake client execution remains the execution boundary. Real GitHub client remains out of scope.

## Explicitly Not Implemented

- API behavior changes
- real GitHub client
- GitHub token loading
- real GitHub network execution
- OAuth/OIDC
- MCP
- frontend
- deployment
- production-readiness claim
- universal exactly-once claim

## Restart-Replay Limitation

A4.4 demonstrates duplicate suppression and durable local/demo audit evidence after durable success has been recorded. It does not prove production-grade exactly-once semantics across every crash window. If the fake client call succeeds but the process dies before `side_effect_records` is marked `succeeded`, A4.4 does not prove universal duplicate suppression for that interrupted attempt. A4.4 is not production-grade audit.

## Latest Baseline Evidence

A4.4 should be validated with:

- focused durable audit and adversarial persistence tests
- `uv run pytest`
- `uv run ruff check .`
- `git diff --check`
- overclaim grep
- network/token grep

The latest validation results belong in the A4.4 IDE evidence report after the commit is created.
