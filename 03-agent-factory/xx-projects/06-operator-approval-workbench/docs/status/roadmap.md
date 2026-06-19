# Roadmap

## A6.0 - Architecture Baseline, Parent Index Cleanup, and Operator Scope Freeze

Status: complete.

A6.0:

- updates the parent artifact index after Artifact 05
- creates the Artifact 06 scaffold
- records Artifact 04 as runtime baseline
- records Artifact 05 as evidence/release-gate reference only
- inventories Artifact 04 modules and watchlist files
- sketches future operator API boundaries
- records API-first/static-later/Next.js-deferred UI strategy
- documents safety requirements and future tests

No runtime code, operator API, UI, live GitHub, credentials, or `.env` access is
included.

## A6.1 - Approval Inbox API

Status: complete.

A6.1 scope:

- copied tracked Artifact 04 runtime/test baseline into Artifact 06
- created operator route/schema modules
- added read-only approval view service
- lists pending approvals
- gets approval detail
- preserve server-derived identity
- ignores query-param role/scope/identity spoofing
- keep fake/default execution
- adds focused API tests

A6.1 did not implement operator approve/reject actions or UI. Inherited
Artifact 04 task/skill approval routes may still exist because the runtime
baseline was copied; those inherited routes are not the Artifact 06 operator
workbench approve/reject surface.

## A6.2 - Approval Action API

Status: complete.

A6.2 scope:

- approve endpoint
- reject endpoint
- stale id rejection
- `args_hash` and `side_effect_id` mismatch rejection
- local/demo audit and actor evidence
- strict request schemas that cannot claim actor, role, or scopes
- server-derived operator/admin decision scopes
- no token required
- no live GitHub calls in tests

A6.2 is backend/API-only. It does not add UI, static HTML, Next.js, live GitHub
execution, token loading, or `.env` access.

For Artifact 06 local/demo identity configuration, `OPERATOR_API_KEY` has
`approval:approve` and `approval:reject` scopes.

## A6.3 - Minimal Static HTML Workbench

Status: complete.

A6.3 scope:

- simple FastAPI-served static local workbench
- approval list/detail
- approve/reject actions through backend API
- safe dynamic data rendering
- fake/default mode visibility
- local demo API key sent only as `X-API-Key`
- no browser storage
- no external scripts or CDN URLs
- no inherited Artifact 04 approval-route calls

A6.3 does not implement Next.js, OAuth/OIDC, sessions, live GitHub execution,
token loading, `.env` access, or broad CORS. Next.js remains deferred.

## A6.4 - Status, Ledger, and Audit Visibility

Status: complete.

A6.4 scope:

- read-only current status endpoint
- read-only local/demo audit endpoint
- read-only side-effect/ledger visibility endpoint
- workbench panels for Current Status, Decision History, Audit Timeline,
  Side-Effect / Ledger, Execution Result, and Known Local/Demo Limitations
- safe redaction for metadata, decision reasons, execution results, errors,
  and side-effect summaries
- visibility reads that do not mutate run, audit, or ledger state
- continued fake/default local demo boundary
- no live GitHub, token loading, `.env` reading, Next.js, React, or frontend
  build tooling

## A6.5 - Demo Packaging and Portfolio Story

Status: current / implemented.

A6.5 scope:

- package the local/demo operator workbench story
- document the demo flow and safety boundaries
- prepare portfolio-facing narrative and evidence docs
- keep live GitHub and production claims out of the default demo
- avoid screenshots by default unless separately approved and redacted
- preserve runtime behavior, approval semantics, fake/default execution, and
  no-token/no-`.env` local demo operation

## Future Work

Potential future scope:

- distinct durable approval identifiers beyond local/demo `run_id`
- richer durable operator inbox storage
- production authentication and sessions, if approved
- package-managed frontend or Next.js, if approved
- deployment planning, if approved

Future work must keep live GitHub, credentials, `.env`, deployment, OAuth/OIDC,
and broad frontend stack changes behind explicit Product Owner approval.
