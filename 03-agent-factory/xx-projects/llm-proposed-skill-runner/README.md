# LLM-Proposed, Harness-Controlled Skill Runner

Artifact 2 is a local/demo agent execution harness for structured skill
proposals.

The project demonstrates a core agentic safety pattern:

```text
The LLM proposes.
The harness validates, authorizes, approval-gates, executes, and audits.
```

An LLM, fake proposer, or mocked proposer can suggest a `SkillProposal`, but the
model is not trusted to authorize work, approve high-risk actions, choose
unregistered tools, or execute anything directly.

## What This Is

This is a portfolio artifact for AI/backend interviews and agentic software
learning. It shows how to put a controlled execution harness around model-shaped
plans.

Implemented Artifact 2 capabilities:

- structured `SkillSpec`, `SkillStep`, and `SkillProposal` contracts
- a trusted `SkillRegistry` containing allowed skill metadata
- deterministic `ProposalValidator` checks before policy or execution
- deterministic `FakeProposer` scenarios for local demos and tests
- optional provider-neutral `LLMProposer` boundary with mocked-client tests
- a checkpointed LangGraph skill execution graph
- deterministic policy checks using server-derived identity and tool metadata
- approval pause/resume for high-risk validated proposals
- controlled dry-run tool execution through `ToolRegistry`
- structured audit events for proposal, validation, policy, approval, and execution

The project was originally copied from Artifact 1,
`Identity-Aware Stateful Agent Harness`. Artifact 2 keeps the identity, policy,
approval, dry-run tool, and audit foundation, then adds a proposal-validation and
skill-execution layer on top.

## What This Is Not

This is not:

- a chatbot
- a RAG wrapper
- an OAuth/OIDC app
- an MCP platform
- a production authorization system
- a production deployment
- a multi-agent framework
- a real GitHub automation service

The repo intentionally does not include OAuth/OIDC, JWT validation, database
persistence, frontend UI, real GitHub writes, real workflow triggers, MCP,
multi-agent behavior, or production deployment hardening.

## Architecture

Artifact 2's skill execution flow is:

```text
Client/task
-> proposer
-> SkillProposal
-> ProposalValidator
-> SkillRegistry
-> policy guard
-> approval gate
-> dry-run ToolRegistry
-> audit
-> SkillRunResult
```

Important boundaries:

- proposer: untrusted source of proposed skill plans
- `SkillProposal`: structured model-shaped request
- `ProposalValidator`: deterministic gate for schema, registry, scope, step, tool, and risk checks
- `SkillRegistry`: trusted catalog of allowed skills and allowed tool metadata
- policy guard: deterministic authorization over server-derived identity and registered tool metadata
- approval gate: human decision point for high-risk execution
- `ToolRegistry`: controlled dry-run execution primitives only
- audit: evidence trail for proposal, validation, policy, approval, and execution events

See [docs/architecture.md](docs/architecture.md) for details.

## Implemented Skill Scenarios

The default skill registry contains three local/demo skills:

- `inspect_sandbox_health`: low-risk inspection using `inspect_sandbox_issues`
- `draft_sandbox_issue_comment`: medium-risk draft generation using `draft_issue_comment`
- `simulate_sandbox_workflow`: high-risk workflow simulation using `trigger_workflow_dry_run`

The Artifact 2.1 demo scenarios are documented in
[docs/demo-scenarios.md](docs/demo-scenarios.md):

- valid low-risk proposal executes a dry-run tool
- invalid proposal is rejected before policy or execution
- hallucinated skill/tool is rejected
- high-risk proposal pauses for approval
- approved high-risk proposal resumes and executes
- rejected high-risk proposal does not execute
- malformed LLM output fails safely

## Current API Boundary

The FastAPI routes expose the inherited local/demo task API from Artifact 1 and
the completed Artifact 2.1 skill-runner API surface:

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

Task routes still wrap the deterministic task harness in `src/app/graph/`.
Skill-run routes wrap the Artifact 2 `SkillGraphService` and expose creation,
read, approval, rejection, and audit for process-local demo runs.

See:

