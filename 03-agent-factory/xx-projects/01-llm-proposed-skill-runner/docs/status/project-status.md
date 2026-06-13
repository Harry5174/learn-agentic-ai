# Project Status

## Project

**Title:** LLM-Proposed, Harness-Controlled Skill Runner

**Principle:** The LLM proposes. The harness validates, authorizes,
approval-gates, executes, and audits.

**Safety Invariant:** Identity is server-derived, policy is deterministic, and
high-risk execution cannot happen before approval.

For the current project constitution, see
[../specs/constitution/mission.md](../specs/constitution/mission.md).

## Current Artifact Status

Artifact 2 has completed the proposal-validation, skill-execution, and
Artifact 2.1 HTTP lifecycle foundation for a local/demo skill runner.

Artifact 2.2 is complete as a local/demo safety artifact. Sprint E2.0 added the
argument contract design, Sprint E2.1 added validator argument checks, Sprint
E2.2 wired validated arguments into execution, and Sprint E2.3 added
adversarial boundary tests plus final documentation packaging.

Raw proposed arguments still do not execute directly.

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
- Artifact 2.2 E2.1 validation of model-proposed scalar step arguments into a
  trusted `ValidatedSkillPlan`
- Artifact 2.2 E2.2 graph wiring so dry-run tools receive accepted validated
  step arguments only
- Artifact 2.2 E2.3 adversarial tests for argument attacks, raw non-execution,
  safe audit/API evidence, and approval preservation

Historical note: Artifact 2.1 included E1.3 documentation, demo walkthrough,
and portfolio packaging work. Current status: Artifact 2.2 is complete within
local/demo scalar-argument scope.

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
- GitHub write operations
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
- GitHub write operations
- real workflow triggers
- provider SDK integration
- live LLM mode through HTTP

## Current Limitation To Keep Visible

Skill specs contain trusted argument metadata, and the proposal validator now
checks model-proposed scalar runtime arguments. The skill execution graph now
passes accepted `ValidatedSkillPlan` arguments to dry-run tools after proposal
validation, policy checks, and any required approval gate.

Raw proposed arguments do not flow directly to `ToolRegistry.execute()`. Public
API and audit summaries expose safe argument-validation status, argument names,
redaction names, and issue codes without raw rejected values.

Artifact 2.2 V1 remains intentionally narrow: no object/list/nested argument
support, no arbitrary JSON payload validation, and no partial acceptance.
