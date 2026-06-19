# Interview Notes

Artifact 06 is the next layer in the Agent Factory sequence: an operator review
surface for high-risk actions.

The important A6.0 decision is that the project is not jumping straight into a
frontend or approval endpoint. It first freezes the architecture:

```text
The LLM proposes.
The harness decides.
The human operator approves high-risk actions.
```

Artifact 04 is the runtime baseline because it owns the approval-gated real
GitHub comment adapter, fake-client default path, durable side-effect ledger,
approval binding, audit store, token boundary, and remote marker reconciliation.

Artifact 05 is evidence context only. It proves the release-gate process around
the Artifact 04 path and packages redacted evidence. It is not runtime code for
Artifact 06.

A6.1 starts API-first by adding a read-only approval inbox:

```text
GET /operator/approvals
GET /operator/approvals/{approval_id}
```

The inbox is deliberately read-only. It can list and inspect pending local/demo
approval requests, but the A6.1 operator endpoints cannot approve, reject,
execute tools, call GitHub, load tokens, or read `.env`.

A6.2 adds explicit backend/API-only operator decision routes:

```text
POST /operator/approvals/{approval_id}/approve
POST /operator/approvals/{approval_id}/reject
```

These routes use server-derived identity, strict request bodies, and
scope-based decision checks before reusing the inherited fake/default
approval-resume behavior. The request body cannot claim actor identity, role,
or scopes. Rejection requires a decision reason. Optional expected
`side_effect_id` and `args_hash` values fail safely if stale, mismatched, or
unavailable.

Inherited Artifact 04 task/skill approval routes may still exist because the
runtime baseline was copied. Those inherited routes are not the Artifact 06
operator workbench approve/reject surface.

A6.1 and A6.2 use `run_id` as `approval_id` for local/demo approval rows until
a distinct durable approval identifier is introduced later.

For Artifact 06 local/demo identity configuration, `OPERATOR_API_KEY` has
`approval:approve` and `approval:reject` scopes. Viewer identity still cannot
approve or reject.

A6.3 adds a minimal static local workbench:

```text
GET /operator/workbench
```

The page lists approvals, loads approval detail, and sends approve/reject
decisions only through the A6 operator routes. It does not call inherited
Artifact 04 approval routes.

The A6.3 workbench is deliberately local/demo only. It displays fake/default
mode and this boundary:

```text
Local demo workbench. Fake/default execution only. No live GitHub execution. No GitHub token or .env required.
```

The operator pastes a local demo API key for the browser page session. The UI
sends that value only as `X-API-Key`, does not store it in browser storage, and
does not embed key values in the static assets. Dynamic response content is
rendered with DOM node creation and text assignment instead of HTML injection.

Next.js, OAuth/OIDC, sessions, broad CORS, live GitHub execution, token
loading, and `.env` access remain out of scope.
