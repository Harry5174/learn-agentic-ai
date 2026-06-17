# Remote Idempotency And Reconciliation

## Purpose

This page defines the Artifact 5 boundary for remote idempotency in the real
GitHub issue-comment adapter.

A5.2 implements marker construction, marker parsing, fake/mocked remote comment
listing, marker lookup, and durable reconciliation tests. A5.3 adds one
approval-gated real issue-comment path that performs live remote lookup and
posting only when explicit server-side real-mode configuration is injected.

## Local And Remote State

Artifact 4 proves local/demo durable state with SQLite for the fake-client path.
That is necessary, but not sufficient, for real GitHub execution.

For a real GitHub comment, the harness has two persistence systems:

- SQLite for local side-effect, approval, and audit state
- GitHub for the externally visible issue comment

Those systems cannot commit atomically. The design must assume a crash can occur
between a successful GitHub POST and local success recording.

## Required Crash Window

```text
1. GitHub comment POST succeeds.
2. Process crashes before SQLite records succeeded.
3. Service restarts.
4. Local ledger is not succeeded.
5. Replay attempts execution.
6. Without remote marker lookup, duplicate real comment may be posted.
```

This is why local SQLite idempotency alone cannot support real GitHub execution.

## Marker Format

A5.3 real GitHub comments include this marker in the posted body:

```html
<!-- agent_factory:v1 side_effect_id=<side_effect_id> args_hash=<validated_arguments_hash> -->
```

The marker must be produced by trusted harness code after validation. It must
not be taken from the model, user input, request body text, or tool arguments.

Required properties:

- deterministic
- machine-readable
- exact-match searchable
- bound to `side_effect_id`
- bound to `validated_arguments_hash`
- included in the actual posted GitHub comment body
- not treated as a secret

## Reconciliation Before Posting

A5.3 applies the following rule before any real post:

```text
1. List existing issue comments.
2. Search for exact marker containing side_effect_id and validated_arguments_hash.
3. If exact marker exists, do not post.
4. Reconcile local durable state to succeeded/already_posted.
5. Persist external GitHub comment id/url if available.
6. Record durable audit event.
7. If marker lookup fails, fail closed.
```

The lookup must happen after local validation, repository allowlist checks,
durable ledger checks, durable approval binding, explicit real-mode checks, and
server-side token loading, but before the real POST.

The marker is not authorization. A5.3 reconciliation does not bypass approval,
does not authorize unapproved planned records, and does not create local durable
records from remote marker text. It reconciles only existing approved/executing
durable records whose side-effect id, validated argument hash, repository, issue
number, and tool match the local request.

## Fail-Closed Cases

The adapter must not post when remote marker state is unsafe, ambiguous, or
incomplete.

Required fail-closed cases:

- marker lookup failure
- multiple matching remote markers unless separately approved
- same `side_effect_id` with different `validated_arguments_hash`
- remote API ambiguity
- repository not allowlisted
- token unavailable or rejected by the server-side token provider
- incomplete remote comment listing
- GitHub HTTP, timeout, transport, or malformed-response failures

## Durable Audit Evidence

A5.3 records durable audit evidence for the remote marker decision. These
decisions are auditable:

- `remote_marker_check_started`
- `remote_marker_found`
- `remote_marker_not_found`
- `remote_marker_ambiguous`
- `remote_marker_mismatch`
- `remote_marker_lookup_failed`
- `remote_reconciled`
- `execution_blocked`
- `repository_allowed`
- `repository_blocked`
- `real_client_list_comments_called`
- `real_client_create_comment_called`

Audit metadata may include marker status, side-effect id, validated argument
hash, repository, issue number, external comment id, and external comment URL
when available.

Audit metadata must not include GitHub tokens, Authorization headers, realistic
secret values, or raw exception text that could contain credentials.

## Relationship To Local Ledger

The local ledger remains the source of harness-owned side-effect lifecycle
state. Remote reconciliation is an additional safety step for real external
effects, not a replacement for local validation, approval binding, or durable
audit.

When an exact remote marker already exists, A5.3 real mode reconciles local
durable state to a succeeded/already_posted outcome and preserves the external
comment id/url if GitHub exposes them.

When marker lookup fails or is ambiguous, A5.3 real mode records a blocked
outcome and avoids the POST.

## A5.3 Boundary

A5.3 adds real issue-comment list/create behavior only for the explicitly
configured approval-gated path. It does not add:

- automated live GitHub tests
- manual smoke execution by default
- arbitrary repository support
- issue creation, PR creation, branch creation, repo file writes, workflow
  dispatch, labels, milestones, assignees, edit, or delete operations
