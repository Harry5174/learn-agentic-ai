# Project Status

## Project

**Title:** LLM-Proposed, Harness-Controlled Skill Runner

**Principle:** The LLM proposes. The harness validates, authorizes,
approval-gates, executes, and audits.

**Safety Invariant:** Identity is server-derived, policy is deterministic, and
high-risk execution cannot happen before approval.

## Current Artifact Status

Artifact 2 has completed the proposal-validation, skill-execution, and
Artifact 2.1 HTTP lifecycle foundation for a local/demo skill runner.

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
- Artifact 2.1 skill-runner API routes for listing skills, creating runs,
  reading runs, approving/rejecting paused runs, and retrieving audit events

Sprint E1.3 is documentation, demo walkthrough, and portfolio packaging work
only. It does not change runtime behavior.

## Active Artifact 2 Sprint Specs

The active Artifact 2 foundation sprint specs are:

- `../specs/sprint-2-spec.md`
- `../specs/sprint-3-spec.md`
- `../specs/sprint-4-spec.md`
- `../specs/sprint-5-spec.md`

Artifact 2.1 extends that foundation with the skill-runner API lifecycle.

Copied Artifact 1 sprint specs that could mislead future IDE agents are archived
under:

```text
../specs/archive/artifact-1-sprint-specs/
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

The FastAPI surface includes the inherited local/demo task API and the completed
Artifact 2.1 skill-runner routes:

- `GET /tools`
- `GET /identity/me`
- `GET /skills`
- `POST /tasks`
- `GET /tasks/{task_id}`
- `POST /tasks/{task_id}/approve`
- `POST /tasks/{task_id}/reject`
- `GET /tasks/{task_id}/audit`
- `POST /skill-runs`
- `GET /skill-runs/{run_id}`
- `POST /skill-runs/{run_id}/approve`
- `POST /skill-runs/{run_id}/reject`
- `GET /skill-runs/{run_id}/audit`

Skill-run routes are exposed through `SkillGraphService` for process-local
demo runs.

The default HTTP skill-runner path uses fake proposer mode. HTTP
`proposer_mode: "llm"` is disabled and returns a safe `400` response without
calling a live model provider. Invalid proposal, high-risk approval, high-risk
rejection, and approved high-risk audit behavior are covered by API tests using
scenario-configured fake proposer injection.

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
- live LLM mode through HTTP

## Current Limitation To Keep Visible

Skill specs contain argument-schema metadata, but the skill execution graph uses
harness-owned default arguments for the dry-run tools. Validating and executing
model-proposed runtime arguments is planned as future Artifact 2.2 work.
