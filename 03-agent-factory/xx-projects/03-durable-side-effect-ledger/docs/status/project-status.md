# Project Status

## Project

**Title:** Artifact 4 - Durable Side-Effect Ledger and Approval Binding

**Copied baseline:** Artifact 3 - Approval-Gated GitHub Tool Harness

**A4.0 status:** Baseline copy and durable-state specification.

**Principle:** The LLM proposes. The harness validates, authorizes, approval-gates, executes, and audits.

**Safety invariant:** Future side-effect execution must require a matching persisted approval binding for the same `side_effect_id` and `validated_arguments_hash` before any replay-safe durable execution proof can be accepted.

## Current Artifact Status

Artifact 4 starts with A4.0, a copied baseline from completed Artifact 3.

The current Artifact 4 folder is:

```text
03-agent-factory/xx-projects/03-durable-side-effect-ledger
```

The source baseline folder is:

```text
03-agent-factory/xx-projects/02-approval-gated-github-tool-harness
```

A4.0 is documentation/specification only. It establishes the durable-state design for future SQLite persistence, durable approval binding, durable side-effect records, durable audit events, and restart-replay semantics.

Artifact 4 has not implemented durable SQLite persistence yet. It has not implemented durable approval binding yet. It has not implemented a durable audit store yet. It still inherits Artifact 3 fake-client local/demo behavior.

Real GitHub execution remains out of scope.

## Implemented In A4.0

A4.0 adds or updates documentation only:

- Artifact 4 README and docs index
- durable-state spec
- persistence-boundary architecture doc
- Artifact 3 vs Artifact 4 comparison
- project status, roadmap, limitations, and interview notes
- parent/root artifact indexes

A4.0 keeps runtime behavior unchanged.

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

A4.0 defines future durable persistence semantics but does not implement them.

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

A4.0 did not add:

- SQLite implementation
- durable side-effect ledger runtime code
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

A4.0 should be validated with:

- `uv run pytest`
- `uv run ruff check .`
- `git diff --check`
- stale-path grep
- overclaim grep

The latest validation results belong in the A4.0 completion report after the commit is created.
