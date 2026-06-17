# Redacted Evidence Example

This example shows the shape of acceptable evidence. Values are placeholders and
must not be copied from secrets. It intentionally avoids realistic token-like
strings.

## Decision Summary

```text
Decision: pass
Live smoke approved by Product Owner: yes, in A5.3 sprint record
Operator: local maintainer
Token value: [REDACTED]
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
Token env name: AGENT_FACTORY_GITHUB_TOKEN
Token present: [TOKEN_PRESENT_TRUE]
Token value: [REDACTED]
Token scope: [SAFE_PLACEHOLDER_ONLY]
```

## A5.2 Preflight

```text
preflight_status: passed
mode: real
real_mode_explicit: true
ci_block_active: false
token_env_name: AGENT_FACTORY_GITHUB_TOKEN
token_present: true
token_value: REDACTED
allowlisted_repo: true
allowlisted_issue: true
fresh_side_effect_mode: fresh_issue
marker_format_verified: true
network_calls_attempted: 0
```

## Allowlist

```text
Allowed repository: owner/example-test-repo
Allowed issue: 1
Rejected repository: owner/not-allowed
Rejected repository HTTP calls: 0
Negative allowlist proof: [SAFE_PLACEHOLDER_ONLY]
```

## Side Effect

```text
Tool: post_github_issue_comment
Side effect id: [SIDE_EFFECT_ID]
Validated arguments hash: [ARGS_HASH]
External comment id: [SAFE_PLACEHOLDER_ONLY]
External comment url: [COMMENT URL]
Ledger status before: [LEDGER STATUS]
Ledger status after: [LEDGER STATUS]
```

## Marker

```html
<!-- agent_factory:v1 side_effect_id=[SIDE_EFFECT_ID] args_hash=[ARGS_HASH] -->
```

## Audit Events

```text
repository_allowed
remote_marker_check_started
remote_marker_not_found
real_client_create_comment_called
Audit event ids: [AUDIT EVENT IDS]
Audit metadata redacted: yes
Audit token values: none
```

## Redaction Proof

```text
redaction check: pass
token-like values in docs/evidence/logs: none found
redaction proof: [REDACTION TEST OUTPUT]
zero-network negative proof: [ZERO HTTP CALLS PROOF]
```

## Final Conclusion

```text
Final conclusion: release gate packet is reviewable and redacted
Known limitations: local/demo harness, manual smoke only, no production claim
Next sprint: A5.3 controlled live smoke execution, only after explicit approval
```

This example intentionally omits token values, Authorization headers, raw
response headers, `.env` contents, and unredacted transport exceptions.
