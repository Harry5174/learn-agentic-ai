# Identity-Aware Stateful Agent Harness

A LangGraph-based agent execution harness where an LLM can propose actions, but identity, policy, approval, execution, and audit are controlled by deterministic system components.

> The LLM proposes. The harness decides.

V1 uses deterministic task interpretation to prove the harness. An LLM can later replace the proposer without changing the identity, policy, approval, execution, or audit layers.

## What This Is

This project is a portfolio MVP for safe agent execution. It demonstrates how a harness can keep security-relevant decisions outside the model:

- identity is resolved by the server from `X-API-Key`
- policy is deterministic and scope-based
- high-risk actions pause before execution
- approval and rejection resume a checkpointed graph
- tools are controlled dry-run functions
- audit events record important decisions and actions
- public-demo endpoints have simple in-memory rate limits

The core invariant is:

```text
Identity is server-derived, policy is deterministic, and high-risk execution cannot happen before approval.
```

## What This Is Not

This is not:

- a chatbot
- a generic RAG wrapper
- an OAuth project
- a production authorization platform
- a production traffic-control system
- a multi-agent demo

V1 intentionally does not include OAuth/OIDC, JWT validation, Redis, database persistence, frontend UI, real GitHub writes, real workflow triggers, LLM/OpenAI calls, LangSmith tracing, new tools, or multi-agent behavior.

## V1 Features

- Domain schemas for identity, tools, policy, approval, state, and audit.
- Server-derived demo API-key identity resolver.
- Controlled dry-run tool registry.
- Deterministic policy guard.
- Structured in-memory audit events.
- LangGraph harness with allowed, denied, failed, pause, approve, and reject paths.
- Checkpointed approval resume flow with LangGraph `InMemorySaver`.
- FastAPI demo API.
- In-memory fixed-window rate limiting for task creation and approval actions.
- Documentation for architecture, API, demo flows, V1 safety model, roadmap, and interview discussion.

Current checks:

```bash
uv run pytest
# 155 passed

uv run ruff check .
# All checks passed!
```

## Architecture Overview

```text
FastAPI route
-> X-API-Key identity dependency
-> in-memory rate limit dependency for protected writes
-> HarnessGraphService
-> local LangGraph harness
-> deterministic policy guard
-> controlled dry-run tool registry
-> structured audit events
-> public response schema
```

Important boundaries:

- API routes do not trust role, scopes, or user ID from request bodies.
- API routes do not evaluate policy directly.
- API routes do not execute tools directly.
- Rate limiting is keyed from server-resolved `api_key_id`, not body claims.
- The tool registry does not authorize.
- The policy guard does not execute tools.
- High-risk tool execution cannot happen before approval.

See [docs/architecture.md](docs/architecture.md) for the full architecture.

## Current API

Demo API keys are defined in `src/app/identity/config.py`:

- `viewer-dev-key`
- `operator-dev-key`
- `admin-dev-key`

Implemented endpoints:

- `GET /tools`
- `GET /identity/me`
- `POST /tasks`
- `GET /tasks/{task_id}`
- `POST /tasks/{task_id}/approve`
- `POST /tasks/{task_id}/reject`
- `GET /tasks/{task_id}/audit`

Protected by in-memory rate limits:

- `POST /tasks`: 5 requests per 60 seconds per API key
- `POST /tasks/{task_id}/approve`: 10 requests per 60 seconds per API key
- `POST /tasks/{task_id}/reject`: 10 requests per 60 seconds per API key

See [docs/api.md](docs/api.md) for request and response examples.

## Quickstart

Install dependencies:

```bash
uv sync
```

Run tests and lint:

```bash
uv run pytest
uv run ruff check .
```

Run the local API:

```bash
uv run uvicorn app.api.main:app --reload
```

The API is available at:

```text
http://127.0.0.1:8000
```

## Demo

Use the demo flow guide:

- [docs/demo-flow.md](docs/demo-flow.md)

The guide includes curl examples for:

- viewer inspect task -> `completed`
- viewer draft task -> `denied`
- operator trigger workflow -> `paused_for_approval`
- admin approve -> `completed`
- admin reject -> `rejected`
- repeated task creation -> `429`

## V1 Safety Model

V1 demonstrates safety-oriented harness design. It is not a production security system.

Safety model summary:

- identity comes from server-side API-key resolution
- request bodies cannot claim elevated role or scopes
- policy is deterministic
- high-risk tools require approval
- admin does not bypass approval
- all tools are dry-run only
- audit events are structured
- checkpointing is in-memory
- rate limiting is in-memory

See [docs/security-model-v1.md](docs/security-model-v1.md) and [docs/public-safety.md](docs/public-safety.md).

## Limitations

V1 is local/demo infrastructure:

- task state does not survive process restart
- checkpoints do not survive process restart
- audit events are not persisted
- rate limits reset on process restart
- rate limits are not distributed
- API keys are static demo credentials
- tools are dry-run only
- no real external GitHub writes occur
- no real workflow triggers occur
- no LLM is called in V1

## Roadmap

- V1: Portfolio MVP with deterministic harness, API, approval, audit, and local rate limiting.
- V1.1: Durability upgrade with SQLite/Postgres checkpointing, durable task storage, and persisted audit trail.
- V2: OAuth/OIDC-integrated agent harness with JWT validation and token-derived scopes.
- V3: Production agent runtime with distributed rate limiting, real external tool adapters, observability, stronger policy engine, and deployment hardening.

See [docs/roadmap.md](docs/roadmap.md).

## Interview Notes

For a concise explanation of the problem, design choices, and V2 extension path, see [docs/interview-notes.md](docs/interview-notes.md).
