# A5.3 Planned Live Flow

This file describes the planned live manual flow. It is not approval to run it.

## Boundary

Do not run this flow unless the Product Owner explicitly says:

```text
Approved to run A5.3 live GitHub smoke against the allowlisted repo/issue.
```

## Existing Adapter Path

The live action must use the existing Artifact 04 approval-gated real adapter
path:

```text
post_github_issue_comment
GitHubRealModeConfig(enabled=True, allowed_repositories=("Harry5174/artifact-5-github-comment-test",), client_mode="real")
EnvironmentGitHubTokenProvider(env_var="AGENT_FACTORY_GITHUB_TOKEN")
DurableSideEffectLedger
DurableApprovalBindingStore
DurableAuditStore
RemoteMarkerLookupService
RealGitHubIssueCommentClient
```

No new GitHub adapter, GitHub operation, issue creation, PR creation, branch
creation, repository file write, workflow dispatch, label, milestone, edit, or
delete operation is in scope.

## Planned Arguments

```text
repository: Harry5174/artifact-5-github-comment-test
issue_number: 1
comment_body: A5.3 controlled live smoke candidate. Prepared 2026-06-18. Unique key: a5.3-controlled-live-smoke-2026-06-18-gate2.
```

## Required Local Order Before Network

```text
1. Validate scalar arguments.
2. Enforce exact repository allowlist.
3. Compute validated_arguments_hash.
4. Compute side_effect_id.
5. Create/check local durable side-effect ledger record.
6. Create/check durable approval binding for the exact side_effect_id + hash.
7. Verify explicit real-mode config.
8. Load token from server-side environment only.
9. List remote issue comments.
10. Check remote idempotency marker.
11. Stop without posting if marker is found, ambiguous, mismatched, incomplete, or lookup fails.
12. Append marker and post exactly one issue comment only when marker is absent.
13. Persist external comment id/url.
14. Record durable audit events.
```

## Live Command Status

No checked-in A5.3 live runner exists. Gate 2 does not add one.

If live execution requires adding a new script, runner, CLI, or runtime code,
stop and obtain explicit approval for that implementation change before adding
it.

## Redacted Evidence To Capture After Approval

```text
Product Owner live approval: [APPROVAL TEXT]
Token present: [TOKEN PRESENT: YES/NO]
Token value: [TOKEN VALUE: REDACTED]
Remote marker searched: [REMOTE MARKER]
Marker status before post: [MARKER STATUS]
External comment id: [COMMENT ID]
External comment URL: [COMMENT URL]
Ledger status before: [LEDGER STATUS]
Ledger status after: [LEDGER STATUS]
Audit event ids: [AUDIT EVENT IDS]
```

