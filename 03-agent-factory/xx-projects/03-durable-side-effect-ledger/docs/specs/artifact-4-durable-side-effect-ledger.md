# Artifact 4 Durable Side-Effect Ledger Spec

## 1. Purpose

A4.0 defines durable-state semantics for Artifact 4 - Durable Side-Effect Ledger and Approval Binding.

A4.0 does not implement SQLite persistence. A4.0 does not add runtime durable ledger behavior. A4.0 does not add real GitHub execution. A4.0 does not add token loading. A4.0 does not make the project production-ready.

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

## 4. Storage Decision

Artifact 4 V1 should use SQLite.

Implementation guidance for future sprints:

- prefer Python stdlib `sqlite3`
- use small repository classes
- use temporary SQLite files in tests
- do not use Postgres, Redis, Docker Compose, or cloud infrastructure

No SQLite implementation exists in A4.0.

## 5. Side-Effect Record Schema

Future conceptual table/record:

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

## 6. Approval Binding Schema

Future conceptual table/record:

```text
approval_bindings
```

Minimum fields:

```text
approval_id
run_id
skill_id
step_id
tool_name
side_effect_id
validated_arguments_hash
approval_status
approved_by
reason
created_at
decided_at
```

Critical invariant:

```text
Execution requires approval_status = approved for the same side_effect_id and validated_arguments_hash.
```

Approval of one validated action must not authorize a later mutation of repository, issue number, comment body, tool name, skill ID, step ID, or side-effect ID.

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

## 11. Standalone Persistence Proof

A4.3 must first prove raw SQLite persistence before graph/service integration:

```text
1. Open SQLite file.
2. Write one side_effect_record.
3. Close/discard repository object.
4. Open a new repository object against the same SQLite file.
5. Read the same record back.
```

This is a future A4.3 acceptance requirement. It is not current A4.0 functionality.

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

A4.0 and Artifact 4 V1 durable-state work explicitly exclude:

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

## 14. Future Implementation Acceptance Checklist

This checklist is future-facing. It does not describe current A4.0 functionality.

### A4.1 Durable-State Contracts

- Define small durable repository interfaces.
- Define record models for side-effect records, approval bindings, and durable audit events.
- Keep models local/demo and SQLite-oriented.
- Do not wire runtime graph/service behavior yet unless separately approved.

### A4.2 SQLite Repository Skeleton

- Add SQLite-backed repository classes using stdlib `sqlite3`.
- Create tables on initialization for local/demo use.
- Store timestamps and JSON fields deterministically.
- Use temporary SQLite files in tests.
- Do not add Postgres, Redis, Docker Compose, cloud services, or Alembic unless separately approved.

### A4.3 Standalone Persistence Proof

- Open a SQLite file.
- Write one `side_effect_record`.
- Close/discard the repository object.
- Open a new repository object against the same SQLite file.
- Read the same record back.
- Prove this before graph/service integration.

### A4.4 Approval Binding Enforcement

- Persist approvals against `side_effect_id` and `validated_arguments_hash`.
- Require matching approved approval binding before execution.
- Reject mismatched hashes or side-effect IDs fail-closed.
- Preserve blocked vs rejected semantics.

### A4.5 Restart-Replay Proof

- Execute once with fake client.
- Persist succeeded side-effect evidence.
- Instantiate a fresh repository/service object against the same SQLite file.
- Replay the same side-effect ID.
- Prove fake client is not called again.
- Persist durable audit evidence for skipped duplicate / already succeeded replay.
