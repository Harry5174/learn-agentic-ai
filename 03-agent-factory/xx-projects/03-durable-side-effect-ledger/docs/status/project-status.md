# Project Status

## Project

**Title:** Artifact 4 - Durable Side-Effect Ledger and Approval Binding

**Copied baseline:** Artifact 3 - Approval-Gated GitHub Tool Harness

**A4.1 status:** SQLite Side-Effect Ledger implemented.

**A4.2 status:** Durable Approval Binding implemented.

**A4.3 status:** Restart-Replay Integration implemented.

**Principle:** The LLM proposes. The harness validates, authorizes, approval-gates, executes, and audits.

**Safety invariant:** Side-effect execution must require a matching persisted approval binding for the same `side_effect_id` and `validated_arguments_hash` before any replay-safe durable execution proof can be accepted.

## Current Artifact Status

Artifact 4 is currently at A4.3. It started with A4.0, a copied baseline from completed Artifact 3.

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

Artifact 4 has not implemented durable audit store yet. The default API startup still does not require a SQLite file.

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
- Both stores survive re-instantiation using the same SQLite file
- Approve/reject update both stores atomically in a single transaction
- A4.3 execution requires an approved binding for the exact side effect before the fake client can be called
- A4.3 replay after durable success does not call the fake client again

Still inherited from Artifact 3/default runtime:

- graph checkpoints use in-memory state
- task/run state is process-local
- default app startup uses process-local side-effect ledger behavior
- audit events are not durably persisted

A4.3 does not turn the default API into a durable SQLite-backed product surface.

## Future Durable-State Target

Current A4.3 durable execution proof:

```text
SkillGraphService
-> DurableApprovalBindingStore
-> DurableSideEffectLedger
-> SQLite
-> FakeGitHubIssueCommentClient
```

Future A4.4 may add `DurableAuditStore`. SQLite is the persistence boundary for the local/demo proof. Fake client execution remains the execution boundary. Real GitHub client remains out of scope.

## Explicitly Not Implemented

- durable audit store runtime code
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

A4.3 demonstrates duplicate suppression after durable success has been recorded. It does not prove production-grade exactly-once semantics across every crash window. If the fake client call succeeds but the process dies before `side_effect_records` is marked `succeeded`, A4.3 does not prove universal duplicate suppression for that interrupted attempt.

## Latest Baseline Evidence

A4.3 should be validated with:

- `uv run pytest tests/test_restart_replay_integration.py`
- `uv run pytest`
- `uv run ruff check .`
- `git diff --check`
- overclaim grep
- network/token grep

The latest validation results belong in the A4.3 IDE evidence report after the commit is created.
