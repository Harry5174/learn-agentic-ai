# Durable Audit Demo

Artifact 4 implements a `DurableAuditStore` using SQLite to provide restart-surviving evidence of execution outcomes for the local/demo fake-client GitHub comment path.

**Note:** This describes representative/test-backed behavior.

## The Audit Event Lifecycle

The execution of a side effect produces a series of durable audit events that track its progression through the safety harness. These events are persisted in the `durable_audit_events` SQLite table.

### Successful Execution Path
When a new approved action executes successfully, the following sequence of events is durably recorded:
1. `execution_requested`: The harness receives the request to run the action.
2. `approval_authorized`: The harness verifies a valid, persisted approval binding matches the requested action.
3. `execution_started`: The side effect record is marked as executing.
4. `fake_client_called`: The `FakeGitHubIssueCommentClient` is invoked.
5. `execution_succeeded`: The fake client returns success, and the side effect is durably marked as succeeded.

### Duplicate Replay Path
If a process restart occurs and a previously successful action is replayed, the sequence is:
1. `execution_requested`
2. `duplicate_suppressed`: The harness recognizes the prior success and suppresses execution. The fake client is not called.

### Blocked Execution Path
If execution is prevented (e.g., due to missing approval or an expired binding):
1. `execution_requested`
2. `execution_blocked`: The harness blocks the execution. The fake client is not called.

### Fake-Client Failure Path
If the fake client raises an exception or simulates a network failure:
1. `execution_requested`
2. `approval_authorized`
3. `execution_started`
4. `fake_client_called`
5. `execution_failed`: The failure is caught, and the side effect is durably marked as failed. This state is terminal.

## Re-instantiation Proof
Because these events are persisted to SQLite, they survive process re-instantiation. If the service and stores are recreated against the same SQLite file, the complete audit trail of `execution_succeeded`, `duplicate_suppressed`, `execution_blocked`, or `execution_failed` remains intact and queryable.
