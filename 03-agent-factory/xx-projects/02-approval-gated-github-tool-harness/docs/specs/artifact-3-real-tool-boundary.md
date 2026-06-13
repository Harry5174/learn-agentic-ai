# Artifact 3 Real Tool Boundary

## 1. Purpose

A3.1 defines the future real side-effect boundary for Artifact 3, the
Approval-Gated GitHub Tool Harness.

A3.1 is documentation/specification only.

A3.1 does not implement GitHub execution. A3.1 does not add a GitHub client.
A3.1 does not add a side-effect ledger implementation. A3.1 does not add the
`post_github_issue_comment` tool.

A3.2 adds isolated GitHub issue-comment client and side-effect ledger
boundaries.

A3.3 wires those boundaries into exactly one approval-gated local/demo skill
path, `post_github_issue_comment`. A3.3 uses validated scalar arguments, a
trusted repository allowlist, explicit approval, `InMemorySideEffectLedger`,
and `FakeGitHubIssueCommentClient` simulated execution. A3.3 does not implement
real GitHub API execution.

The goal is to document the future contract before any real GitHub write path
exists, so later A3.x implementation work can stay narrow, auditable, and
fail-closed.

## 2. Future Tool Boundary

The current local/demo and future real side-effect tool name is:

```text
post_github_issue_comment
```

The future scalar arguments are:

```text
repository: string
issue_number: integer
comment_body: string
```

These arguments remain scalar-only. They must pass the existing Artifact
2.2-style validation boundary before any later real execution path can consider
them:

```text
LLM output
-> SkillProposal parsing
-> ProposalValidator
-> validated scalar arguments
-> policy
-> approval
-> side-effect boundary
```

Raw proposed arguments must never flow directly into real execution or
`ToolRegistry.execute()`.

## 3. Real Execution Preconditions

A future real GitHub issue comment may be posted only if all of these are true:

- server-derived identity exists
- required role/scope is present
- proposal is structurally valid
- arguments are registry-declared
- arguments are scalar-only
- arguments are validator-normalized
- policy allows the requested repository
- approval is explicitly granted
- approval binds to the validated action
- real GitHub mode is explicitly enabled
- GitHub client is configured
- `side_effect_id` is computed
- side-effect ledger reports no prior execution
- audit event is emitted before/after the side-effect attempt

If any precondition fails, later implementation must fail closed and must not
call GitHub.

A3.3 satisfies these gates only for the fake-client local/demo path. Real
GitHub mode remains absent.

## 4. Real-Mode Configuration Rule

Real GitHub mode should require explicit future configuration:

```text
REAL_GITHUB_ENABLED=true
```

The default must remain:

```text
false / dry-run
```

Real mode must never be inferred from the presence of a GitHub token alone. A
configured token without explicit real-mode enablement must still leave the
harness in dry-run behavior.

A3.3 does not implement this configuration.

## 5. GitHub Token Boundary

GitHub tokens are server-side configuration only.

The model/proposer must never provide:

```text
GitHub token
authorization header
API base URL
client config
transport config
```

Any proposal that attempts to provide credentials or client configuration
through tool arguments should be rejected as a control-plane or unsafe argument
attempt.

## 6. Repository Allowlist Policy

Recommended V1 policy:

```text
Only repositories explicitly configured in an allowlist may receive real comments.
```

Conceptual future configuration:

```text
ALLOWED_GITHUB_REPOSITORIES=Harry5174/learn-agentic-ai
```

The repository allowlist is a server-owned policy input. It must not be
provided by the model, request body, or proposed tool arguments.

A3.3 implements a minimal trusted in-code local/demo allowlist for the
fake-client path, defaulting to `Harry5174/learn-agentic-ai`. A3.3 does not
implement real-mode repository configuration.

## 7. Approval Binding Model

Future approval must bind to the exact validated action, not only the run ID.

Minimum approval binding fields:

```text
skill_run_id
step_id
tool_name
validated_arguments_hash
side_effect_id
```

The approval display may show human-readable repository, issue number, and
comment summary, but the executable approval decision should bind to the
validated action hash and side-effect identity.

If a paused run is resumed with different validated arguments, changed tool
name, changed step ID, or changed `side_effect_id`, the previous approval must
not authorize execution.

A3.3 binds approval to the validated tool arguments held in the current graph
state and computes `validated_arguments_hash` and `side_effect_id` immediately
before fake-client execution. The current `ApprovalDecision` schema does not
persist `validated_arguments_hash` or `side_effect_id`; stronger persisted
approval binding remains a future sprint.

## 8. Idempotency / Replay Protection

Future concepts:

```text
SideEffectLedger
SideEffectRecord
side_effect_id
```

The deterministic `side_effect_id` should be derived from:

```text
skill_run_id
step_id
tool_name
validated_arguments_hash
```

Required future flow:

```text
1. Compute side_effect_id.
2. Check ledger before real execution.
3. If ledger hit exists, skip real GitHub call and return cached/skipped result.
4. If ledger miss exists, execute through GitHub client.
5. Record result in ledger.
6. Emit audit evidence.
```

