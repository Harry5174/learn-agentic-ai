# Artifact 3 vs Artifact 4 Comparison

Artifact 4 is the direct continuation of the completed Artifact 3 project. This document highlights the architectural differences and the evolving safety guarantees between the two artifacts.

## Artifact 3: Process-Local Safety
Artifact 3 proved approval-gated fake-client side-effect control.
- **Ledger:** Used an `InMemorySideEffectLedger` to prevent duplicate execution within the same running process.
- **Approval:** Approvals were verified but not durably bound to the specific action across process boundaries.
- **Audit:** Audit evidence was kept in memory.
- **Limitation:** If the process restarted, all knowledge of past executions, approvals, and audit trails was lost.

## Artifact 4: Durable Safety
Artifact 4 adds SQLite-backed persistence to achieve restart-safe side-effect control.
- **Ledger:** Uses a `DurableSideEffectLedger` backed by SQLite. Side-effect records and their statuses survive process restarts.
- **Approval:** Uses a `DurableApprovalBindingStore`. Approvals are durably bound to the exact `side_effect_id` and `validated_arguments_hash`.
- **Duplicate Suppression:** Proves restart/replay duplicate suppression. A fresh instance of the service connected to the same SQLite file will not re-execute a previously succeeded fake-client action.
- **Audit:** Uses a `DurableAuditStore` to persist restart-surviving audit events tracking the execution lifecycle (e.g., `execution_succeeded`, `duplicate_suppressed`, `execution_blocked`).

## Shared Constraints (What Did Not Change)
Artifact 4 **still does not perform real GitHub network execution**.
Both artifacts operate entirely as local/demo safety harnesses utilizing a `FakeGitHubIssueCommentClient`. There is no GitHub token loading, no real GitHub API execution, and neither artifact claims production-readiness or universal exactly-once execution guarantees.
