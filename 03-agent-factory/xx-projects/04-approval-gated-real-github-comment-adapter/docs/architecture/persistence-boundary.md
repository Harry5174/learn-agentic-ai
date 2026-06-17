# Persistence Boundary

Artifact 4 adds a durable-state design boundary before any real GitHub write can be considered.

A4.0 documents the future shape and acceptance requirements. A4.1 implements the side-effect ledger. A4.2 implements the approval binding store. A4.3 integrates both stores into the fake-client GitHub comment execution path through explicit runtime injection. A4.3.1 modularizes that restart/replay implementation and graph/tool boundaries without adding runtime behavior. A4.4 implements the durable audit store and adversarial persistence suite.

## Why Artifact 3 Is Not Enough

Artifact 3 uses `InMemorySideEffectLedger` for local/demo replay suppression. That proves the harness can check a side-effect ID before fake-client execution while the process is alive.

It is insufficient across restart because:

- ledger records disappear when the process exits
- approval decisions do not durably bind `side_effect_id` and `validated_arguments_hash`
- audit evidence is process-local
- duplicate replay after restart cannot be proven safe from memory alone

## Why Artifact 4 Adds SQLite

Artifact 4 uses SQLite as the local/demo persistence boundary. SQLite is enough for the portfolio proof because it is file-backed, simple, deterministic in tests, and available through Python stdlib `sqlite3`.

The target is restart-safe local/demo evidence, not production infrastructure.

Do not use Postgres, Redis, Docker Compose, or cloud infrastructure for Artifact 4 V1.

## Durable Data

Durable records implemented:

- side-effect records keyed by `side_effect_id` (A4.1)
- approval bindings keyed to `side_effect_id` and `validated_arguments_hash` (A4.2)
- durable audit events keyed by `event_id` with run_id and side_effect_id lookup (A4.4)
- status timestamps for planned, approved, executing, succeeded, failed, skipped duplicate, rejected, and blocked states
- safe hashes and previews for comment bodies, not full comment bodies by default
- succeeded and failed fake-client execution evidence for the A4.3 durable GitHub comment path
- restart-surviving audit evidence for execution, duplicate suppression, blocked attempts, and fake-client failures

## Current Durable Stores

### DurableSideEffectLedger (A4.1)

SQLite-backed store for side-effect records. Persists `side_effect_id`, lifecycle status, timestamps, and execution evidence.

### DurableApprovalBindingStore (A4.2)

SQLite-backed store for approval bindings. Persists approval decisions against exact `side_effect_id` and `validated_arguments_hash`.

Key properties:
- one approval binding per side_effect_id in V1
- domain-level matching on run_id, skill_id, step_id, tool_name, validated_arguments_hash
- approve/reject update both approval_bindings and side_effect_records in a single SQLite transaction
- expired approval does not mutate side-effect status
- `assert_approved_for_action` is a pure read check: no mutation, no execution

### DurableAuditStore (A4.4)

SQLite-backed store for local/demo durable audit events. Persists lifecycle evidence for the durable fake-client path. It remains an optional runtime dependency and is not placed in checkpointed graph state.

Key properties:
- `durable_audit_events` table
- list by run_id and side_effect_id
- deterministic ordering by `created_at, event_id`
- targeted unsafe metadata rejection before SQLite persistence
- local/demo audit evidence only, not production-grade audit

### A4.4 Durable GitHub Comment Execution

A4.4 injects durable side-effect, approval, and audit stores into the existing `post_github_issue_comment` path when tests or callers provide them explicitly. Default app startup remains compatible with the inherited in-memory path and does not require a SQLite file.

Execution sequence:

```text
validated GitHub comment arguments
-> deterministic validated_arguments_hash
-> deterministic side_effect_id
-> DurableSideEffectLedger lookup
-> DurableAuditStore execution_requested event when provided
-> already succeeded: return duplicate-suppressed evidence, no fake-client call
-> executing: return unsafe-to-retry evidence, no fake-client call
-> DurableApprovalBindingStore.assert_approved_for_action
-> DurableAuditStore approval_authorized event when provided
-> require side_effect_records.status = approved
-> DurableAuditStore execution_started event when provided
-> mark executing
-> DurableAuditStore fake_client_called event when provided
-> call FakeGitHubIssueCommentClient
-> mark succeeded or failed
-> DurableAuditStore execution_succeeded or execution_failed event when provided
```

The replay path preserves `succeeded`; it does not rewrite the durable side-effect record to `skipped_duplicate`.
Duplicate replay records `duplicate_suppressed` durable audit evidence when `DurableAuditStore` is provided.

## Process-Local Data That Remains

Artifact 4 V1 may still keep some local/demo state process-local unless a later sprint explicitly widens scope:

- demo API key identity configuration
- in-memory rate limiting
- LangGraph checkpoint behavior outside the approved durable side-effect proof
- fake proposer scenario selection
- local test helpers and fake clients

## Execution Boundary That Remains

Fake GitHub client remains the execution boundary.

Real GitHub client remains out of scope. GitHub token loading remains out of scope. Real GitHub network execution remains out of scope.

The future durable path should still execute only through `FakeGitHubIssueCommentClient` until a separately approved artifact or sprint designs real execution.

## Dataflow Diagram

```text
Validated action
-> side_effect_id
-> approval binding
-> durable side-effect record
-> durable audit event
-> fake-client execution / skipped duplicate
```

Current A4.4 durable execution boundary:

```text
SkillGraphService
-> DurableApprovalBindingStore
-> DurableSideEffectLedger
-> DurableAuditStore
-> SQLite
-> FakeGitHubIssueCommentClient
```

## Not Production Persistence

Artifact 4 V1 is still local/demo. SQLite persistence is intended to prove restart-replay semantics for one approval-gated fake-client side-effect path.

It is not:

- production compliance-grade audit
- high-availability storage
- cloud deployment architecture
- multi-operator concurrency control
- OAuth/OIDC security infrastructure
- a real GitHub write system
- production-ready

## Restart-Replay Proof Requirement

A valid restart-replay proof must create a fresh repository/service object against the same SQLite file after the first execution. Calling the same object twice only proves in-process idempotency and is not enough for Artifact 4.

A4.4 proves this for the fake-client GitHub comment path with fresh store/context/fake-client objects against the same SQLite file. The second fake client is not called, the durable side-effect record remains `succeeded`, and durable audit events remain queryable after restart.

A4.4 demonstrates duplicate suppression after durable success exists. It does not prove production-grade exactly-once semantics for the crash window where the fake client succeeds but the process dies before `side_effect_records` is marked `succeeded`. A4.4 provides local/demo durable audit evidence, not production-grade audit or compliance audit.
