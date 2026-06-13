# Project Status

## Project

**Title:** Artifact 4 - Durable Side-Effect Ledger and Approval Binding

**Copied baseline:** Artifact 3 - Approval-Gated GitHub Tool Harness

**A4.1 status:** SQLite Side-Effect Ledger implemented.

**Principle:** The LLM proposes. The harness validates, authorizes, approval-gates, executes, and audits.

**Safety invariant:** Future side-effect execution must require a matching persisted approval binding for the same `side_effect_id` and `validated_arguments_hash` before any replay-safe durable execution proof can be accepted.

## Current Artifact Status

Artifact 4 is currently at A4.1. It started with A4.0, a copied baseline from completed Artifact 3.

The current Artifact 4 folder is:

```text
03-agent-factory/xx-projects/03-durable-side-effect-ledger
```

The source baseline folder is:

```text
03-agent-factory/xx-projects/02-approval-gated-github-tool-harness
```

A4.1 implements the `DurableSideEffectLedger` backed by a SQLite boundary. It defines the `side_effect_records` table and validates proper status transitions without making the database available to the graph/service yet.

Artifact 4 has not implemented durable approval binding yet. It has not implemented a durable audit store yet. It still inherits Artifact 3 fake-client local/demo behavior for the main graph path.

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

Current runtime persistence is still inherited from Artifact 3:

- graph checkpoints use in-memory state
- task/run state is process-local
- side-effect ledger state is process-local
- audit events are not durably persisted
- approval decisions do not persist `validated_arguments_hash`
- approval decisions do not persist `side_effect_id`

- The SQLite side-effect ledger exists but is not yet bound to the executing graph.

A4.1 defines and tests the durable ledger, but does not inject it into the application runtime yet.

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

- durable approval binding runtime code
- durable audit store runtime code
- graph/service behavior changes
- API behavior changes
- approval behavior changes
- new runtime persistence tests
- real GitHub client
- GitHub token loading
- real GitHub network execution
- OAuth/OIDC
- MCP
- frontend
- deployment
- production-readiness claim

## Latest Baseline Evidence

A4.1 should be validated with:

- `uv run pytest`
- `uv run ruff check .`
- `git diff --check`
- stale-path grep
- overclaim grep

The latest validation results belong in the A4.1 completion report after the commit is created.
