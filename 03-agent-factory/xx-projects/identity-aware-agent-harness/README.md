# Identity-Aware Stateful Agent Harness

Identity-Aware Stateful Agent Harness is a local/demo execution harness for controlled agent actions. It is built to show how an LLM-facing system can keep identity, policy, approval, execution, and audit decisions inside deterministic application code.

**Project Principle:** The LLM proposes. The harness decides.

**Core Safety Invariant:** Identity is server-derived, policy is deterministic, and high-risk execution cannot happen before approval.

## Current Status

This repository is a portfolio MVP, not a production-ready service.

- Sprint 0 complete: domain contracts and schema tests.
- Sprint 1 complete: server-derived API-key identity resolver.
- Sprint 2 complete: controlled dry-run tool registry.
- Sprint 3 complete: deterministic policy guard.
- Sprint 4 complete: in-memory audit logger.
- Sprint 5 complete: local LangGraph harness with allowed, denied, failed, and approval-pause paths.
- Sprint 6 complete: checkpointed approval resume flow using LangGraph `InMemorySaver`.
- Sprint 7 complete: FastAPI demo API with tools, identity, task creation, task retrieval, approval, rejection, and audit endpoints.
- Sprint 8 complete: in-memory API rate limiting and public safety documentation.

Current checks:

```bash
uv run pytest
# 155 passed

uv run ruff check .
# All checks passed!
```

## Current API

Implemented API endpoints:

- `GET /tools`: returns public metadata for the controlled dry-run tools.
- `GET /identity/me`: resolves identity from the `X-API-Key` header.
- `POST /tasks`: starts a graph task through `HarnessGraphService`.
- `GET /tasks/{task_id}`: returns the current public task summary.
- `POST /tasks/{task_id}/approve`: resumes a paused task with an approval decision through `HarnessGraphService`.
- `POST /tasks/{task_id}/reject`: resumes a paused task with a rejection decision through `HarnessGraphService`.
- `GET /tasks/{task_id}/audit`: returns the task's structured audit trail.

`POST /tasks`, `POST /tasks/{task_id}/approve`, and `POST /tasks/{task_id}/reject` are protected by simple in-memory fixed-window rate limits keyed from the server-derived API-key identity.

This is a local/demo API. It uses a module-level, in-memory `HarnessGraphService` and LangGraph `InMemorySaver`. Task state and checkpoints are process-local, do not survive process restart, and are not backed by durable persistence.

## Architecture Summary

The current flow is:

```text
FastAPI route
→ X-API-Key identity dependency
→ HarnessGraphService
→ local LangGraph harness
→ deterministic policy guard
→ controlled dry-run tool registry
→ public response schema
```

Important boundaries:

- Identity is resolved server-side from `X-API-Key`.
- Rate limiting is keyed from the resolved API-key identity, not request body claims.
- API routes do not inspect role/scopes manually.
- API routes do not evaluate policy directly.
- API routes do not execute tools directly.
- Approval and rejection routes delegate to `HarnessGraphService`.
- The tool registry does not authorize.
- The policy guard does not execute tools.
- Audit records decisions and actions but does not control routing.
- High-risk execution pauses before tool execution and requires an approval resume path.

## Quickstart

```bash
uv sync
uv run pytest
uv run ruff check .
uv run uvicorn app.api.main:app --reload
```

Demo API keys are defined in `src/app/identity/config.py`.

## Non-Goals

V1 intentionally does not include:

- production durability
- database persistence
- OAuth/OIDC
- JWT validation
- Redis or distributed rate limiting
- real GitHub writes
- real workflow triggers
- LLM calls
- frontend dashboard
- production deployment hardening
- multi-agent behavior

## What This Is Not

- not a chatbot
- not a generic RAG wrapper
- not an OAuth project
- not a production authorization platform
- not a multi-agent demo
