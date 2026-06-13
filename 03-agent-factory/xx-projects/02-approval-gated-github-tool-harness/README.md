# Artifact 3 — Approval-Gated GitHub Tool Harness

Artifact 3 is the Approval-Gated GitHub Tool Harness project.

A3.0 was only a baseline copy and rename sprint. This project was copied from
the finalized Artifact 2.2 baseline, and Artifact 2.2 remains the completed
dry-run scalar argument validation artifact.

A3.1 is a documentation/specification-only sprint that defines the future real
side-effect boundary for an approval-gated GitHub issue-comment tool. It does
not implement GitHub execution.

A3.2 adds isolated GitHub issue-comment client and side-effect ledger
boundaries.

A3.3 wires those boundaries into exactly one approval-gated local/demo skill
path, `post_github_issue_comment`. The skill uses validated scalar arguments,
a trusted repository allowlist, explicit approval, an in-memory side-effect
ledger, and `FakeGitHubIssueCommentClient` simulated execution.

A3.4 adds an adversarial safety suite and documentation for that one
fake-client GitHub issue-comment path. It tests argument smuggling,
unsupported payloads, repository policy bypass attempts, approval bypass
attempts, approval-binding mutation behavior, replay suppression, fake-client
failure behavior, network/token safety, and audit completeness.

Artifact 3 still has not implemented real GitHub API execution.

Repository folder numbering was applied after the original A3.0 copy/rename
prompt. The current source baseline folder is
`03-agent-factory/xx-projects/01-llm-proposed-skill-runner`, and the current
Artifact 3 folder is
`03-agent-factory/xx-projects/02-approval-gated-github-tool-harness`.

The core safety pattern is:

```text
The LLM proposes.
The harness validates, authorizes, approval-gates, executes, and audits.
```

A fake proposer, mocked LLM proposer boundary, or future configured proposer can
suggest a `SkillProposal`, but the model is not trusted to authorize work,
approve high-risk actions, choose unregistered tools, or execute anything
directly.

## What This Is

This is a portfolio artifact for AI/backend interviews and agentic software
learning. It demonstrates a narrow approval-gated GitHub issue-comment skill
path while keeping real network execution disabled.

Inherited baseline capabilities include:

- structured skill contracts and trusted skill registry metadata
- deterministic proposal validation before policy or execution
- fake proposer scenarios for local tests and demos
- optional provider-neutral `LLMProposer` boundary with mocked-client tests
- checkpointed skill execution graph
- server-derived identity, deterministic policy, approval gating, dry-run tools,
  and structured audit evidence
- Artifact 2.1 skill-runner HTTP routes for listing skills, creating runs,
  reading runs, approving/rejecting paused runs, and retrieving audit events
- Artifact 2.2 validation for model-proposed scalar tool arguments before
  dry-run execution
- A3.2 isolated GitHub issue-comment request/result/failure schemas, fake
  client boundary, deterministic side-effect id helpers, and in-memory ledger
  boundary tests
- A3.3 `post_github_issue_comment` skill/tool registration with approval,
  repository allowlist policy, fake-client execution, ledger replay
  suppression, and audit evidence
- A3.4 adversarial safety tests for the GitHub comment side-effect boundary,
  including smuggling, unsupported payloads, policy/approval bypass attempts,
  replay behavior, failure safety, network/token checks, and audit evidence

Artifact 3 A3.1 defines the future boundary for an approval-gated GitHub
issue-comment tool named `post_github_issue_comment` with scalar arguments
`repository`, `issue_number`, and `comment_body`.

Artifact 3 A3.3 implements that one local/demo skill path with the fake client.
It does not enable real GitHub execution.

## What This Is Not

This is not a chatbot, RAG wrapper, OAuth/OIDC app, MCP platform, production
authorization system, production deployment, multi-agent framework, or real
GitHub automation service.

The repo intentionally does not include OAuth/OIDC, JWT validation, database
persistence, frontend UI, real GitHub writes, real workflow triggers, MCP,
multi-agent behavior, or production deployment hardening.

A3.3 does not include a real GitHub client, real-mode configuration, token
handling, live LLM HTTP mode, OAuth/OIDC, MCP, database persistence, frontend,
workflow dispatch, PR creation, branch creation, issue creation, repo
file-write tooling, or durable ledger/audit persistence.

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

The inherited primary demo is still the Artifact 2.1 skill-runner API:

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

- [Project constitution](docs/specs/constitution/mission.md)
- [Artifact 3 real tool boundary](docs/specs/artifact-3-real-tool-boundary.md)
- [Skill-runner API contract](docs/api/skill-runner-api.md)
- [Inherited task API reference](docs/api/task-api.md)
- [Architecture](docs/architecture/architecture.md)
- [Security model](docs/architecture/security-model.md)
- [Threat model](docs/architecture/threat-model.md)
- [Adversarial argument validation](docs/adversarial-argument-validation.md)
- [Adversarial GitHub side-effect safety](docs/adversarial-github-side-effect-safety.md)
- [Known limitations](docs/status/known-limitations.md)
- [Roadmap](docs/status/roadmap.md)
- [Interview notes](docs/status/interview-notes.md)
- [Artifact 1 vs Artifact 2](docs/comparisons/artifact-1-vs-artifact-2.md)

## Current Boundaries

Artifact 3 A3.3 adds exactly one GitHub-specific skill/tool path:
`post_github_issue_comment`. It accepts only validated scalar `repository`,
`issue_number`, and `comment_body` arguments, checks the trusted repository
allowlist, pauses for approval, computes `validated_arguments_hash` and
`side_effect_id`, checks the process-local side-effect ledger, and then uses
the fake GitHub issue-comment client for simulated local/demo execution.

A3.4 adds adversarial tests around that path. The tests prove that smuggled
control-plane arguments, credential-like fields, unsupported object/list/nested
payloads, repository allowlist bypass attempts, approval bypass attempts, and
fake-client failures remain inside the local/demo safety boundary. A3.4 did
not require implementation hardening and did not add real GitHub execution.

The default HTTP skill-runner demo uses fake proposer mode. HTTP
`proposer_mode: "llm"` is disabled and rejected without calling a live model
provider. Invalid-proposal and high-risk skill-run scenarios are covered by API
tests using scenario-configured fake proposer injection when default curl cannot
select those scenarios.

Skill specs include trusted argument metadata. A model-shaped proposal can
include runtime tool arguments, but only registry-declared scalar
string/integer/boolean values accepted by `ProposalValidator` can reach dry-run
tool execution. Unknown, missing, wrong-type, forbidden control-plane, object,
and list arguments are rejected. Public API and audit summaries expose safe
argument-validation status, argument names, redaction names, and issue codes
without echoing rejected raw values.

This remains a local/demo artifact with process-local state, in-memory
checkpointing, in-memory audit/rate limits, fake-client GitHub comment
simulation, and no durable persistence. A3.3 does not add object/list/nested
argument support, partial acceptance, live HTTP LLM mode, MCP, OAuth/OIDC,
database persistence, durable replay protection, or real GitHub writes.
