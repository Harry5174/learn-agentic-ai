# LLM-Proposed, Harness-Controlled Skill Runner

Artifact 2 is a local/demo agent execution harness for structured skill
proposals.

The core safety pattern is:

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
plans while keeping authority in deterministic application layers.

Implemented capabilities include:

- structured skill contracts and trusted skill registry metadata
- deterministic proposal validation before policy or execution
- fake proposer scenarios for local tests and demos
- optional provider-neutral `LLMProposer` boundary with mocked-client tests
- checkpointed skill execution graph
- server-derived identity, deterministic policy, approval gating, dry-run tools,
  and structured audit evidence
- Artifact 2.1 skill-runner HTTP routes for listing skills, creating runs,
  reading runs, approving/rejecting paused runs, and retrieving audit events

## What This Is Not

This is not a chatbot, RAG wrapper, OAuth/OIDC app, MCP platform, production
authorization system, production deployment, multi-agent framework, or real
GitHub automation service.

The repo intentionally does not include OAuth/OIDC, JWT validation, database
persistence, frontend UI, real GitHub writes, real workflow triggers, MCP,
multi-agent behavior, or production deployment hardening.

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

Base URL:

```text
http://127.0.0.1:8000
```

Demo API keys:

- `viewer-dev-key`
- `operator-dev-key`
- `admin-dev-key`

These are static local/demo credentials, not production identity.

## Primary Demo

Artifact 2.1's primary demo is the skill-runner API:

- `GET /skills`
- `POST /skill-runs`
- `GET /skill-runs/{run_id}`
- `POST /skill-runs/{run_id}/approve`
- `POST /skill-runs/{run_id}/reject`
- `GET /skill-runs/{run_id}/audit`

Start with [docs/demos/skill-runner-api-demo.md](docs/demos/skill-runner-api-demo.md).

The inherited Artifact 1-style task API is still available and documented at
[docs/demos/task-api-demo.md](docs/demos/task-api-demo.md).

## Documentation

Use [docs/README.md](docs/README.md) as the documentation index.

High-value entry points:

- [Skill-runner API contract](docs/api/skill-runner-api.md)
- [Inherited task API reference](docs/api/task-api.md)
- [Architecture](docs/architecture/architecture.md)
- [Security model](docs/architecture/security-model.md)
- [Threat model](docs/architecture/threat-model.md)
- [Known limitations](docs/status/known-limitations.md)
- [Roadmap](docs/status/roadmap.md)
- [Interview notes](docs/status/interview-notes.md)
- [Artifact 1 vs Artifact 2](docs/comparisons/artifact-1-vs-artifact-2.md)

## Current Boundaries

The default HTTP skill-runner demo uses fake proposer mode. HTTP
`proposer_mode: "llm"` is disabled and rejected without calling a live model
provider. Invalid-proposal and high-risk skill-run scenarios are covered by API
tests using scenario-configured fake proposer injection when default curl cannot
select those scenarios.

Skill specs include argument-schema metadata, but current skill execution uses
harness-owned default arguments for registered dry-run tools. Validating and
executing model-proposed runtime tool arguments is future Artifact 2.2 work.

This remains a local/demo artifact with process-local state, in-memory
checkpointing, in-memory audit/rate limits, dry-run tools only, and no durable
persistence.
