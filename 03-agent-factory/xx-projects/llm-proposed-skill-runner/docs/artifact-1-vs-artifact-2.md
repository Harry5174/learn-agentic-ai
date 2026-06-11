# Artifact 1 vs Artifact 2

## Summary

Artifact 1 proves the execution harness.

Artifact 2 adds model-shaped skill proposals while keeping execution authority in
the harness.

## Artifact 1: Identity-Aware Stateful Agent Harness

Artifact 1 focused on deterministic task interpretation and safe execution
control.

It implemented:

- server-derived API-key identity
- deterministic task-to-tool selection
- controlled dry-run tools
- deterministic policy guard
- approval gate for high-risk tools
- checkpointed resume
- structured audit trail
- local/demo FastAPI task API
- in-memory rate limiting

Artifact 1's key idea:

```text
Do not let request bodies control identity, policy, approval, or execution.
```

## Artifact 2: LLM-Proposed, Harness-Controlled Skill Runner

Artifact 2 keeps the Artifact 1 harness foundation and adds:

- structured skill contracts
- `SkillProposal` as model-shaped output
- `ProposalValidator`
- trusted `SkillRegistry`
- deterministic `FakeProposer`
- optional provider-neutral `LLMProposer`
- skill execution graph
- proposal and validation audit evidence

Artifact 2's key idea:

```text
The LLM proposes.
The harness validates, authorizes, approval-gates, executes, and audits.
```

## Difference In The Proposer

Artifact 1:

```text
user query -> deterministic task interpreter -> selected tool
```

Artifact 2:

```text
user task -> proposer -> SkillProposal -> ProposalValidator -> registered skill steps
```

The model-shaped proposal layer is new in Artifact 2.

## Difference In The Safety Boundary

Artifact 1 prevents clients from claiming identity or bypassing policy.

Artifact 2 also prevents model output from:

- inventing trusted skills
- inventing tools
- understating risk
- skipping required scopes
- executing before validation
- executing high-risk work before approval

## What Stayed The Same

Both artifacts keep these decisions out of the model:

- identity
- authorization
- approval
- execution
- audit

Both artifacts use dry-run tools only.

## Current Integration Boundary

The current public FastAPI API remains the inherited Artifact 1 task API.

The Artifact 2 skill runner is implemented in service/graph modules and verified
by tests. Public skill-runner API endpoints are future work, not Sprint 5 work.
