# Safety Model

Artifact 2 demonstrates safety-oriented harness design for model-proposed skill
execution. It is not a production security system.

The core invariant is:

```text
Identity is server-derived, policy is deterministic, and high-risk execution cannot happen before approval.
```

## The Model Is Not Trusted

The proposer may be fake, mocked, or LLM-backed. In all cases, its output is
treated as untrusted.

Prompt instructions are not security controls. The harness assumes the proposer
can return malformed output, hallucinated skills, hallucinated tools, missing
steps, understated risk, or unsupported versions.

## Proposal Validation

`ProposalValidator` treats `SkillProposal` like an external API request.

It checks the proposal against trusted `SkillRegistry` metadata before policy,
approval, or execution can happen.

Validation rejects:

- unknown skills
- unsupported versions
- empty step lists
- duplicate step IDs
- unknown steps
- disallowed tool names
- missing required scopes
- risk understatement

Validation derives final risk and approval requirement from registry metadata,
not from model claims.

## Server-Derived Identity

The harness uses demo API keys resolved by server code into `IdentityContext`.

The request body and model output cannot claim or override:

- user ID
- role
- scopes
- API key ID

## Deterministic Policy

Policy is implemented as deterministic application logic.

The policy guard evaluates:

- resolved identity
- registered tool metadata
- required scopes
- tool risk level

It returns one of:

- allow
- deny
- require approval

The model does not decide authorization.

## High-Risk Approval Gate

High-risk tools require approval before execution.

The graph pauses and checkpoints state before high-risk execution. A later
approval or rejection resumes the graph.

Important behavior:

- admin does not bypass approval
- approval happens before high-risk dry-run tool execution
- rejection finalizes without tool execution
- invalid approvers fail safely without tool execution

## Dry-Run Tools

All tools are controlled dry-run tools.

The harness does not perform:

- real GitHub writes
- real issue comments
- real workflow dispatches
- external side-effecting tool calls

## Audit Trail

The harness records structured audit events for important decisions and actions,
including:

- task or run creation
- proposal produced
- validation completed
- permission checks
- approval requested
- approval granted
- approval rejected
- tool executed
- task/run completed
- task/run failed

Audit events are currently in-memory and not durably persisted.

## Checkpointing

The graph uses LangGraph `InMemorySaver`.

This enables local checkpoint/resume behavior during one process lifetime, but:

- checkpoints do not survive process restart
- paused work can resume only while the process remains alive
- durable checkpointing is future work

## Tool Argument Limitation

Skill specs include argument-schema metadata. Current execution still uses
harness-owned default arguments for registered dry-run tools.

The current harness validates proposed skill/step/tool/risk structure. It does
not yet validate and execute arbitrary model-proposed runtime tool arguments.

## Explicit Non-Goals

- OAuth/OIDC
- JWT validation
- production identity provider integration
- database persistence
- durable audit storage
- Redis or distributed rate limiting
- MCP
- real external tool adapters
- frontend dashboard
- production deployment hardening
- multi-agent behavior

## Safety Claim

Artifact 2 demonstrates a safer agent harness shape:

```text
untrusted proposer suggests a skill plan
validator checks it against trusted registry metadata
server resolves identity
deterministic policy decides
approval gates high-risk execution
controlled tools execute dry-run actions
audit records the path
```

It should not be described as production security infrastructure.
