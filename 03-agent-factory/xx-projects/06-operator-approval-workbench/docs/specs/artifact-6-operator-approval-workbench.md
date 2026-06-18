# Artifact 06 - Operator Approval Console / Workbench Spec

## Status

A6.0 is a cleanup/design-boundary sprint.

It is not a frontend sprint, not an operator API implementation sprint, not a
new product feature sprint, and not a runtime refactor sprint.

## Sprint Goal

A6.0 prepares the project for Artifact 06 by:

1. Fixing parent README/index consistency after Artifact 05.
2. Creating the Artifact 06 scaffold.
3. Recording the runtime baseline decision: Artifact 04 runtime, Artifact 05
   evidence/reference layer.
4. Producing an architecture/module-boundary inventory and freezing future
   operator API/UI scope before implementation.

## Thesis

```text
The LLM proposes.
The harness decides.
The human operator approves high-risk actions.
```

The model must never directly execute tools, authorize side effects, provide
credentials, enable real mode, widen allowlists, approve work, or decide
operator authority.

## Runtime Baseline Decision

Artifact 06 runtime baseline: Artifact 04.

Artifact 04 owns the runtime harness:

- app code
- FastAPI boundaries
- GitHub client boundary
- fake-client default
- real-mode config
- token provider
- durable ledger
- approval binding
- audit
- side effects
- remote marker reconciliation

Artifact 05 role: evidence/release-gate reference only.

Artifact 05 owns:

- manual release-gate evidence
- redacted evidence packaging
- offline preflight proof
- final release-gate reports
- live-smoke safety documentation

Artifact 05 intentionally has no `src/app` package and must not be copied as
the runtime baseline.

## A6.0 Scope

A6.0 may:

- create docs/scaffold
- update the parent artifact index
- document the runtime baseline
- document the Artifact 05 evidence role
- inventory Artifact 04 modules and watchlist files
- sketch future operator API boundaries
- document UI strategy
- document safety requirements
- document future test plan

A6.0 must not:

- create `src/app`
- copy Artifact 04 runtime code
- implement operator API routes
- implement approve/reject endpoints
- implement UI
- create static HTML
- adopt Next.js
- refactor Artifact 04 runtime files
- run live GitHub
- require credentials
- read `.env`

## Future Operator API Boundary

Future A6.1 module names may include:

- `src/app/api/operator_routes.py`
- `src/app/api/operator_schemas.py`
- `src/app/operator/approval_views.py`
- `src/app/operator/approval_actions.py`
- `src/app/operator/audit_views.py`

These are proposals only in A6.0. A6.1 must decide and implement the actual
names.

Future endpoints may include:

- `GET /operator/approvals`
- `GET /operator/approvals/{approval_id}`
- `POST /operator/approvals/{approval_id}/approve`
- `POST /operator/approvals/{approval_id}/reject`
- `GET /operator/approvals/{approval_id}/audit`
- `GET /operator/side-effects/{side_effect_id}`

A6.0 does not implement these endpoints.

## Future Operator API Invariants

Future endpoints must preserve:

- server-derived identity
- role/scope policy
- approval binding
- `args_hash` consistency
- `side_effect_id` consistency
- durable audit events
- fake/default execution
- no token required for default local/demo use
- no live GitHub by default

Approval/rejection request bodies must not claim identity, role, scopes,
approval authority, repository allowlists, real-mode enablement, token values,
`args_hash`, or `side_effect_id` authority.

## UI Strategy

- A6.0: no UI implementation
- A6.1-A6.2: backend/operator API first
- A6.3: minimal static HTML workbench served by FastAPI
- Next.js: deferred

Next.js is deferred because backend operator contracts are not stable yet,
OAuth/session questions are premature, frontend stack work would distract from
approval safety, and a static local UI is enough for demo review.

## Safety Requirements

Future A6 implementation must preserve these requirements:

- UI must escape/render comment bodies safely.
- UI must not display secrets or token-like values.
- Approval action must use server-derived identity.
- Approval/rejection request body cannot claim role or scopes.
- Viewer can view only if allowed, but cannot approve.
- Every approve/reject action must record actor identity.
- Approving stale/mismatched `side_effect_id` or `args_hash` must fail.
- UI must show fake/default execution mode clearly.
- No token required for UI demo.
- No real GitHub call in tests.

## Future Test Plan

Future A6 tests should include:

- viewer cannot approve
- request body cannot claim role/scopes
- operator/admin approval records actor
- stale approval id rejected
- `args_hash` mismatch rejected
- `side_effect_id` mismatch rejected
- rejection records audit
- approved fake execution updates status
- comment body safely rendered/escaped in UI
- no token required for UI demo
- no real GitHub call in tests

## Block Conditions

Stop if the work requires runtime code copying, runtime refactor, API
implementation, UI implementation, Next.js, `.env`, credentials, live GitHub,
OAuth/OIDC, MCP, deployment, or broad GitHub automation.
