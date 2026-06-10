# Architecture

## Project Principle

The LLM proposes. The harness decides.

## Core Safety Invariant

Identity is server-derived, policy is deterministic, and high-risk execution cannot happen before approval.

## Current Layers

1. FastAPI API Layer: implemented as a local/demo API.
2. API Safety Layer: in-memory rate limiting for task creation and approval actions.
3. Identity Layer: API-key resolver and FastAPI dependency implemented.
4. Harness Service Layer: `HarnessGraphService` wraps the local checkpointed graph.
5. Local LangGraph Orchestration Layer: implemented with `InMemorySaver`.
6. Policy Guard Layer: implemented as pure deterministic authorization logic.
7. Tool Registry Layer: implemented as a controlled registry of three dry-run tools.
8. Dry-Run Tool Layer: implemented with no external side effects.
9. Audit Layer: implemented as structured in-memory audit event helpers.
10. Durable Persistence Layer: not implemented.

## API Boundary

The API layer stays thin:

```text
route
→ get_current_identity dependency
→ HarnessGraphService
→ response schema
```

API routes must not:

- trust role/scopes/user_id from request bodies
- evaluate policy manually
- execute tools manually
- inspect role/scopes manually
- create approval decisions outside the service/graph boundary

Approval and rejection routes resolve identity with `get_current_identity` and then delegate to `HarnessGraphService`. The audit route reads structured audit events through the same service boundary.

Rate limiting is applied after identity resolution and is keyed from server-derived `api_key_id` plus route group. It does not alter graph policy, approval, or execution semantics.

## Current Graph Flow

```text
START
→ interpret_task
→ policy_guard
    ├── ALLOW → execute_tool → generate_report → END
    ├── DENY → finalize_denial → END
    └── REQUIRE_APPROVAL → pause_for_approval → handle_approval_decision
```

Unknown tasks are marked `FAILED` and routed to report generation without tool execution.

## Approval Resume Flow

When policy requires approval:

```text
pause_for_approval
→ create ApprovalRequest
→ checkpoint state
→ interrupt before high-risk execution
```

On resume:

```text
Command(resume={ approval_decision, approval_actor })
→ validate approval decision and actor
→ approved: execute dry-run tool
→ rejected: finalize rejection
→ invalid actor/decision: fail safely
```

Admin does not bypass approval. High-risk tools never return direct allow from policy.

## Current API Endpoints

Implemented:

- `GET /tools`
- `GET /identity/me`
- `POST /tasks`
- `GET /tasks/{task_id}`
- `POST /tasks/{task_id}/approve`
- `POST /tasks/{task_id}/reject`
- `GET /tasks/{task_id}/audit`

## State and Persistence

Current checkpointing is in-memory and process-local through LangGraph `InMemorySaver`.

State does not survive process restart. This project does not yet include durable persistence, SQLite checkpointing, or database-backed task storage.

The API should be treated as local/demo infrastructure only. It does not include OAuth/OIDC, JWT validation, database persistence, LLM calls, frontend functionality, or deployment hardening.
The in-memory rate limiter is local/demo protection only. It is not Redis-backed, distributed, or suitable as production traffic control.

## V1 Non-Goals

- Redis or distributed rate limiting
- OAuth/OIDC
- JWT validation
- database persistence
- SQLite checkpointing
- LLM calls
- real identity provider
- frontend dashboard
- complex RAG
- fine-tuning
- real GitHub writes
- real workflow triggers
- multi-agent system
- OPA/Casbin
- Kubernetes
- production deployment hardening
