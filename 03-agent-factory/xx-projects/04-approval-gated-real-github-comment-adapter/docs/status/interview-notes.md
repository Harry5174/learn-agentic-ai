# Interview Notes

## One-Minute Summary

Artifact 5 - Approval-Gated Real GitHub Comment Adapter is the next step after
the completed Artifact 4 durable side-effect ledger.

Artifact 4 proved local/demo durable fake-client safety: SQLite-backed
side-effect records, durable approval bindings, durable audit events, and
restart/replay duplicate suppression for the fake-client GitHub comment path.

Artifact 5 asks the next safety question:

```text
What has to be true before the harness may safely attempt one real GitHub issue comment?
```

A5.0 answers with a specification, not runtime behavior. It defines the
real-mode boundary, token scope, repository allowlist requirements, remote
idempotency marker, reconciliation behavior, fail-closed ambiguity rules,
durable audit requirements, known limitations, and future sprint roadmap.

## Strong Framing

This is not a GitHub automation product.

It is a staged safety artifact for one future external side effect:

```text
post one GitHub issue comment
```

The model never receives authority to execute that side effect. The harness owns
validation, policy, approval, idempotency, persistence, execution, and audit.

## Why Artifact 4 Matters

Artifact 4 is the right baseline because it already makes the local side of the
side-effect decision durable:

- side-effect records survive process restart
- approval bindings are tied to exact `side_effect_id` and
  `validated_arguments_hash`
- durable audit events explain execution decisions
- replay after durable success suppresses duplicate fake-client execution

That is necessary before a real adapter, but it is not sufficient.

## Why Remote Idempotency Is Needed

SQLite and GitHub cannot commit atomically. A real GitHub comment can succeed
remotely while the process crashes before local SQLite records success.

The required crash window is:

```text
1. GitHub comment POST succeeds.
2. Process crashes before SQLite records succeeded.
3. Service restarts.
4. Local ledger is not succeeded.
5. Replay attempts execution.
6. Without remote marker lookup, duplicate real comment may be posted.
```

Future real mode must therefore search GitHub comments for a harness-generated
marker before posting:

```html
<!-- agent_factory:v1 side_effect_id=<side_effect_id> args_hash=<validated_arguments_hash> -->
```

If the marker exists, the harness does not post again. It reconciles local
durable state and records audit evidence. If marker lookup fails or is
ambiguous, the harness fails closed.

## Token Boundary

A5.0 adds guidance only. It does not load or use a GitHub token.

Future real mode should use a server-side fine-grained token with a short
expiration, one allowlisted test repository, Issues read/write permission, no
Contents permission, no Actions/workflows permission, and no broad repo scope.

Tokens must not come from request bodies, model output, tool arguments, logs,
audit rows, exception messages, or test snapshots.

## Current Non-Implementation Line

A5.0 does not add API behavior changes, real GitHub client code, token loading,
HTTP/network code, real GitHub API calls, runtime remote marker lookup,
OAuth/OIDC, MCP, frontend, deployment, manual live smoke tests, production-ready
claims, or universal exactly-once claims.
