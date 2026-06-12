# Threat Model

## Scope

This threat model covers the local/demo Artifact 2 skill runner inherited by
Artifact 3 and the A3.1 future real side-effect boundary specification.

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

## Future Real GitHub Side-Effect Risks

A3.1 defines these mitigations for implementation in later A3.x sprints. It
does not implement real GitHub execution, a GitHub client, a side-effect
ledger, `side_effect_id`, or `post_github_issue_comment`.

Risk:

Duplicate GitHub comments are caused by replay, resume, retry, or repeated
approval paths.

Future mitigation:

- derive a deterministic `side_effect_id` from `skill_run_id`, `step_id`,
  `tool_name`, and `validated_arguments_hash`
- check a side-effect ledger before any real GitHub call
- skip duplicate real calls when the ledger already records the side effect
- audit ledger hits, misses, executed effects, skipped effects, and failures

Risk:

Approval mismatches or stale approvals authorize a different action than the
human approved.

Future mitigation:

- bind approval to the exact validated action, not only the run ID
- include `skill_run_id`, `step_id`, `tool_name`, `validated_arguments_hash`,
  and `side_effect_id` in the approval binding
- reject or repause execution if the validated action changes before resume

Risk:

Repository targeting abuse causes comments to be posted to an unintended
repository.

Future mitigation:

- allow real comments only for repositories explicitly configured in a
  server-owned allowlist
- keep allowlist policy outside model output and request-provided arguments
- audit repository allowed and repository denied decisions

Risk:

Token or client configuration is injected through proposed arguments.

Future mitigation:

- treat GitHub tokens and client configuration as server-side configuration
  only
- reject model-proposed tokens, authorization headers, API base URLs, client
  config, and transport config
- preserve the Artifact 2.2-style scalar argument validation boundary before
  policy, approval, or side-effect execution

Risk:

Real mode is accidentally enabled because a token is present.

Future mitigation:

- require explicit future configuration such as `REAL_GITHUB_ENABLED=true`
- keep the default as false / dry-run
- never infer real mode from token presence alone

Risk:

GitHub API failures create ambiguity about whether a comment was posted.

Future mitigation:

- capture GitHub client failures as structured failure results
- audit failures without exposing secrets
- avoid automatic retries that could duplicate comments
- do not convert ambiguous outcomes into success

Risk:

Audit gaps make real side effects hard to explain.

Future mitigation:

- emit audit evidence before and after the side-effect attempt
- include real-mode, repository policy, `side_effect_id`, ledger, client-called,
  client-not-called, executed, skipped, and failed events
- avoid exposing secrets or raw rejected payloads in audit output

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