The ledger exists to prevent duplicate comments during replay, resume, retry,
or repeated approval paths. It should record enough structured evidence to
explain whether a side effect executed, skipped, or failed.

Conceptual `SideEffectLedger` contract:

- look up a record by `side_effect_id`
- report whether prior execution evidence exists
- record an execution attempt result exactly once
- expose safe, non-secret evidence for audit summaries

Conceptual `SideEffectRecord` fields:

- `side_effect_id`
- `skill_run_id`
- `step_id`
- `tool_name`
- `validated_arguments_hash`
- `repository`
- `issue_number`
- status such as executed, skipped, or failed
- provider result reference, if one exists
- failure reason code, if one exists
- audit event references

A3.2 implements isolated `SideEffectLedger`, `SideEffectRecord`,
`InMemorySideEffectLedger`, validated argument hashing, and side-effect id
helpers.

A3.3 wires the in-memory ledger into the one fake-client
`post_github_issue_comment` path. Ledger hits after a prior success skip the
duplicate fake-client call. This is local/demo replay suppression only, not
durable production idempotency.

## 9. GitHub Client Boundary

Future boundary:

```text
GitHubIssueCommentClient
FakeGitHubIssueCommentClient
optional RealGitHubIssueCommentClient
```

The client should only perform:

```text
post_issue_comment(repository, issue_number, comment_body)
```

Tests must use fake or mocked clients only.

The model must not select the client, configure transport, provide headers, or
choose API endpoints. The harness should construct the configured client from
server-side configuration after validation, policy, approval, and idempotency
checks pass.

A3.2 implements `GitHubIssueCommentClient` and
`FakeGitHubIssueCommentClient` only. A3.3 uses the fake client for local/demo
simulated execution. `RealGitHubIssueCommentClient` remains deferred.

## 10. Dry-Run vs Real Behavior

Dry-run mode:

```text
validates, authorizes, approval-gates, audits, but does not call GitHub
```

Fake-client local/demo mode:

```text
validates, authorizes, approval-gates, checks idempotency, calls the fake
GitHub client, records result, audits, and still makes no network call
```

Real mode:

```text
validates, authorizes, approval-gates, checks idempotency, calls configured
GitHub client, records result, audits
```

Default behavior remains dry-run.

A later implementation should keep dry-run evidence clear enough to show that
GitHub was not called.

A3.3 audit evidence explicitly records that real GitHub network calls are
false for the fake-client path.

## 11. Failure Behavior

GitHub client failure must be captured as a structured failure result.

Failure behavior must preserve these rules:

- failure must be audited
- failure must not be retried automatically in a way that can duplicate comments
- failure must not expose secrets
- failure must not convert into success
- ambiguous GitHub outcomes must not be treated as confirmed success
- failed attempts must leave enough audit evidence for a human to inspect the
  state before retrying

## 12. Audit Event Requirements

Minimum future audit evidence:

```text
proposal_received
proposal_validation_passed
proposal_validation_failed
policy_allowed
policy_denied
approval_required
approval_granted
approval_rejected
real_mode_disabled
repository_allowed
repository_denied
side_effect_id_computed
side_effect_ledger_hit
side_effect_ledger_miss
side_effect_executed
side_effect_skipped
side_effect_failed
github_client_called
github_client_not_called
```

Audit evidence should show the boundary decisions without exposing secrets or
raw rejected payloads.

## 13. Non-Goals

A3.1 explicitly excludes:

- live LLM HTTP mode
- MCP
- OAuth/OIDC
- JWT validation
- database-backed full run store
- durable audit store
- frontend
- workflow dispatch
- PR creation
- repo file writes
- multi-agent behavior
- object/list/nested arguments
- partial acceptance
- production deployment
- autonomous real execution
- multiple real tools

A3.3 still excludes implementation of:

- real GitHub API execution
- real GitHub client code
- broad GitHub client runtime wiring beyond the fake-client comment path
- durable side-effect ledger wiring
- durable side-effect ledger
- second GitHub tool
- real-mode configuration

## 14. Acceptance Criteria for Future Implementation

A future implementation of this boundary should not be accepted unless:

- real mode is disabled by default
- real mode requires explicit server-side configuration
- token presence alone cannot enable real mode
- GitHub tokens and client config cannot come from model output
- repository targeting is constrained by server-owned allowlist policy
- `post_github_issue_comment` accepts only registry-declared scalar arguments
- proposed arguments pass deterministic validation before policy or approval
- approval binds to the exact validated action
- deterministic `side_effect_id` is computed before execution
- side-effect ledger check happens before any real GitHub call
- ledger hits skip duplicate real calls
- GitHub client failures produce structured audited failures
- audit evidence records both called and not-called client outcomes
- tests use fake or mocked GitHub clients only
- dry-run behavior remains available and is the default
- existing local/demo Artifact 2.2 scalar argument boundaries remain intact
