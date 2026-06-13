# Project Status

## Project

**Title:** Artifact 4 - Durable Side-Effect Ledger and Approval Binding

**Copied baseline:** Artifact 3 - Approval-Gated GitHub Tool Harness

**A4.1 status:** SQLite Side-Effect Ledger implemented.

**A4.2 status:** Durable Approval Binding implemented.

**Principle:** The LLM proposes. The harness validates, authorizes, approval-gates, executes, and audits.

**Safety invariant:** Side-effect execution must require a matching persisted approval binding for the same `side_effect_id` and `validated_arguments_hash` before any replay-safe durable execution proof can be accepted.

## Current Artifact Status

Artifact 4 is currently at A4.2. It started with A4.0, a copied baseline from completed Artifact 3.

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

Artifact 4 has not implemented durable audit store yet. It still inherits Artifact 3 fake-client local/demo behavior for the main graph path. The durable stores are not yet integrated into the graph/service execution path.

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

## Inherited Runtime Baseline

The copied runtime still inherits completed Artifact 3 behavior:

- validated scalar tool arguments
- one approval-gated GitHub issue-comment skill path
- trusted repository allowlist policy
- explicit approval
- deterministic `validated_arguments_hash`
- deterministic `side_effect_id`
- process-local `InMemorySideEffectLedger`
- `FakeGitHubIssueCommentClient` simulated execution
- in-memory audit evidence
- adversarial tests for the fake-client side-effect boundary

This inherited behavior is local/demo only and fake-client-only.

## Current Persistence Status

The SQLite-backed durable stores exist but are not yet bound to the executing graph:

- `DurableSideEffectLedger` persists side-effect records in SQLite
- `DurableApprovalBindingStore` persists approval bindings in SQLite
- Both stores survive re-instantiation using the same SQLite file
- Approve/reject update both stores atomically in a single transaction

Still inherited from Artifact 3 runtime:

- graph checkpoints use in-memory state
- task/run state is process-local
- side-effect ledger in graph path is process-local
- audit events are not durably persisted

A4.2 defines and tests the durable approval binding store, but does not inject it into the application runtime yet.

## Future Durable-State Target

Future Artifact 4 implementation should target:

```text
SkillGraphService
-> DurableApprovalBindingStore
-> DurableSideEffectLedger
-> DurableAuditStore
-> SQLite
-> FakeGitHubIssueCommentClient
```

SQLite is the planned persistence boundary. Fake client execution remains the execution boundary. Real GitHub client remains out of scope.

## Explicitly Not Implemented

- durable audit store runtime code
- graph/service behavior changes
- API behavior changes
- approval behavior changes in graph path
- real GitHub client
- GitHub token loading
- real GitHub network execution
- OAuth/OIDC
- MCP
- frontend
- deployment
- production-readiness claim

## Latest Baseline Evidence

A4.2 should be validated with:

- `uv run pytest`
- `uv run ruff check .`
- `git diff --check`
- overclaim grep
- network/token grep

The latest validation results belong in the A4.2 completion report after the commit is created.
