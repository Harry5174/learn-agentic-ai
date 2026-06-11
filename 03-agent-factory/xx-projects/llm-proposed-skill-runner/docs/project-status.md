# Project Status

## Project

**Title:** LLM-Proposed, Harness-Controlled Skill Runner

**Principle:** The LLM proposes. The harness validates, authorizes,
approval-gates, executes, and audits.

**Safety Invariant:** Identity is server-derived, policy is deterministic, and
high-risk execution cannot happen before approval.

## Current Artifact Status

Artifact 2 has completed the proposal-validation and skill-execution foundation
for a local/demo skill runner.

Implemented:

- `SkillSpec`, `SkillStep`, and `SkillProposal` contracts
- `SkillRegistry` with default registered skills
- `ProposalValidator` for deterministic validation of untrusted proposals
- `FakeProposer` for deterministic local/test scenarios
- optional `LLMProposer` boundary using injected mocked clients in tests
- checkpointed skill execution graph in `src/app/skill_graph/`
- policy and approval integration for validated skill proposals
- dry-run tool execution through the existing `ToolRegistry`
- audit events for proposal, validation, policy, approval, and execution

Sprint 5 is documentation, demo scenario, and portfolio packaging work only.

## Active Artifact 2 Sprint Specs

The active Artifact 2 sprint specs are:

- `docs/sprint-2-spec.md`
- `docs/sprint-3-spec.md`
- `docs/sprint-4-spec.md`
- `docs/sprint-5-spec.md`

Copied Artifact 1 sprint specs that could mislead future IDE agents are archived
under:

```text
docs/archive/artifact-1-sprint-specs/
```

## Inherited Foundation From Artifact 1

Artifact 2 keeps the completed Artifact 1 harness foundation:

- server-derived demo API-key identity resolver
- deterministic policy guard
- controlled dry-run tool registry
- structured in-memory audit helpers
- checkpointed approval resume behavior
- FastAPI task API
- in-memory public-demo rate limiting

Artifact 2 adds the skill proposal layer on top of that foundation. It does not
move security-relevant decisions into the model.

## Current API Status

The FastAPI surface remains the inherited local/demo task API:

- `GET /tools`
- `GET /identity/me`
- `POST /tasks`
- `GET /tasks/{task_id}`
- `POST /tasks/{task_id}/approve`
- `POST /tasks/{task_id}/reject`
- `GET /tasks/{task_id}/audit`

No public skill-runner API endpoints have been added.

The Artifact 2 skill runner is currently exercised through `SkillGraphService`
and focused tests.

## Current Persistence Status

The graph uses LangGraph `InMemorySaver`.

This means:

- task/run state is process-local
- checkpoints do not survive process restart
- paused tasks or skill runs can resume only while the process is alive
- audit events are not persisted to a database

## Current Test Boundary

Tests use deterministic fake outputs or mocked LLM-client outputs.

No test depends on:

- real model calls
- network access
- API keys or credentials
- real GitHub writes
- real workflow triggers

## Explicitly Not Implemented

- public skill-runner API endpoints
- OAuth/OIDC
- JWT validation
- MCP
- database persistence
- durable audit storage
- frontend
- production deployment
- multi-agent behavior
- real GitHub writes
- real workflow triggers
- full proposed tool-argument validation framework
- provider SDK integration

## Current Limitation To Keep Visible

Skill specs contain argument-schema metadata, but the skill execution graph uses
harness-owned default arguments for the dry-run tools. Validating and executing
model-proposed runtime arguments is future work.
