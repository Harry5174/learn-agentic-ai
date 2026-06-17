# Evidence Bundle Template

Use this template for a future A5.x release-gate evidence bundle. Replace
examples with redacted values only.

## 1. Decision Summary

```text
Decision:
Live smoke approved by Product Owner:
Sprint:
Date:
Operator:
```

## 2. Artifact 04 Baseline

```text
Expected closeout commit: 9ef8ab8
Artifact 04 final tag:
Remote main:
Verification commands:
```

The final Artifact 04 tag must point to `9ef8ab8`, unless a newer closeout
commit has been explicitly approved by the Design Supervisor.

## 3. Workspace And Branch

```text
Branch:
git status -sb:
git status --short:
```

## 4. Credential Hygiene

Do not include token values.

```text
.env ignored:
.env untracked:
.env unstaged:
Token source: server-side environment only
Token scope: fine-grained PAT, one repository, Issues read/write only
No Contents permission:
No Actions/workflows permission:
Short expiration:
```

## 5. Allowlist

```text
Allowed repository:
Allowed issue:
Rejected repository/issue test:
Zero HTTP call proof for rejection:
```

The negative allowlist test must prove rejection happened before network
execution. Preferred evidence is mocked/spy transport showing zero HTTP calls.

## 6. Planned Side Effect

```text
Tool:
Repository:
Issue:
Side effect id:
Validated arguments hash:
Comment body description:
```

Before live smoke, one of the following must be true:

- fresh test issue with no previous marker
- new unique validated comment body producing a new `side_effect_id`
- explicit reconciliation path if marker already exists

## 7. Approval Binding

```text
Approval actor:
Approval binding side_effect_id:
Approval binding validated_arguments_hash:
Approval binding status:
```

## 8. Durable Ledger

```text
Ledger state before:
Ledger state after:
External comment id:
External comment url:
```

## 9. Remote Marker Lookup

```text
Marker lookup started:
Marker result:
Marker found before post:
Marker absent before post:
Reconciliation performed:
Post performed:
```

Marker lookup failure, ambiguity, or incomplete listing must fail closed.

## 10. Durable Audit Events

Expected event names may include:

```text
repository_allowed
remote_marker_check_started
remote_marker_found
remote_marker_not_found
remote_reconciled
real_client_create_comment_called
execution_blocked
```

## 11. Redaction Proof

Include either:

```text
redaction test output
```

or:

```text
grep output proving no token-like values appear in docs/evidence/logs
```

## 12. Block Conditions Review

```text
No credential printed:
No .env contents read:
No CI live GitHub execution:
No unsupported GitHub operation:
No arbitrary repository support:
No production-ready claim:
```

## 13. Final Decision

```text
Release gate decision:
Known limitations:
Follow-up:
```

