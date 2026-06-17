# Redacted Evidence Example

This example shows the shape of acceptable evidence. Values are placeholders and
must not be copied from secrets.

## Decision Summary

```text
Decision: pass
Live smoke approved by Product Owner: yes, in A5.3 sprint record
Operator: local maintainer
```

## Baseline

```text
Expected Artifact 04 closeout commit: 9ef8ab8
Artifact 04 tag target: 9ef8ab8...
Remote main target: 9ef8ab8...
```

## Credential Hygiene

```text
.env ignored: yes
.env tracked: no
.env contents printed: no
Token source: server-side environment only
Token value: [REDACTED]
```

## Allowlist

```text
Allowed repository: owner/example-test-repo
Allowed issue: 1
Rejected repository: owner/not-allowed
Rejected repository HTTP calls: 0
```

## Side Effect

```text
Tool: post_github_issue_comment
Side effect id: side_effect_[REDACTED_ID]
Validated arguments hash: hash_[REDACTED_HASH]
External comment id: github_comment_[REDACTED_ID]
External comment url: https://github.com/owner/example-test-repo/issues/1#issuecomment-[REDACTED]
```

## Marker

```html
<!-- agent_factory:v1 side_effect_id=side_effect_[REDACTED_ID] args_hash=hash_[REDACTED_HASH] -->
```

## Audit Events

```text
repository_allowed
remote_marker_check_started
remote_marker_not_found
real_client_create_comment_called
```

## Redaction Proof

```text
redaction check: pass
token-like values in docs/evidence/logs: none found
```

This example intentionally omits token values, Authorization headers, raw
response headers, `.env` contents, and unredacted transport exceptions.

