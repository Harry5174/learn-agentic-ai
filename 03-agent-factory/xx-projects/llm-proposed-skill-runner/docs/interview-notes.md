# Interview Notes

## One-Minute Summary

LLM-Proposed, Harness-Controlled Skill Runner is a local/demo agent execution
harness for model-shaped skill plans.

The core idea is:

```text
The LLM proposes.
The harness validates, authorizes, approval-gates, executes, and audits.
```

The model or fake proposer can suggest a structured `SkillProposal`, but the
harness controls validation, policy, approval, tool execution, and audit.

## Problem Solved

Many agent demos blur together intent, authorization, execution, and
explanation. This project separates those concerns.

The proposer is treated as an untrusted source of possible work. Its output is
validated like an external API request before anything can execute.

## What Artifact 2 Adds Over Artifact 1

Artifact 1 proved the harness foundation with deterministic task
interpretation:

- server-derived identity
- deterministic policy
- approval gate
- dry-run tools
- audit trail
- checkpointed resume

Artifact 2 adds:

- explicit skill contracts
- model-shaped `SkillProposal`
- deterministic `ProposalValidator`
- trusted `SkillRegistry`
- fake proposer scenarios
- optional mocked LLM proposer boundary
- skill execution graph

The important design move is that adding a proposer does not give the model
authority.

## Why The Model Is Not Trusted

The model may hallucinate:

- a skill
- a tool
- a lower risk level
- missing required steps
- malformed JSON
- unsupported versions

The harness rejects those cases before policy evaluation or tool execution.

## Why ProposalValidator Exists

`ProposalValidator` checks untrusted proposals against trusted registry
metadata.

It validates:

- known skill ID
- supported skill version
- non-empty steps
- duplicate step IDs
- known registered steps
- allowed tool names
- required scopes
- risk consistency

It derives final risk and approval requirement from registry metadata, not from
the model.

## Why Policy Is Still Needed

Validation answers:

```text
Is this proposed skill structurally allowed for this registry and identity?
```

Policy answers:

```text
May this resolved identity execute or request this registered tool now?
```

That separation keeps proposal validation, authorization, approval, and
execution independently testable.

## Why High-Risk Actions Require Approval

High-risk validated proposals do not execute directly.

The graph creates an approval request, checkpoints state, and pauses. Approval
or rejection later resumes the graph.

Rejection finalizes without tool execution. Invalid approval actors fail safely.

## How The Optional LLM Boundary Works

`LLMProposer` is provider-neutral and receives an injected client. Tests use
mocked clients only.

Malformed model output becomes a malformed proposal with evidence in the
rationale, then the validator rejects it. No tests require credentials, network
access, or real model calls.

## Current API Boundary

The FastAPI routes still expose the inherited deterministic task API from
Artifact 1. They do not expose new skill-runner endpoints yet.

The Artifact 2 skill runner is currently demonstrated through
`SkillGraphService` and tests.

That is intentional for Sprint 5: the sprint packages what exists without
adding surface area.

## Current Limitations

- local/demo artifact
- no OAuth/OIDC or JWT validation
- no MCP
- no database persistence
- no frontend
- no multi-agent behavior
- no real GitHub writes
- no real workflow triggers
- tools are dry-run only
- proposed runtime tool arguments are not fully validated or executed yet

## Strong Interview Framing

This is not "an LLM that can use tools."

It is a harness that shows how a system can accept model-proposed work while
keeping authority in deterministic, testable application layers.
