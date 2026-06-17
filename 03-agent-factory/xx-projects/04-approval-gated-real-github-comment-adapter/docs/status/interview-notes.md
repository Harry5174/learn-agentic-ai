# Interview Notes

## One-Minute Explanation

I started with a fake-client approval-gated GitHub comment harness, added
durable SQLite side-effect state, then safely crossed into one real external
side effect. The key distributed-systems issue was the crash window between
GitHub accepting a comment and SQLite recording success. I handled that with a
remote idempotency marker embedded in the comment, remote lookup before post,
and reconciliation on replay. The model never directly calls GitHub; the harness
validates, approval-gates, allowlists, checks local/remote idempotency, uses
server-side tokens, and audits decisions.

## Project Thesis

```text
The LLM proposes.
The harness decides.
```

This is a controlled safety harness, not an end-user product. The model must
never directly execute tools, provide credentials, enable real mode, bypass
policy, or authorize side effects.

## Artifact Progression

**Artifact 4 (baseline):** Proved local/demo durable fake-client safety with
SQLite-backed side-effect records, durable approval bindings, durable audit
events, and restart/replay duplicate suppression. Intentionally did not
implement real GitHub execution, token loading, or remote marker lookup.

**Artifact 5 (this artifact):** Built on Artifact 4 to safely cross into one
real external side effect: posting a single GitHub issue comment.

## Sprint Progression

- **A5.0:** Defined the real-mode boundary, token scope, remote idempotency
  marker format, reconciliation behavior, fail-closed rules, and non-goals.
  Documentation/specification only.
- **A5.1:** Added safe client interface, server-side environment token provider,
  real-mode config boundary, and disabled real client. Tests prove fake client
  remains default, missing tokens fail closed, and token values stay out of
  results/audit.
- **A5.2:** Added deterministic marker builder/parser, fake/mocked remote
  comment listing, marker lookup outcomes (found, absent, mismatch, ambiguous,
  lookup failed), durable reconciliation, and crash-window simulation proving
  marker recovery does not post.
- **A5.3:** Added narrow real GitHub issue-comment client using standard-library
  HTTP, bounded pagination, repository allowlist enforcement, remote marker
  lookup before posting, marker-found reconciliation, marker-absent posting
  with deterministic marker appended, and durable audit for real-mode decisions.
- **A5.4:** Added adversarial token leakage tests, hostile transport exception
  redaction, repository allowlist bypass tests, approval/hash mutation tests,
  marker spoofing tests (quoted, duplicated, extra-field), HTTP/timeout failure
  tests, and crash-window replay through executing durable records.
- **A5.5:** Documentation, demo, and portfolio packaging. No runtime changes.

## Key Technical Decision: Remote Idempotency

The most interesting distributed-systems issue is the crash window:

```text
1. GitHub comment POST succeeds.
2. Process crashes before SQLite records succeeded.
3. Service restarts.
4. Local ledger is not succeeded.
5. Replay attempts execution.
6. Without remote marker lookup, duplicate real comment may be posted.
```

The solution: embed a harness-generated marker in the comment body, look it up
remotely before any post, and reconcile local state if the marker already exists.
If lookup fails or is ambiguous, fail closed.

```html
<!-- agent_factory:v1 side_effect_id=<side_effect_id> args_hash=<validated_arguments_hash> -->
```

This marker is not authorization. It does not bypass approval. It is a
reconciliation affordance for the crash window between two systems that cannot
commit atomically.

## Safety Controls Before Posting

```text
validated proposal
-> repository allowlist
-> validated_arguments_hash
-> side_effect_id
-> durable approval binding
-> local durable ledger check
-> explicit real-mode config
-> server-side token provider
-> remote marker lookup
-> reconcile if marker found
-> post once with marker if marker absent
-> persist external id/url
-> durable audit
```

## What Not To Overclaim

- **Not production-ready.** This is a local/demo artifact.
- **Not universal exactly-once.** Remote marker lookup reduces duplicate-post
  risk for the scoped path, but bounded pagination, remote deletion, and human
  editing remain documented limitations. The harness fails closed when lookup
  completeness is uncertain.
- **Not arbitrary GitHub automation.** One issue-comment operation only. One
  allowlisted repository for manual test. No PR, branch, issue creation, repo
  writes, or workflow dispatch.
- **Not OAuth-secured yet.** Token loading uses server-side environment only.
  No OAuth/OIDC, no MCP, no frontend, no deployment.

## What To Highlight

- The staged safety progression from fake to real
- The crash-window analysis and remote reconciliation design
- The adversarial test coverage
- The "harness decides" principle applied to real external effects
- The honest limitations and non-goals