- [docs/api.md](docs/api.md)
- [docs/skill-runner-api.md](docs/skill-runner-api.md)
- [docs/skill-runner-demo.md](docs/skill-runner-demo.md)

## Skill-Runner HTTP Demo

The default HTTP skill-runner demo uses `proposer_mode: "fake"`. If omitted,
the API defaults to fake proposer mode.

The default running API can demonstrate:

- skill listing with `GET /skills`
- low-risk skill-run creation with `POST /skill-runs`
- skill-run summary retrieval with `GET /skill-runs/{run_id}`
- skill-run audit retrieval with `GET /skill-runs/{run_id}/audit`
- safe rejection of HTTP `proposer_mode: "llm"` with `400 Bad Request`

Invalid proposal, high-risk approval, high-risk rejection, and approved
high-risk audit behavior are covered by API tests using scenario-configured fake
proposer injection. The default curl flow does not currently expose a public
request field for selecting those fake proposer scenarios.

See [docs/skill-runner-demo.md](docs/skill-runner-demo.md) for curl-oriented
walkthroughs.

## Identity, Policy, Approval, And Audit

The safety invariant is:

```text
Identity is server-derived, policy is deterministic, and high-risk execution cannot happen before approval.
```

Identity is resolved from server-known demo API keys. Request bodies and model
outputs cannot claim user ID, role, scopes, or API key ID.

Policy checks are deterministic. The policy guard does not ask the model whether
an action is safe.

High-risk tool execution pauses for approval. Rejection finalizes the run without
tool execution.

Audit events record proposal, validation, policy, approval, and execution
evidence. Audit state is local/in-memory and not durably persisted.

See:

- [docs/security-model-v1.md](docs/security-model-v1.md)
- [docs/threat-model.md](docs/threat-model.md)
- [docs/audit-trail.md](docs/audit-trail.md)

## Tool Argument Limitation

Skill specs include argument-schema metadata, but current skill execution does
not validate or execute arbitrary model-proposed runtime arguments.

The graph uses harness-owned default arguments for the registered dry-run tools.
This keeps Artifact 2.1 honest: Artifact 2 validates which skill, steps, tools,
scopes, and risk levels are allowed, but a full proposed-argument validation
framework is future Artifact 2.2 work.

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

## Demo API Keys

Demo API keys are defined in `src/app/identity/config.py`:

- `viewer-dev-key`
- `operator-dev-key`
- `admin-dev-key`

These are static local/demo credentials, not production identity.

## Tests

The test suite covers:

- schema contracts
- identity resolution
- tool registry and dry-run tools
- policy guard behavior
- approval schemas and checkpoint resume
- audit helpers
- inherited task graph/API behavior
- skill registry
- proposal validation
- fake proposer scenarios
- optional LLM proposer parsing with mocked clients
- skill execution graph allow, reject, approval, resume, and audit paths

No test requires real model calls, network access, credentials, real GitHub
writes, or workflow triggers.

## Known Limitations

This is a local/demo artifact.

Current limits include:

- no production deployment
- no OAuth/OIDC
- no JWT validation
- no MCP
- no database persistence
- no durable audit store
- no frontend
- no multi-agent behavior
- no real GitHub writes
- no real workflow triggers
- tools remain dry-run
- HTTP skill-runner mode defaults to fake proposer behavior
- HTTP `llm` proposer mode is disabled and rejected
- real LLM proposer is optional and tests use mocked output
- tool arguments remain limited and harness-owned defaults are used

See [docs/known-limitations.md](docs/known-limitations.md).

## Roadmap

The narrow future roadmap is:

- validated proposed tool arguments
- MCP adapter after skill/tool contracts stabilize
- OAuth/OIDC identity integration
- durable audit/task persistence
- real GitHub write tools behind approval gates
- small adversarial proposal test suite
- portfolio deployment demo

See [docs/roadmap.md](docs/roadmap.md).

## Portfolio Notes

For interview-oriented framing, see:

- [docs/interview-notes.md](docs/interview-notes.md)
- [docs/artifact-1-vs-artifact-2.md](docs/artifact-1-vs-artifact-2.md)
- [docs/project-status.md](docs/project-status.md)
