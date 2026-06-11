# Interview Notes

## One-Minute Summary

LLM-Proposed, Harness-Controlled Skill Runner is currently an Artifact 2
baseline copied from the completed Artifact 1 harness, `Identity-Aware Stateful
Agent Harness`.

Artifact 2 skill-runner implementation has not started yet. `SkillSpec`,
`SkillProposal`, proposal validation, fake proposer, real LLM proposer, and
skill execution graph changes are planned for later sprints.

The important idea is:

```text
The LLM proposes. The harness decides.
```

The inherited baseline uses deterministic task interpretation instead of an LLM
so the project can prove the safety architecture first. Later Artifact 2 sprints
can add LLM-proposed skills without changing identity, policy, approval,
execution, or audit boundaries.

## Problem Solved

Agent demos often let the model blur together intent, authorization, execution, and explanation.

The inherited baseline separates those concerns:

- the proposer interprets user intent
- the server resolves identity
- deterministic policy decides what is allowed
- high-risk actions require approval
- controlled tools execute dry-run actions
- audit records what happened

## Why It Is Not a Chatbot or RAG App

The project is not centered on conversation or retrieval.

It is centered on execution control:

- who is acting
- what tool is selected
- whether the actor has permission
- whether approval is required
- whether the tool actually executes
- what audit trail is produced

## Why Identity Is Server-Derived

User-provided request bodies are not trusted for identity.

Identity comes from `X-API-Key`, resolved by server code into an `IdentityContext`.

This prevents a client or model from claiming:

- admin role
- extra scopes
- different user ID

## Why Policy Is Deterministic

Authorization should be predictable and testable.

The policy guard uses identity, tool metadata, required scopes, and risk level. It does not ask a model whether something is safe.

This makes policy behavior inspectable in unit tests and API tests.

## Why High-Risk Actions Require Approval

High-risk actions are not allowed directly, even for admin identity.

The graph pauses before high-risk execution and creates an approval request. Approval or rejection resumes the checkpointed graph.

This proves the safety invariant:

```text
high-risk execution cannot happen before approval
```

## How LangGraph Checkpoint/Resume Works Here

The graph reaches an approval node and interrupts with approval context.

State is checkpointed with LangGraph `InMemorySaver`.

Later, the API injects an approval or rejection decision through `Command(resume=...)`.

The graph validates the decision and actor, then either:

- executes the dry-run tool after approval
- finalizes rejection without tool execution
- fails safely for invalid approval actors

## How FastAPI Wraps the Graph

FastAPI routes stay thin:

```text
route
-> identity dependency
-> rate limit dependency for protected writes
-> HarnessGraphService
-> public response schema
```

Routes do not evaluate policy, inspect roles/scopes manually, or execute tools.

## What The Current Baseline Intentionally Does Not Include

The current baseline does not include:

- OAuth/OIDC
- JWT validation
- Redis
- database persistence
- frontend
- real GitHub writes
- real workflow triggers
- LLM/OpenAI calls
- `SkillSpec` or `SkillProposal`
- proposal validation
- fake or real LLM skill proposers
- skill registry changes
- skill execution graph changes
- LangSmith tracing
- multi-agent behavior
- production deployment hardening

These are omitted so the core harness invariant stays easy to inspect.

## What I Would Improve in V2

High-value extensions:

- durable checkpointing with SQLite or Postgres
- persisted audit trail
- OAuth/OIDC identity
- JWT validation and token-derived scopes
- Redis or gateway rate limiting
- real external tool adapters behind approval gates
- observability and tracing
- production deployment hardening

The key design goal would remain the same:

```text
keep identity, policy, approval, execution, and audit outside the model
```
