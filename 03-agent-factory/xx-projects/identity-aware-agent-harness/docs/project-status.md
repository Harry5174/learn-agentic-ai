# Project Status

## Project

**Title:** Identity-Aware Stateful Agent Harness

**Principle:** The LLM proposes. The harness decides.

**Safety Invariant:** Identity is server-derived, policy is deterministic, and high-risk execution cannot happen before approval.

## Sprint Status

- Sprint 0 complete: domain contracts.
- Sprint 1 complete: server-derived identity resolver.
- Sprint 2 complete: controlled dry-run tool registry.
- Sprint 3 complete: deterministic policy guard.
- Sprint 4 complete: structured in-memory audit helpers.
- Sprint 5 complete: local LangGraph harness.
- Sprint 6 complete: checkpointed approval resume flow.
- Sprint 7 complete: FastAPI task API.
- Sprint 8 next: Rate Limiting and Public Safety.
- Sprint 9 planned: Documentation and Portfolio Polish.

## Completed Sprint 7 Implementation

Implemented:

- FastAPI application skeleton.
- `GET /tools`
- `GET /identity/me`
- `POST /tasks`
- `GET /tasks/{task_id}`
- `POST /tasks/{task_id}/approve`
- `POST /tasks/{task_id}/reject`
- `GET /tasks/{task_id}/audit`
- `X-API-Key` identity dependency.
- `HarnessGraphService` wrapper over the checkpointed local graph.
- Thin FastAPI routes that delegate task behavior to graph/service layers.
- Structured audit trail responses for task history.

## Current Test Status

```bash
uv run pytest
# 143 passed

uv run ruff check .
# All checks passed!
```

## Current Persistence Status

The graph uses LangGraph `InMemorySaver`.

This means:

- task state is process-local
- checkpoints do not survive process restart
- paused tasks can be resumed only while the process is alive
- no database persistence exists yet

## Explicitly Not Implemented

- database persistence
- durable checkpoint storage
- SQLite checkpointing
- rate limiting
- LLM calls
- real GitHub writes
- real workflow triggers
- OAuth/OIDC
- JWT validation
- frontend
- production deployment hardening

## Next Implementation Slice

Sprint 8 focuses on rate limiting and public safety:

```text
Rate limiting and public safety controls
```
