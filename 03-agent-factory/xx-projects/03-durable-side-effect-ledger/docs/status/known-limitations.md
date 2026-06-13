# Known Limitations

This file lists current limits so Artifact 4 stays honest as a portfolio artifact.

## A4.0 Scope

Artifact 4 - Durable Side-Effect Ledger and Approval Binding starts at A4.0 as a baseline/spec sprint copied from completed Artifact 3.

A4.0 is documentation/specification only. It does not change runtime behavior.

## Not Implemented Yet

Artifact 4 has not implemented:

- SQLite persistence
- durable side-effect ledger runtime code
- durable approval binding runtime code
- durable audit store runtime code
- durable graph/service integration
- durable API behavior
- restart-safe execution behavior
- real GitHub execution
- real GitHub client
- GitHub token loading
- production persistence
- production audit guarantees

## Inherited Local/Demo Runtime

The copied runtime still inherits Artifact 3 local/demo behavior:

- process-local graph/checkpoint state
- process-local side-effect ledger
- in-memory audit events
- static demo API keys
- fake proposer scenarios
- fake-client GitHub issue-comment execution

This inherited behavior is useful for local tests and demos, but it does not prove restart-safe side-effect execution.

## Persistence

Current limits:

- checkpoints do not survive process restart
- task/run state is not stored in a database
- audit events are not durably persisted
- side-effect ledger records are in-memory only
- rate limit windows reset on process restart
- `ApprovalDecision` does not persist `validated_arguments_hash`
- `ApprovalDecision` does not persist `side_effect_id`

A4.0 defines future durable-state semantics to address those limits later.

## Tool Execution

Tools remain local/demo only.

The inherited GitHub issue-comment path uses `FakeGitHubIssueCommentClient` for simulated local/demo execution only.

Not implemented:

- real GitHub client code
- real GitHub writes
- real issue comments
- real workflow triggers
- external side-effecting adapters
- automatic token loading

## Product Surface

Not implemented:

- frontend
- multi-agent behavior
- MCP
- OAuth/OIDC
- JWT validation
- production deployment demo
- operational monitoring

## Security Claim

Artifact 4 A4.0 should not be described as production security infrastructure.

It defines planned durable-state design for a local/demo restart-replay proof. It does not yet provide durable replay protection, durable approval binding, or durable audit evidence at runtime.

The project is not production-ready.
