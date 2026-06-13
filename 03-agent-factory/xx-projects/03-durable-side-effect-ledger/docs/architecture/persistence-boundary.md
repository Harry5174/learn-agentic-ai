# Persistence Boundary

Artifact 4 adds a durable-state design boundary before any real GitHub write can be considered.

A4.0 documents the future shape and acceptance requirements. A4.1 implements the side-effect ledger. A4.2 implements the approval binding store.

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
- status timestamps for planned, approved, executing, succeeded, failed, skipped duplicate, rejected, and blocked states
- safe hashes and previews for comment bodies, not full comment bodies by default

Future durable records:

- durable audit events for lifecycle evidence (not yet implemented)

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
- `assert_approved_for_action` is a pure read check — no mutation, no execution

Neither store is yet integrated into the graph/service execution path.

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

Target store boundary:

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

A4.2 proves approval binding persistence across re-instantiation. Full restart-replay proof with fake-client execution is deferred to A4.3.
