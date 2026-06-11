# Project Status

## Project

**Title:** LLM-Proposed, Harness-Controlled Skill Runner

**Principle:** The LLM proposes. The harness decides.

**Safety Invariant:** Identity is server-derived, policy is deterministic, and high-risk execution cannot happen before approval.

**Current Artifact Status:** Artifact 2 baseline copied from the completed
Artifact 1 harness, `Identity-Aware Stateful Agent Harness`.

Artifact 2 skill-runner implementation has not started yet. `SkillSpec`,
`SkillProposal`, proposal validation, fake proposer, real LLM proposer, skill
registry changes, and skill execution graph changes are planned for later
sprints.

## Sprint Status

- Artifact 2 Sprint 0 in progress: baseline copy, metadata rename, and
  documentation clarification.
- Artifact 2 Sprint 1 has not started.

## Inherited Baseline From Artifact 1

The copied codebase currently contains the completed Artifact 1 implementation:

- domain contracts
- server-derived identity resolver
- controlled dry-run tool registry
- deterministic policy guard
- structured in-memory audit helpers
- local LangGraph harness
- checkpointed approval resume flow
- FastAPI task API
- rate limiting and public safety docs
- portfolio documentation

## Inherited API Implementation

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

## Inherited Rate Limiting Implementation

Implemented:

- In-memory fixed-window rate limiter.
- Task creation rate limit for `POST /tasks`.
- Approval action rate limit for `POST /tasks/{task_id}/approve`.
- Rejection action rate limit for `POST /tasks/{task_id}/reject`.
- HTTP `429` response when a protected endpoint exceeds its limit.
- Rate limit keys derived from server-resolved API-key identity.
- Public safety documentation for local/demo limitations.

## Inherited Documentation

Implemented:

- Portfolio-ready README.
- Final architecture documentation.
- Final API reference.
- Demo flow documentation with curl examples.
- V1 safety model documentation.
- V1/V1.1/V2/V3 roadmap.
- Interview notes for explaining design decisions.
- Honest limitations and non-goals across docs.

## Current Test Status

```bash
uv run pytest
# 155 passed

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

- Artifact 2 `SkillSpec`
- Artifact 2 `SkillStep`
- Artifact 2 `SkillProposal`
- proposal validation
- fake proposer
- real LLM proposer
- skill registry changes
- skill execution graph changes
- database persistence
- durable checkpoint storage
- SQLite checkpointing
- Redis or distributed rate limiting
- LLM calls
- real GitHub writes
- real workflow triggers
- OAuth/OIDC
- JWT validation
- frontend
- production deployment hardening

## Artifact 2 Status

Artifact 2 is at Sprint 0 baseline status only.

Future work should follow the roadmap in `docs/roadmap.md`.
