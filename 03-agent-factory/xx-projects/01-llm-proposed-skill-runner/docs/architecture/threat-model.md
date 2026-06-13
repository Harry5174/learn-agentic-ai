# Threat Model

## Scope

This threat model covers the local/demo Artifact 2 skill runner.

It focuses on model-proposed skill execution where an untrusted proposer returns
a structured `SkillProposal` and the harness remains responsible for validation,
authorization, approval, execution, and audit.

## Assets To Protect

- identity context
- role and scope decisions
- trusted skill and tool registry metadata
- approval decisions
- dry-run execution boundary
- audit evidence
- checkpointed paused state

## Trust Boundaries

```text
untrusted task/proposer output
-> SkillProposal parsing
-> deterministic validation
-> deterministic policy
-> approval gate
-> controlled dry-run execution
```

Trusted components:

- server-side identity resolver
- `SkillRegistry`
- `ToolRegistry`
- `ProposalValidator`
- policy guard
- approval graph/service logic

Untrusted inputs:

- user task text
- model output
- fake or mocked proposer output
- request bodies
- approval reason text

## Model Output Risks

The proposer may return:

- malformed JSON
- missing required fields
- unknown skill IDs
- unsupported versions
- unknown steps
- duplicate steps
- hallucinated tools
- understated risk levels
- plans that omit required scopes

Mitigation:

- parse output into `SkillProposal`
- convert malformed output into a rejected malformed proposal with evidence
- validate against trusted registry metadata
- reject before policy or execution

## Prompt Instructions Are Not Security

Prompt text can guide the proposer, but it cannot enforce authorization.

Security-relevant decisions live in deterministic code:

- identity resolution
- proposal validation
- policy
- approval
- tool registry execution boundary

## Identity Risks

Risk:

A client or model claims elevated role, scopes, user ID, or API key identity.

Mitigation:

- identity is resolved server-side from `X-API-Key`
- request bodies do not define identity
- model output does not define identity
- rate limit keys use server-derived `api_key_id`

## Authorization Risks

Risk:

The model proposes a tool the actor is not allowed to use.

Mitigation:

- validator checks required scopes for the proposed skill and steps
- policy guard checks resolved identity against registered tool metadata
- routes and tools do not make ad hoc authorization decisions

## High-Risk Execution Risks

Risk:

High-risk work executes without human approval.

Mitigation:

- high-risk registered tools return `require_approval`
- graph pauses before execution
- approval/rejection resumes checkpointed state
- rejection and invalid approvers do not execute tools

## Tool Execution Risks

Risk:

The model causes arbitrary code, external API calls, real GitHub writes, or real
workflow triggers.

Mitigation:

- only registered tools execute
- tools are dry-run only
- no external side-effecting tool adapters are implemented
- proposed tool names are checked against registered skill metadata

## Runtime Argument Risks

Risk:

The model proposes malformed arguments, unknown argument names, object/list
payloads, or control-plane fields that try to influence identity, policy,
approval, risk, tool selection, or skill selection.

Mitigation:

- model-proposed runtime arguments are accepted only after registry-schema
  validation
- only validator-normalized scalar arguments reach dry-run execution
- unsafe, malformed, unknown, or control-plane arguments are rejected before
  execution
- raw proposed arguments never flow directly into `ToolRegistry.execute()`

## Audit Risks

Risk:

The system cannot explain why a proposal executed or failed.

Mitigation:

- audit records proposal, validation, policy, approval, execution, and final status
- proposal and validation events include structured metadata

Limitation:

- audit events are in-memory only and not durably persisted

## Current Limitations

- local/demo only
- no durable persistence
- no OAuth/OIDC or JWT validation
- no MCP
- no frontend
- no multi-agent behavior
- no production deployment
- scalar string/integer/boolean arguments only
- no object/list/nested argument support
- no partial acceptance
