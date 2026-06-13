# A4.3/A4.4 Restart-Replay Demo

This demo describes the A4.3 local/demo restart/replay proof and the A4.4 durable audit evidence added around that path. It does not post real GitHub comments, does not load GitHub tokens, and does not use a real GitHub client.

## What A4.3 Demonstrates

A4.3 demonstrates restart-replay duplicate suppression for the local/demo fake-client GitHub comment path using SQLite-backed side-effect and approval records.

The proof sequence is:

```text
1. Create a temporary SQLite file.
2. Create service/store/context objects against that file.
3. Persist a planned side-effect record for a validated GitHub comment action.
4. Persist and approve an approval binding for the exact side_effect_id and validated_arguments_hash.
5. Execute the GitHub comment path.
6. FakeGitHubIssueCommentClient is called once.
7. side_effect_records.status becomes succeeded.
8. Discard the first store/context/fake-client objects.
9. Create fresh store/context/fake-client objects against the same SQLite file.
10. Replay the same action.
11. The fresh fake client is not called.
12. The tool result reports already_succeeded / duplicate-suppressed evidence.
13. side_effect_records.status remains succeeded.
14. In A4.4, durable_audit_events records duplicate_suppressed evidence when DurableAuditStore is injected.
```

## Execution Boundary

A4.3 still executes only through `FakeGitHubIssueCommentClient`. The replay proof verifies call counts on fake clients. It does not use `requests`, `httpx`, PyGithub, `GITHUB_TOKEN`, or any real GitHub network path.

## Replay Outcome

A4.3 preserves the original durable success record:

```text
succeeded -> already_succeeded result
succeeded remains succeeded
fake client is not called again
```

It does not rewrite `succeeded` to `skipped_duplicate`.

In A4.4, duplicate replay is also visible in `durable_audit_events` as local/demo audit evidence.

## Unsafe-To-Retry Case

If restart/replay sees:

```text
side_effect_records.status = executing
```

A4.3 does not call the fake client. It returns unsafe-to-retry / already-executing evidence because an interrupted executing attempt may already have performed a side effect.

## Limitation

A4.4 adds durable local/demo audit evidence around the same path, but it is not production-grade audit or compliance audit.

A4.4 proves duplicate suppression after durable success exists. It does not prove production-grade exactly-once semantics across every crash window. If the fake client succeeds but the process dies before `side_effect_records` is marked `succeeded`, A4.4 does not prove universal duplicate suppression for that interrupted attempt.
