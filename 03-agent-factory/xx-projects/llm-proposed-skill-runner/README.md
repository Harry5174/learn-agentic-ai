# LLM-Proposed, Harness-Controlled Skill Runner

> Status: Artifact 2 baseline.
>
> This project was copied from the completed Artifact 1 harness:
> `Identity-Aware Stateful Agent Harness`.
>
> Artifact 2 skill-runner implementation has not started yet. `SkillSpec`,
> `SkillProposal`, proposal validation, fake proposer, real LLM proposer,
> and skill execution graph changes are planned for later sprints.

Artifact 2 will become a LangGraph-based skill runner where an LLM can propose
skills, but validation, policy, approval, execution, and audit remain controlled
by deterministic system components.

The current codebase is the inherited baseline behavior from Artifact 1:

> The LLM proposes. The harness decides.

The copied baseline uses deterministic task interpretation to prove the harness
shape. Artifact 2 has not yet added LLM-proposed skills.

## What This Is

This project is the Sprint 0 baseline for Artifact 2. It currently demonstrates
the inherited Artifact 1 harness behavior:

- identity is resolved by the server from `X-API-Key`
- policy is deterministic and scope-based
- high-risk actions pause before execution
- approval and rejection resume a checkpointed graph
- tools are controlled dry-run functions
- audit events record important decisions and actions
- public-demo endpoints have simple in-memory rate limits

The inherited baseline invariant is:

```text
Identity is server-derived, policy is deterministic, and high-risk execution cannot happen before approval.
```

Future Artifact 2 sprints will add explicit skill proposal contracts and
validation without moving security-relevant decisions into the model.

## What This Is Not

This is not:

- a chatbot
- a generic RAG wrapper
- an OAuth project
- a production authorization platform
- a production traffic-control system
- a multi-agent demo

The inherited baseline intentionally does not include OAuth/OIDC, JWT validation,
Redis, database persistence, frontend UI, real GitHub writes, real workflow
triggers, LLM/OpenAI calls, LangSmith tracing, new tools, or multi-agent
behavior.

## Inherited Baseline Behavior From Artifact 1

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

Last copied baseline checks:

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

The current API is inherited baseline behavior from Artifact 1. Artifact 2
skill proposal endpoints have not been implemented yet.

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

The demo flow is inherited baseline behavior from Artifact 1.

Use the demo flow guide:

- [docs/demo-flow.md](docs/demo-flow.md)

The guide includes curl examples for:

- viewer inspect task -> `completed`
- viewer draft task -> `denied`
- operator trigger workflow -> `paused_for_approval`
- admin approve -> `completed`
- admin reject -> `rejected`
- repeated task creation -> `429`

## Baseline Safety Model

The inherited baseline demonstrates safety-oriented harness design. It is not a
production security system.

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

## Baseline Limitations

The copied baseline is local/demo infrastructure:

- task state does not survive process restart
- checkpoints do not survive process restart
- audit events are not persisted
- rate limits reset on process restart
- rate limits are not distributed
- API keys are static demo credentials
- tools are dry-run only
- no real external GitHub writes occur
- no real workflow triggers occur
- no LLM is called in the current baseline
- no Artifact 2 skill proposal contracts are implemented yet

## Roadmap

- Sprint 0: Copied Artifact 1 baseline with renamed docs and metadata.
- Later Artifact 2 sprints: `SkillSpec`, `SkillStep`, `SkillProposal`,
  proposal validation, fake proposer, real LLM proposer, skill registry, and
  skill execution graph changes.
- Future hardening: durable state, persisted audit trail, production identity,
  distributed rate limiting, observability, and deployment hardening.

See [docs/roadmap.md](docs/roadmap.md).

## Interview Notes

For a concise explanation of the problem, design choices, and V2 extension path, see [docs/interview-notes.md](docs/interview-notes.md).
