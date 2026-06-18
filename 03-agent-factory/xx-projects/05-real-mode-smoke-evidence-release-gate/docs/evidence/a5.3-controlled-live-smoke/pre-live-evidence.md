# A5.3 Pre-Live Evidence

Status: Gate 2 preparation completed before the approved live smoke. The live
result is recorded in `live-result.md`.

## Branch And Baseline

```text
Artifact 05 branch: artifact-5.3-controlled-live-smoke-execution
Artifact 05 starting commit: 4446a3a5f48073bc9a88c7c8f56f65325fe7bab8
Artifact 04 expected tag target: 9ef8ab86a46bda254137a7c8e5c0984ea9384cf8
Artifact 04 remote tag verified: 9ef8ab86a46bda254137a7c8e5c0984ea9384cf8
```

## Target

```text
Repository: Harry5174/artifact-5-github-comment-test
Issue: 1
Allowed repository: yes
Allowed issue: yes
```

## Planned Unique Comment Body

```text
A5.3 controlled live smoke candidate. Prepared 2026-06-18. Unique key: a5.3-controlled-live-smoke-2026-06-18-gate2.
```

This body is non-secret and is intended to produce a fresh validated argument
hash for the A5.3 live boundary.

## Planned Harness Metadata

Derived from the Artifact 04 idempotency algorithm:

```text
skill_run_id: a5.3-controlled-live-smoke-2026-06-18
step_id: post_comment
tool_name: post_github_issue_comment
validated_arguments_hash: 5cedbfca87b2306cda1c27e89abbb4f751ee8876856a8450852ba4e57b84d792
side_effect_id: 35f403dec6aa79b3f6ab16de0e8fbd7b5a2f90db15d46e404e0ae079f78dbae3
fresh_side_effect_mode: new_unique_body
```

## Preflight Summary

Redacted A5.2 preflight helper output:

```text
preflight_status: passed
mode: real
real_mode_explicit: true
ci_block_active: false
token_env_name: AGENT_FACTORY_GITHUB_TOKEN
token_present: [TOKEN PRESENT: YES]
token_value: REDACTED
allowlisted_repo: true
allowlisted_issue: true
fresh_side_effect_mode: new_unique_body
marker_format_verified: true
network_calls_attempted: 0
failure_reason: omitted
```

Gate 2 preflight passed after loading token presence into the local shell
environment. The token value was not printed.

For local A5.3 smoke only, the live snippet loaded
`AGENT_FACTORY_GITHUB_TOKEN` from the local Artifact 04 `.env` file into
process memory without printing, committing, or recording the token value. This
is a test-only exception and not production behavior.

## Redaction Proof Placeholders

```text
.env contents printed: no
Token value printed: no
Authorization header printed: no
Raw environment dump printed: no
External comment URL: [COMMENT URL]
Remote marker: [REMOTE MARKER]
Audit event ids: [AUDIT EVENT IDS]
```

## Stop Conditions

The live smoke was blocked before execution if any of these were true:

- Product Owner live approval phrase is missing.
- Token is missing.
- `.env` is tracked, staged, printed, or committed.
- Repository or issue is not allowlisted.
- Artifact 04 tag/baseline verification fails.
- A5.2 preflight fails.
- Marker lookup is found, ambiguous, mismatched, incomplete, or failed.
- The flow requires adding a new live runner, CLI, adapter, or runtime code.
