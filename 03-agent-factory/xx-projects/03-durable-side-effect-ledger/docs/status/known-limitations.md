# Known Limitations

This file lists current limits so Artifact 4 stays honest as a portfolio artifact.

## Current Scope

Artifact 4 - Durable Side-Effect Ledger and Approval Binding is at A4.2.

A4.0 is documentation/specification only. It does not change runtime behavior.

A4.1 implements the SQLite-backed `DurableSideEffectLedger`. It does not integrate with graph/service execution.

A4.2 implements the SQLite-backed `DurableApprovalBindingStore`. It persists approval decisions against exact `side_effect_id` and `validated_arguments_hash`. It does not integrate with graph/service execution.

## Not Implemented Yet

Artifact 4 has not implemented:

- durable audit store runtime code
- durable graph/service integration
- durable API behavior
- restart-safe execution behavior (full restart-replay proof)
- real GitHub execution
- real GitHub client
- GitHub token loading
- production persistence
- production audit guarantees

## Inherited Local/Demo Runtime

The copied runtime still inherits Artifact 3 local/demo behavior:

- process-local graph/checkpoint state
- process-local side-effect ledger in graph path
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
- the graph-path side-effect ledger is still in-memory
- rate limit windows reset on process restart
- the durable stores exist but are not wired into the graph/service execution path

A4.2 implements durable approval bindings and side-effect records in SQLite, but graph/service integration is deferred to a future sprint.

## Approval Binding Consistency

A4.2 approve and reject transitions update both `approval_bindings` and `side_effect_records` in a single SQLite transaction using the same connection. This prevents partial state for the approve/reject path.

The `expire` transition only updates `approval_bindings` and does not mutate `side_effect_records`. This is a deliberate V1 design decision: expired is an approval-binding state, not a side-effect execution state.

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

Artifact 4 A4.2 should not be described as production security infrastructure.

It implements durable approval binding and side-effect ledger persistence for a local/demo approval-binding proof. It does not yet provide full restart-safe side-effect execution, durable audit evidence at runtime, or graph/service integration.

The project is not production-ready.
