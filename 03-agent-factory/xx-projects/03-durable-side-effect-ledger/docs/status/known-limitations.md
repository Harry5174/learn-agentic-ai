# Known Limitations

This file lists current limits so Artifact 4 stays honest as a portfolio artifact.

## Current Scope

Artifact 4 - Durable Side-Effect Ledger and Approval Binding is at A4.4.

A4.0 is documentation/specification only. It does not change runtime behavior.

A4.1 implements the SQLite-backed `DurableSideEffectLedger`. It does not integrate with graph/service execution.

A4.2 implements the SQLite-backed `DurableApprovalBindingStore`. It persists approval decisions against exact `side_effect_id` and `validated_arguments_hash`.

A4.3 integrates those durable stores into the fake-client GitHub issue-comment execution path through explicit dependency injection. It proves restart/replay duplicate suppression after durable success has already been recorded.

A4.3.1 modularized the restart/replay implementation and graph/tool boundaries without adding runtime behavior.

A4.4 implements local/demo durable audit events and adversarial persistence tests. It records restart-surviving evidence for execution, duplicate suppression, blocked attempts, and fake-client failures when `DurableAuditStore` is explicitly injected.

A4.5 is a documentation and portfolio-packaging sprint that does not change runtime behavior.

## Not Implemented Yet

Artifact 4 has not implemented:

- default durable API startup requiring a SQLite file
- real GitHub execution
- real GitHub client
- GitHub token loading
- production persistence
- production-grade audit guarantees
- compliance audit
- production-grade exactly-once execution

## Inherited Local/Demo Runtime

The copied runtime still inherits Artifact 3 local/demo behavior:

- process-local graph/checkpoint state
- process-local side-effect ledger in default graph path unless durable stores are explicitly injected
- in-memory audit events
- static demo API keys
- fake proposer scenarios
- fake-client GitHub issue-comment execution

This inherited behavior is useful for local tests and demos. A4.4 adds a durable restart-replay proof and local/demo durable audit evidence for the fake-client GitHub comment path, but does not turn the whole app into durable production infrastructure.

## Persistence

Current limits:

- checkpoints do not survive process restart
- task/run state is not stored in a database
- durable audit events are persisted only when `DurableAuditStore` is explicitly injected
- the default graph-path side-effect ledger is still in-memory
- rate limit windows reset on process restart

A4.4 wires durable side-effect, approval, and audit stores into the GitHub comment execution path only when explicitly injected. The durable stores are not hidden globals, and no committed database file is required.

## Approval Binding Consistency

A4.2 approve and reject transitions update both `approval_bindings` and `side_effect_records` in a single SQLite transaction using the same connection. This prevents partial state for the approve/reject path.

The `expire` transition only updates `approval_bindings` and does not mutate `side_effect_records`. This is a deliberate V1 design decision: expired is an approval-binding state, not a side-effect execution state.

## Tool Execution

Tools remain local/demo only.

The GitHub issue-comment path uses `FakeGitHubIssueCommentClient` for simulated local/demo execution only. A4.3 persists succeeded or failed fake-client execution evidence in SQLite when durable dependencies are injected.
A4.4 additionally persists local/demo audit events for the durable fake-client path when `DurableAuditStore` is injected.

Replay behavior:

- `succeeded` returns already_succeeded / duplicate-suppressed evidence and remains `succeeded`
- `executing` is treated as unsafe to retry and does not call the fake client
- `failed` is terminal and does not auto-retry

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

Artifact 4 A4.4 should not be described as production security infrastructure.

It implements durable approval binding, side-effect ledger persistence, restart-replay duplicate suppression, and local/demo durable audit events for a fake-client proof. It does not provide production-grade audit or compliance audit.

A4.4 demonstrates duplicate suppression after durable success exists. If the fake client call succeeds but the process dies before `side_effect_records` is marked `succeeded`, A4.4 does not prove production-grade exactly-once semantics for that crash window.

The project is not production-ready.
