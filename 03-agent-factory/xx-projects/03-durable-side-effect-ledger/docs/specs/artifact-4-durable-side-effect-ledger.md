# Artifact 4 Durable Side-Effect Ledger Spec

## 1. Purpose

A4.0 defines durable-state semantics for Artifact 4 - Durable Side-Effect Ledger and Approval Binding.

A4.1 implements the `DurableSideEffectLedger` backed by SQLite. A4.1 does not add durable approval binding. A4.1 does not add real GitHub execution. A4.1 does not add token loading. A4.1 does not make the project production-ready.

A4.2 implements the `DurableApprovalBindingStore` backed by SQLite. A4.2 persists approval decisions against exact `side_effect_id` and `validated_arguments_hash`. A4.2 does not add durable audit store. A4.2 does not integrate with graph/service execution. A4.2 does not provide full restart-safe side-effect execution. A4.2 does not execute fake client. A4.2 does not execute real GitHub calls.

This spec defines the records, approval bindings, state transitions, restart-replay guarantees, and future acceptance requirements that must exist before the harness can safely move toward real side effects.

## 2. Durable-State Mission

Make approval-gated side-effect execution durable, replay-safe, and auditable across process restarts before enabling any real GitHub write.

The core proof question is:

```text
If the same approved side effect is replayed after process restart, can the harness prove it will not execute twice?
```

## 3. Architecture Boundary

Future target architecture:

```text
SkillGraphService
-> DurableApprovalBindingStore
-> DurableSideEffectLedger
-> DurableAuditStore
-> SQLite
-> FakeGitHubIssueCommentClient
```

SQLite is the persistence boundary for Artifact 4. Fake GitHub client remains the execution boundary. Real GitHub client remains out of scope.

The future durable stores must be owned by harness code, not model output. Model-proposed arguments remain untrusted until validated by existing registry and proposal-validation layers.

A4.1 implements `DurableSideEffectLedger`. A4.2 implements `DurableApprovalBindingStore`. Both are backed by SQLite. Graph/service integration is deferred to a future sprint.

## 4. Storage Decision

Artifact 4 V1 should use SQLite.

Implementation guidance for future sprints:

- prefer Python stdlib `sqlite3`
- use small repository classes
- use temporary SQLite files in tests
- do not use Postgres, Redis, Docker Compose, or cloud infrastructure

A basic SQLite ledger implementation exists in A4.1. A durable approval binding store exists in A4.2. Neither is yet wired into the graph/service.

## 5. Side-Effect Record Schema

Table:

```text
side_effect_records
```

Minimum fields:

```text
side_effect_id
run_id
skill_id
step_id
tool_name
validated_arguments_hash
status
repository
issue_number
comment_body_hash
comment_body_preview
created_at
updated_at
approved_at
started_at
executed_at
skipped_at
failed_at
external_result_json
failure_json
```

Decision: do not store full `comment_body` by default in V1. Store `comment_body_hash` plus a short redacted/safe preview.

If full comment body storage is needed later, it requires separate approval.

Implemented in A4.1.

## 6. Approval Binding Schema

Table:

```text
approval_bindings
```

Fields:

```text
approval_id TEXT PRIMARY KEY
run_id TEXT NOT NULL
skill_id TEXT NOT NULL
step_id TEXT NOT NULL
tool_name TEXT NOT NULL
side_effect_id TEXT NOT NULL UNIQUE
validated_arguments_hash TEXT NOT NULL
approval_status TEXT NOT NULL
requested_by TEXT
decided_by TEXT
reason TEXT
created_at TEXT NOT NULL
decided_at TEXT
expires_at TEXT
```

Critical invariant:

```text
Execution requires approval_status = approved for the same side_effect_id and validated_arguments_hash.
```

Approval of one validated action must not authorize a later mutation of repository, issue number, comment body, tool name, skill ID, step ID, or side-effect ID.

Constraints:
- `approval_id` is PRIMARY KEY (unique)
- `side_effect_id` has UNIQUE constraint (one binding per side effect in V1)
- No SQL-level foreign key — domain-level checks enforce the relationship

Implemented in A4.2.

## 6.1 Approval Binding Status Lifecycle

`ApprovalBindingStatus` is a separate enum from `DurableSideEffectStatus` and from the existing graph-level `ApprovalStatus`.

Values:

```text
pending
approved
rejected
expired
```

Terminal statuses:

```text
approved
rejected
expired
```

Allowed transitions:

```text
pending -> approved
pending -> rejected
pending -> expired
```

Forbidden transitions:

```text
approved -> rejected
approved -> expired
rejected -> approved
expired -> approved
expired -> rejected
```

## 6.2 Approval-to-Side-Effect Interaction

When approval is decided, the following side-effect status updates apply:

```text
approved -> side_effect_records planned -> approved
rejected -> side_effect_records planned -> rejected
expired -> side_effect_records remains planned (no mutation)
```

V1 design decision: expired approval does not mutate side_effect_records status. Expired is an approval-binding state, not a side-effect execution state.

Approve and reject transitions update both `approval_bindings` and `side_effect_records` in a single SQLite transaction to avoid partial state.

Implemented in A4.2.

## 7. Durable Audit Event Schema

Future conceptual table/record:

```text
durable_audit_events
```

Minimum fields:

```text
event_id
run_id
side_effect_id
event_type
actor_id
message
metadata_json
created_at
```

This is not a production compliance-grade audit system. It is a local/demo durable evidence store for side-effect lifecycle events.

