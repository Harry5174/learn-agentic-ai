# Evidence Bundle Template

Use this template for a future A5.x release-gate evidence bundle. Replace every
value with a redacted placeholder or a short status statement. Do not paste
token values, Authorization header values, `.env` contents, raw unredacted
transport exceptions, or realistic-looking fake secrets.

Safe placeholders:

```text
[TOKEN PRESENT: YES/NO]
[TOKEN VALUE: REDACTED]
[COMMENT URL]
[SIDE_EFFECT_ID]
[ARGS_HASH]
[REMOTE MARKER]
[LEDGER STATUS]
[AUDIT EVENT IDS]
[ZERO HTTP CALLS PROOF]
[REDACTION TEST OUTPUT]
```

## 1. Final Release-Gate Conclusion

```text
Release gate decision:
Sprint:
Date:
Operator:
Conclusion:
Known limitations:
Recommended follow-up:
```

This conclusion must not claim production readiness, arbitrary repository
support, or universal exactly-once execution.

## 2. Artifact 04 Closeout Verification

```text
Expected closeout commit: 9ef8ab8
Artifact 04 final tag target:
Verification command output:
Design Supervisor newer-closeout approval: yes/no
```

The final Artifact 04 tag must point to `9ef8ab8`, unless a newer closeout
commit has been explicitly approved by the Design Supervisor.

## 3. Branch And Commit Status

```text
Artifact 05 branch:
Artifact 05 commit:
git status -sb:
git status --short:
Relevant git log:
```

## 4. Manual Live-Run Approval Record

```text
Live smoke sprint:
Product Owner explicit live-run approval:
Approval timestamp:
Approval source:
Approval text excerpt:
```

A5.3 may not run live GitHub unless the Product Owner explicitly approves the
live smoke step in that sprint. No implicit live approval is allowed.

## 5. Preflight Evidence

```text
A5.1 redaction checklist complete:
A5.2 preflight gate complete:
A5.2 preflight status:
A5.2 preflight token_env_name: AGENT_FACTORY_GITHUB_TOKEN
A5.2 preflight token_present: [TOKEN PRESENT: YES/NO]
A5.2 preflight network_calls_attempted: 0
.env ignored:
.env untracked:
.env unstaged:
Token presence recorded safely: [TOKEN PRESENT: YES/NO]
Token value: [TOKEN VALUE: REDACTED]
Token source: server-side environment only
Token scope confirmed: one repository, Issues read/write only
No Contents permission:
No Actions/workflows permission:
Short expiration:
Evidence output path:
Rollback/cleanup note:
```

Do not include command output that prints `.env` contents or token values.

## 6. Fresh Side-Effect Rule Evidence

Before A5.3 live smoke, one of the following must be true:

- fresh test issue with no previous marker
- new unique validated comment body producing a new `side_effect_id`
- explicit reconciliation path if marker already exists

```text
Selected fresh side-effect path:
Fresh test issue evidence:
Unique comment body evidence:
Reconciliation approval if marker already exists:
Side effect id: [SIDE_EFFECT_ID]
Validated arguments hash: [ARGS_HASH]
```

## 7. Allowlisted Repo/Issue Evidence

```text
Allowed repository:
Allowed issue:
Server-owned allowlist source:
Request/model/tool did not widen allowlist:
```

## 8. Planned Side Effect

```text
Tool: post_github_issue_comment
Repository:
Issue:
Comment body description:
Side effect id: [SIDE_EFFECT_ID]
Validated arguments hash: [ARGS_HASH]
```

The only allowed live operation remains one GitHub issue comment.

## 9. Approval Binding Evidence

```text
Approval actor:
Approval binding side_effect_id: [SIDE_EFFECT_ID]
Approval binding validated_arguments_hash: [ARGS_HASH]
Approval binding status:
Approval binding checked before network:
```

## 10. Remote Marker Lookup Evidence

```text
Marker lookup started:
Remote marker searched: [REMOTE MARKER]
Marker found before post:
Marker absent before post:
Marker ambiguity:
Incomplete listing:
Lookup failure:
Reconciliation performed:
Post performed:
```

Marker lookup failure, ambiguity, or incomplete listing must fail closed.

## 11. Real Comment URL Placeholder

```text
External comment URL: [COMMENT URL]
External comment id:
```

Use a real URL only in the future A5.3 evidence packet after the explicitly
approved live run. Until then, keep `[COMMENT URL]`.

## 12. SQLite Side-Effect Records Evidence

```text
Ledger state before: [LEDGER STATUS]
Ledger state after: [LEDGER STATUS]
External comment id persisted:
External comment URL persisted: [COMMENT URL]
Replay state:
```

## 13. Audit Trail Evidence

Expected event names may include:

```text
repository_allowed
remote_marker_check_started
remote_marker_found
remote_marker_not_found
remote_reconciled
real_client_list_comments_called
real_client_create_comment_called
execution_blocked
```

Evidence:

```text
Audit event ids: [AUDIT EVENT IDS]
Audit metadata redacted:
No token values in audit metadata:
No Authorization headers in audit metadata:
```

## 14. Replay / No-Duplicate Evidence

```text
Replay command or mocked replay evidence:
Local duplicate suppression:
Remote marker duplicate prevention:
Second POST attempted:
Result:
```

The marker is idempotency evidence only. It is not authorization and does not
bypass durable approval binding.

## 15. Negative Allowlist Zero-Network Evidence

The non-allowlisted repo/issue test must prove rejection happened before
network execution.

```text
Rejected repository/issue test:
Rejection point:
Zero HTTP call proof: [ZERO HTTP CALLS PROOF]
Mocked/spy transport HTTP call count:
A5.2 preflight network_calls_attempted: 0
```

Evidence that only shows a GitHub error after a network attempt is not
acceptable.

## 16. Redaction Proof

Include either redaction test output:

```text
[REDACTION TEST OUTPUT]
```

or grep output proving no token-like values appear in generated
docs/evidence/log artifacts:

```text
Generated evidence path:
Token-like pattern scan output:
Expected result: no matches in generated evidence/log artifacts
```

Safety checklist documents may intentionally mention detection patterns. Do not
use those intentional documentation references as proof that generated evidence
contains a secret.

## 17. Known Limitations

```text
Local/demo limitation acknowledged:
Manual run limitation acknowledged:
Remote marker deletion/editing risk acknowledged:
GitHub availability/rate-limit risk acknowledged:
Bounded pagination risk acknowledged:
No production-readiness claim:
No universal exactly-once claim:
```
