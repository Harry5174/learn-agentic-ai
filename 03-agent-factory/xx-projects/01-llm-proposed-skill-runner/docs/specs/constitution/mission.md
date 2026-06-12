# Mission

## Artifact Identity

**Name:** LLM-Proposed, Harness-Controlled Skill Runner

**Current status:** Artifact 2.2 is complete as a local/demo validated-argument
skill runner.

Artifact 2.1 exposes the skill-runner lifecycle through FastAPI:

- `GET /skills`
- `POST /skill-runs`
- `GET /skill-runs/{run_id}`
- `POST /skill-runs/{run_id}/approve`
- `POST /skill-runs/{run_id}/reject`
- `GET /skill-runs/{run_id}/audit`

Artifact 2.2 adds validated model-proposed scalar tool arguments. Model-shaped
`SkillProposal` objects may include runtime tool arguments, but only
registry-declared, scalar, validator-normalized arguments can reach dry-run
execution.

## Mission Statement

This project demonstrates how to accept model-shaped work proposals without
giving the model authority over identity, authorization, approval, execution, or
audit.

The artifact exists to make a safety-oriented agent execution harness visible,
testable, and explainable for future coding agents, reviewers, mentors, and
interviewers.

## Core Invariant

```text
The LLM/proposer proposes.
The harness validates, authorizes, approval-gates, executes, and audits.
```

The proposer is untrusted. The harness owns every security-relevant decision.

## Safety Model

The current harness uses:

- server-derived identity from local demo API keys
- trusted `SkillRegistry` metadata
- deterministic `ProposalValidator` checks
- trusted `ToolArgumentSpec` metadata
- validated scalar arguments from `ValidatedSkillPlan`
- deterministic policy checks
- approval pause/resume for high-risk work
- registered dry-run tools only
- structured audit events
- process-local, in-memory state

Request bodies and model output must not define identity, role, scopes, policy
decisions, approval authority, trusted tools, final risk, or control-plane
runtime arguments.

## Engineering Skill Demonstrated

This artifact demonstrates backend/API engineering for controlled agentic
execution:

- typed schemas for model-shaped proposals and public responses
- clear trust boundaries between proposer, validation, policy, approval,
  execution, and audit
- graph-based pause/resume behavior for approval gates
- test-backed failure paths for invalid proposals and unsafe requests
- honest local/demo limitations

## Primary Demo Surface

The primary Artifact 2.1 demo is the skill-runner API under `/skills` and
`/skill-runs`.

The inherited `/tasks` API remains available as an Artifact 1-style task harness
demo, but it is not the primary Artifact 2.1 demo surface.

## Non-Goals

Artifact 2.2 does not include:

- object/list/nested argument support
- partial acceptance of mixed valid and invalid argument plans
- live LLM mode through HTTP
- MCP
- OAuth/OIDC or JWT validation
- database persistence
- durable audit storage
- frontend UI
- real GitHub writes
- real workflow triggers
- deployment hardening
- multi-agent behavior

## Future-Agent Guidance

Future agents should:

- preserve the core invariant
- treat model output like an untrusted external request
- keep authorization, approval, and execution outside prompts
- reuse existing service, graph, registry, policy, approval, and audit boundaries
- keep routes thin and avoid moving policy decisions into HTTP handlers
- keep tests deterministic and free of live model/network requirements
- describe limitations plainly instead of implying production readiness
- do not weaken the argument boundary
- do not allow raw proposed arguments to reach `ToolRegistry.execute()`
- do not add infrastructure integrations before preserving validation,
  approval, audit, and redaction boundaries
