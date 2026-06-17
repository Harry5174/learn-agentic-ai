# Artifact 0 vs Artifact 1

## Summary

Artifact 0 proves the execution harness.

Artifact 1 adds model-shaped skill proposals while keeping execution authority in
the harness.

## Artifact 0: Identity-Aware Stateful Agent Harness

Artifact 0 focused on deterministic task interpretation and safe execution
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

Artifact 0's key idea:

```text
Do not let request bodies control identity, policy, approval, or execution.
```

## Artifact 1: LLM-Proposed, Harness-Controlled Skill Runner

Artifact 1 keeps the Artifact 0 harness foundation and adds:

- structured skill contracts
- `SkillProposal` as model-shaped output
- `ProposalValidator`
- trusted `SkillRegistry`
- deterministic `FakeProposer`
- optional provider-neutral `LLMProposer`
- skill execution graph
- proposal and validation audit evidence

Artifact 1's key idea:

```text
The LLM proposes.
The harness validates, authorizes, approval-gates, executes, and audits.
```

## Difference In The Proposer

Artifact 0:

```text
user query -> deterministic task interpreter -> selected tool
```

Artifact 1:

```text
user task -> proposer -> SkillProposal -> ProposalValidator -> registered skill steps
```

The model-shaped proposal layer is new in Artifact 1.

## Difference In The Safety Boundary

Artifact 0 prevents clients from claiming identity or bypassing policy.

Artifact 1 also prevents model output from:

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

The public FastAPI API includes the inherited Artifact 0 task API and the
Artifact 1.1 skill-runner lifecycle API.

The inherited task API remains useful for demonstrating the original execution
harness. The Artifact 1.1 skill-runner API is the primary demo surface for
model-shaped skill proposals.

See:

- [../api/task-api.md](../api/task-api.md)
- [../api/skill-runner-api.md](../api/skill-runner-api.md)
- [../demos/task-api-demo.md](../demos/task-api-demo.md)
- [../demos/skill-runner-api-demo.md](../demos/skill-runner-api-demo.md)
