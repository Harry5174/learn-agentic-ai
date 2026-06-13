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

Status: Current sprint.

Scope implemented:

- durable side-effect record model
- SQLite connection manager and side_effect_records table
- `DurableSideEffectLedger` with state transition validation
- Re-instantiation persistence test

A4.1 does not integrate the ledger into the runtime execution path.

## A4.2 Durable Approval Binding

Future work only.

Potential scope:

- persist approval against `side_effect_id` and `validated_arguments_hash`
- require matching approved approval binding before execution
- fail closed on mismatched approval binding
- preserve blocked vs rejected semantics

## A4.3 Standalone Persistence Proof

Future work only.

Acceptance requirement:

```text
1. Open SQLite file.
2. Write one side_effect_record.
3. Close/discard repository object.
4. Open a new repository object against the same SQLite file.
5. Read the same record back.
```

This must be proven before graph/service integration.

## A4.4 Graph Integration

Future work only.

Integrate the `DurableSideEffectLedger` and `DurableApprovalBindingStore` into the main execution path.

## A4.5 Restart-Replay Proof

Future work only.

Potential scope:

- execute once through fake client
- persist succeeded side-effect evidence
- restart with a fresh repository/service object against the same SQLite file
- replay the same side-effect ID
- prove fake client is not called again
- return skipped duplicate / already succeeded evidence
- persist durable audit explanation

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
