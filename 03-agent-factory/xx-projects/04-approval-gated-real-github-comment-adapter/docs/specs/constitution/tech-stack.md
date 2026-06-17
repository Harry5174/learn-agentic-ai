# Tech Stack

This file records the current Artifact 1 technology choices and the boundaries
future agents should preserve.

## Runtime And Application Stack

- **Python:** application language.
- **FastAPI:** local/demo HTTP API for identity, tools, tasks, skills, and
  skill runs.
- **Pydantic:** typed domain, request, and response schemas.
- **LangGraph:** checkpointed execution graph with approval pause/resume.
- **In-memory/process-local state:** current checkpoint, audit, task/run, and
  rate-limit state. This is an explicit local/demo limitation.

## Development And Verification Stack

- **uv:** dependency management and command runner.
- **pytest:** test runner for schemas, graph behavior, API behavior, validation,
  policy, approval, tools, audit, and proposer boundaries.
- **Ruff:** linting.

Tests must remain deterministic. They must not require network access, real
model calls, provider credentials, real GitHub writes, or workflow triggers.

## Agent Harness Boundaries

The current harness relies on:

- **Dry-run tool registry:** only registered dry-run tools execute.
- **Fake proposer default:** HTTP skill-run creation defaults to deterministic
  fake proposer behavior.
- **Mocked LLM proposer boundary:** `LLMProposer` exists internally and is
  tested with mocked clients only.
- **Server-derived identity:** API keys resolve to server-known local demo
  identity; clients and model output do not claim roles or scopes.
- **Approval gate:** high-risk work pauses before execution and resumes only
  with a server-derived approval/rejection actor.
- **Audit trail:** proposal, validation, policy, approval, execution, and final
  status events provide evidence.

## Dependency Boundaries

Do not add dependencies casually.

Specifically:

- no provider SDKs by default
- no database dependency unless explicitly approved
- no MCP dependency unless explicitly approved
- no OAuth/OIDC or JWT stack unless explicitly approved
- no frontend framework unless explicitly approved
- no scripts unless explicitly approved

## LLM Boundary

HTTP `proposer_mode: "llm"` is disabled and rejected. Enabling a
live LLM demo mode would be future work and must be explicit, configured, and
testable without requiring live calls.

Live LLM calls must not be introduced into automated tests.

## Persistence Boundary

Current state is process-local and in memory.

Future persistence must not be added as incidental cleanup. It should be a
deliberate design step after the proposal, validation, approval, and audit
contracts are stable.

## Tool Argument Boundary

Artifact 1.2 validates proposed runtime arguments against trusted
`ToolArgumentSpec` metadata.

Skill graph execution uses validator-approved scalar arguments from
`ValidatedSkillPlan`.

Raw proposal arguments are never passed directly to `ToolRegistry.execute()`.

The V1 scope remains intentionally narrow:

- string, integer, and boolean arguments only
- object/list/nested argument support deferred
- partial acceptance unsupported
- dry-run tools only
- process-local state
- in-memory audit
