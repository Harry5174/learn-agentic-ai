# A4.4 Durable Audit Demo

This demo describes the A4.4 local/demo durable audit proof. It does not post real GitHub comments, does not load GitHub tokens, and does not use a real GitHub client.

## What A4.4 Demonstrates

A4.4 demonstrates restart-surviving audit evidence for the durable fake-client GitHub comment path.

The proof sequence is:

```text
1. Create a temporary SQLite file.
2. Create durable side-effect, approval, and audit stores against that file.
3. Persist a planned side-effect record for a validated GitHub comment action.
4. Persist and approve an approval binding for the exact side_effect_id and validated_arguments_hash.
5. Execute the GitHub comment path with DurableAuditStore injected at runtime.
6. FakeGitHubIssueCommentClient is called once.
7. side_effect_records.status becomes succeeded.
8. durable_audit_events records execution_requested, approval_authorized, execution_started, fake_client_called, and execution_succeeded.
9. Discard the first store/context/fake-client objects.
10. Create fresh store/context/fake-client objects against the same SQLite file.
11. Replay the same action.
12. The fresh fake client is not called.
13. durable_audit_events records duplicate_suppressed.
14. A fresh DurableAuditStore can list the prior audit events by run_id or side_effect_id.
```

## Blocked and Failed Outcomes

A4.4 also records durable local/demo evidence when execution is not allowed:

```text
approval missing / pending / rejected / expired -> execution_blocked
wrong side_effect_id or validated_arguments_hash -> execution_blocked
blocked / rejected / failed / executing / skipped_duplicate side-effect status -> execution_blocked
fake-client failure -> execution_failed
```

Blocked attempts do not call the fake client.

## Metadata Safety

Durable audit metadata is intentionally small. It stores local/demo identifiers, side-effect status, replay outcome, repository, issue number, and fake result summaries.

It does not store raw GitHub tokens, authorization headers, client transport config, or full raw rejected payloads. Tests check the raw `durable_audit_events.metadata_json` value in SQLite.

## Boundary

A4.4 is not production-grade audit and not compliance audit. It is local/demo durable evidence for side-effect lifecycle decisions.

A4.4 still does not execute real GitHub calls, load GitHub tokens, add a real GitHub client, or claim universal exactly-once execution.
