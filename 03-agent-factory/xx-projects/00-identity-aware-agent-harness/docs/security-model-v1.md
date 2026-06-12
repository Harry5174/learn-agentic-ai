# V1 Safety Model

V1 demonstrates safety-oriented harness design. It is not a production security system.

The core invariant is:

```text
Identity is server-derived, policy is deterministic, and high-risk execution cannot happen before approval.
```

## Server-Derived Identity

V1 uses demo API keys resolved by the server from `X-API-Key`.

The request body cannot claim or override:

- user ID
- role
- scopes
- API key ID

This keeps identity outside the model and outside client-controlled task payloads.

## Deterministic Policy

Policy is implemented as deterministic application logic.

The policy guard evaluates:

- resolved identity
- selected tool
- required scopes
- tool risk level

It returns one of:

- allow
- deny
- require approval

The LLM, or V1 deterministic proposer, does not decide authorization.

## High-Risk Approval Gate

High-risk tools require approval before execution.

The graph pauses and checkpoints state before high-risk execution. A later approval or rejection resumes the graph.

Important behavior:

- admin does not bypass approval
- approval happens before high-risk dry-run tool execution
- rejection finalizes without tool execution
- invalid approvers fail safely without tool execution

## Dry-Run Tools

All V1 tools are controlled dry-run tools.

V1 does not perform:

- real GitHub writes
- real issue comments
- real workflow dispatches
- external side-effecting tool calls

## Audit Trail

The harness records structured audit events for important decisions and actions, including:

- task creation
- tool selection
- permission checks
- approval requested
- approval granted
- approval rejected
- tool executed
- task completed
- task failed

Audit events are currently in-memory and not durably persisted.

## Checkpointing

V1 uses LangGraph `InMemorySaver`.

This enables local checkpoint/resume behavior during one process lifetime, but:

- checkpoints do not survive process restart
- paused tasks can resume only while the process remains alive
- durable checkpointing belongs in V1.1 or V2

## Rate Limiting

V1 includes simple in-memory fixed-window rate limiting for:

- task creation
- approval actions
- rejection actions

Rate limiting is keyed from server-resolved API-key identity.

Limitations:

- limits reset on process restart
- limits are not shared across processes
- limits are not distributed across machines
- Redis or gateway-based rate limiting belongs in V2 or production infrastructure

## Explicit Non-Goals

V1 does not implement:

- OAuth/OIDC
- JWT validation
- production identity provider integration
- database persistence
- durable audit storage
- Redis or distributed rate limiting
- real external tool adapters
- LLM/OpenAI calls
- frontend dashboard
- production deployment hardening

## V1 Security Claim

V1 demonstrates a safer agent harness shape:

```text
model/proposer suggests intent
server resolves identity
deterministic policy decides
approval gates high-risk execution
controlled tools execute dry-run actions
audit records the path
```

It should not be described as production-ready security infrastructure.