Not yet implemented.

## 8. Status Lifecycle

Final Artifact 4 V1 statuses:

```text
planned
approved
executing
succeeded
failed
skipped_duplicate
rejected
blocked
```

Valid transitions:

```text
planned -> approved
planned -> rejected
planned -> blocked

approved -> executing

executing -> succeeded
executing -> failed

succeeded -> skipped_duplicate on replay evidence
```

Terminal statuses:

```text
succeeded
failed
skipped_duplicate
rejected
blocked
```

## 9. Required Lifecycle Decisions

### Failed Is Terminal

`failed` is terminal in Artifact 4 V1. No automatic or manual retry path exists. Retry requires a new side-effect plan, new `side_effect_id`, and new approval.

### Blocked Has A Concrete Meaning

`blocked` means deterministic policy/config denial before human approval.

Difference:

```text
blocked:
  system denied before human approval
  example: repository not allowed

rejected:
  human rejected after approval was requested
```

Blocked behavior:

```text
planned -> blocked only
blocked is terminal
blocked does not create approval request
blocked does not execute
blocked must be auditable
```

### Planned Can Persist

`planned` records may persist without approval. `planned` records are queryable. `planned` records cannot execute without a matching approved approval binding.

### Skipped Duplicate Is Replay Evidence

`skipped_duplicate` is a replay outcome/evidence status, not a normal forward execution path.

## 10. Restart-Replay Semantics

Core proof sequence:

```text
1. service_1 creates or loads SQLite file.
2. GitHub comment action is validated and planned.
3. Human approval is persisted against side_effect_id + validated_arguments_hash.
4. Fake client executes once.
5. side_effect_id is recorded as succeeded.
6. service_1 shuts down.
7. service_2 starts with the same SQLite file.
8. Same side_effect_id is replayed.
9. Fake client is not called again.
10. Durable ledger returns skipped_duplicate / already_succeeded evidence.
11. Durable audit explains what happened.
```

A restart-replay test must instantiate a fresh repository/service object against the same SQLite file. Calling the same object twice is not sufficient.

Not yet fully proven. A4.2 proves approval binding persistence across re-instantiation. Full restart-replay proof is deferred to A4.3.

## 11. Standalone Persistence Proof

Proven in A4.1 for side-effect records and in A4.2 for approval bindings:

```text
1. Open SQLite file.
2. Write one side_effect_record / approval_binding.
3. Close/discard repository/store object.
4. Open a new repository/store object against the same SQLite file.
5. Read the same record back.
```

Both `tests/test_durable_side_effect_ledger.py` and `tests/test_durable_approval_binding.py` contain re-instantiation persistence tests.

## 12. Failure Behavior

Future failure behavior:

```text
fake-client failure is recorded as failed
failed is terminal in V1
failure is durably auditable
failure does not become success
failure does not trigger automatic retry
failure does not expose secrets
```

Failure metadata must avoid secrets and full sensitive payloads. A redacted failure shape is required before persistence.

## 13. Non-Goals

Artifact 4 V1 durable-state work explicitly excludes:

```text
real GitHub API calls
GitHub token loading
real GitHub client
workflow dispatch
PR creation
repo file writes
issue creation
branch creation
MCP
OAuth/OIDC
JWT validation
frontend
Postgres
Redis
Docker Compose
cloud deployment
live LLM HTTP mode
multi-agent behavior
production audit claims
production readiness
```

## 14. Implementation Acceptance Checklist

This checklist tracks the implementation of Artifact 4.

### A4.1 SQLite Side-Effect Ledger (Completed)

- Define small durable repository interfaces.
- Define record models for side-effect records.
- Keep models local/demo and SQLite-oriented.
- Add SQLite-backed repository class using stdlib `sqlite3`.
- Create `side_effect_records` table on initialization.
- Store timestamps and JSON fields deterministically.
- Use temporary SQLite files in tests.
- Prove standalone persistence (re-instantiation test).

### A4.2 Durable Approval Binding (Completed)

- Define `ApprovalBindingStatus` enum separate from `DurableSideEffectStatus`.
- Define `ApprovalBindingRecord` model.
- Add `DurableApprovalBindingStore` class using stdlib `sqlite3`.
- Create `approval_bindings` table with UNIQUE constraint on `side_effect_id`.
- Persist approvals against `side_effect_id` and `validated_arguments_hash`.
- Require matching fields (run_id, skill_id, step_id, tool_name, validated_arguments_hash).
- Reject mismatched hashes or side-effect IDs fail-closed.
- Enforce one approval binding per side_effect_id in V1.
- Approve/reject update both stores in a single SQLite transaction.
- Expired approval does not mutate side-effect status.
- Add `assert_approved_for_action` pure read check.
- Add 9 controlled domain error types.
- Prove approval binding persistence (re-instantiation test).

### A4.3 Graph Integration and Restart-Replay Proof (Future)

- Integrate `DurableApprovalBindingStore` and `DurableSideEffectLedger` into main execution path.
- Execute once with fake client.
- Persist succeeded side-effect evidence.
- Instantiate a fresh repository/service object against the same SQLite file.
- Replay the same side-effect ID.
- Prove fake client is not called again.
- Persist durable audit evidence for skipped duplicate / already succeeded replay.

### A4.4 Durable Audit Store (Future)

- Add `durable_audit_events` table.
- Add `DurableAuditStore` class.
- Persist durable audit explanation for lifecycle events.
