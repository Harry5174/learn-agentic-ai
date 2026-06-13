# Roadmap

This roadmap is intentionally narrow. Artifact 4 - Durable Side-Effect Ledger and Approval Binding starts with A4.0 as a baseline/spec sprint copied from completed Artifact 3.

Artifact 4 moves from in-memory side-effect safety toward restart-safe durable side-effect safety. It does not move to real GitHub execution.

## A4.0 Baseline Copy And Durable-State Spec

A4.0 created the Artifact 4 folder from completed Artifact 3 and defined the durable-state design before implementation.

A4.0 includes:

- Artifact 4 project identity
- durable-state specification
- persistence-boundary architecture doc
- Artifact 3 vs Artifact 4 comparison
- status, roadmap, limitations, and interview notes
- parent index updates

A4.0 does not implement SQLite persistence, durable runtime behavior, real GitHub execution, or token loading.

Status: Completed.

## A4.1 SQLite Side-Effect Ledger

A4.1 implements the first slice of durable state.

Scope implemented:

- durable side-effect record model
- SQLite connection manager and side_effect_records table
- `DurableSideEffectLedger` with state transition validation
- Re-instantiation persistence test

A4.1 does not integrate the ledger into the runtime execution path.

Status: Completed.

## A4.2 Durable Approval Binding

A4.2 implements durable approval binding backed by SQLite.

Scope implemented:

- `ApprovalBindingStatus` enum (pending, approved, rejected, expired) separate from `DurableSideEffectStatus`
- `ApprovalBindingRecord` model
- `DurableApprovalBindingStore` with full create/read/transition/assertion methods
- `approval_bindings` table with UNIQUE constraint on side_effect_id
- domain-level approval-to-side-effect matching (run_id, skill_id, step_id, tool_name, validated_arguments_hash)
- one approval binding per side_effect_id in V1
- approve/reject update both approval_bindings and side_effect_records in a single SQLite transaction
- expired approval does not mutate side_effect_records status
- `assert_approved_for_action` pure read check for exact side_effect_id + validated_arguments_hash
- 9 controlled domain error types
- re-instantiation persistence test for approval bindings

A4.2 does not implement durable audit store. A4.2 does not integrate with graph/service execution. A4.2 does not provide full restart-safe side-effect execution. A4.2 does not execute fake client. A4.2 does not execute real GitHub calls.

A4.2 proves approval bindings can persist in SQLite and authorize only the exact side_effect_id and validated_arguments_hash after store re-instantiation.

Status: Completed.

## A4.3 Graph Integration and Restart-Replay Proof

A4.3 implements restart-replay integration for the local/demo fake-client GitHub comment path.

Scope implemented:

- optional durable store injection into `SkillGraphService` and the graph-built GitHub comment execution context
- integration of `DurableApprovalBindingStore` and `DurableSideEffectLedger` into `post_github_issue_comment`
- deterministic `validated_arguments_hash` and deterministic `side_effect_id`
- approved execution path: assert durable approval, require approved side-effect status, mark executing, call `FakeGitHubIssueCommentClient`, mark succeeded or failed
- restart/replay test with fresh store/context/fake-client objects against the same SQLite file
- duplicate replay after success returns already_succeeded / duplicate-suppressed evidence
- duplicate replay after success preserves `side_effect_records.status = succeeded`
- persisted `executing` status returns unsafe-to-retry evidence and does not call the fake client
- failed terminal side effects do not auto-retry

A4.3 does not add durable audit store. A4.3 does not execute real GitHub calls. A4.3 does not load GitHub tokens. A4.3 does not prove production-grade exactly-once semantics across crash windows between fake-client success and durable success marking.

Status: Completed.

## A4.3.1 Modularization and Runtime Boundary Cleanup

A4.3.1 modularized the restart/replay implementation and graph/tool boundaries without adding runtime behavior.

Scope implemented:

- split restart/replay tests by behavior
- extracted durable GitHub comment execution and result-shaping helpers
- extracted selected graph routing, metadata, policy, validation, and execution-context helpers
- preserved fake-client-only execution and explicit durable dependency injection

A4.3.1 does not add durable audit store, real GitHub execution, token loading, API behavior changes, or production-grade exactly-once claims.

Status: Completed.

## A4.4 Durable Audit Store and Adversarial Persistence Suite

A4.4 implements local/demo durable audit evidence and adversarial persistence tests.

Scope implemented:

- `durable_audit_events` table
- `DurableAuditStore`
- durable audit event model and event-type enum
- safe JSON metadata serialization with targeted unsafe metadata rejection
- deterministic audit listing ordered by `created_at, event_id`
- optional runtime-only audit-store injection
- successful execution audit evidence
- duplicate replay audit evidence
- blocked execution audit evidence
- fake-client failure audit evidence
- adversarial persistence tests for approval mismatches, side-effect statuses, restart/replay, failure, metadata safety, and fake-client-only execution boundaries

A4.4 does not execute real GitHub calls, load GitHub tokens, add a second GitHub tool, or claim production-grade audit. A4.4 does not claim universal exactly-once execution.

Status: Completed.

## Still Out Of Scope

- real GitHub API calls
- GitHub token loading
- real GitHub client
- workflow dispatch
- PR creation
- repo file writes
- issue creation
- branch creation
- MCP
- OAuth/OIDC
- JWT validation
- frontend
- Postgres
- Redis
- Docker Compose
- cloud deployment
- live LLM HTTP mode
- multi-agent behavior
- production audit claims
- production readiness
