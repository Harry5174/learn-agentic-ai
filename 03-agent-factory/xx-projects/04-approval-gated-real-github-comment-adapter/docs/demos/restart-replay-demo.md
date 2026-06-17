# Restart / Replay Demo

Artifact 4 integrates SQLite-backed durable side-effect records, approval bindings, and audit events into the fake-client GitHub issue-comment execution path. A core capability proven by this integration is restart/replay duplicate suppression.

**Note:** This describes representative/test-backed behavior. The default public HTTP API startup currently does not wire up the SQLite database to demonstrate this via `curl`.

## The Replay Scenario

### 1. First Approved Execution
An approved side effect is executed for the first time. The `SkillGraphService` verifies the `DurableApprovalBindingStore` and then calls the `FakeGitHubIssueCommentClient`. The fake network call succeeds, and the `DurableSideEffectLedger` marks the record as `succeeded`.

### 2. Simulated Process Restart
The service, stores, and fake-client objects are discarded, simulating a process exit or crash after durable success was recorded. Fresh instances of the `SkillGraphService`, `DurableSideEffectLedger`, `DurableApprovalBindingStore`, and `FakeGitHubIssueCommentClient` are re-instantiated, connected to the same underlying SQLite file.

### 3. Replay Attempt
The exact same approved action (with the identical `side_effect_id` and `validated_arguments_hash`) is requested again.

### 4. Duplicate Suppression
The `SkillGraphService` consults the `DurableSideEffectLedger` before attempting execution. It discovers that the side effect is already `succeeded`.
The service returns an `already_succeeded` or `duplicate_suppressed` evidence result.
Crucially, **the fake client is not called again**.

## Conclusion
This proves that an approved side effect that has achieved durable success will survive a process restart without triggering duplicate execution, acting as a local/demo safety harness for exactly-once side-effect execution within the bounded context.
