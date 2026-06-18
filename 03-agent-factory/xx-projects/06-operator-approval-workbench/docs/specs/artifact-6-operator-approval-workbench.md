# Artifact 06 - Operator Approval Console / Workbench Spec

## Status

A6.0 completed the architecture baseline and scope freeze.

A6.1 adds the first backend operator API surface:

```text
GET /operator/approvals
GET /operator/approvals/{approval_id}
```

A6.1 is backend/API-only. It does not implement approve/reject actions, UI,
static HTML, Next.js, live GitHub execution, credentials, or `.env` access.

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

## A6.1 Runtime Copy

A6.1 copies the tracked Artifact 04 runtime/test baseline into Artifact 06:

- `pyproject.toml`
- `uv.lock`
- `.python-version`
- `src/app/`
- `tests/`

A6.1 intentionally does not copy:

- `.env`
- `.env.example`
- `.venv`
- `.pytest_cache`
- `.ruff_cache`
- Artifact 04 docs/README

The copy is used to make Artifact 06 self-contained for API implementation and
tests. A6.1 does not modify Artifact 04 files.

## A6.1 Scope

A6.1 may:

- implement read-only approval list endpoint
- implement read-only approval detail endpoint
- add operator response schemas
- add read-only approval view service
- add tests for read-only inbox/detail behavior
- update docs/status

A6.1 must not:

- implement approve/reject endpoints
- implement UI
- create static HTML
- adopt Next.js
- refactor Artifact 04 runtime files
- run live GitHub
- require credentials
- read `.env`

## A6.1 Operator API Boundary

A6.1 uses:

- `src/app/api/operator_routes.py`
- `src/app/api/operator_schemas.py`
- `src/app/operator/approval_views.py`

A6.1 does not create `approval_actions.py`.

A6.1 implements:

- `GET /operator/approvals`
- `GET /operator/approvals/{approval_id}`

Future A6.2 endpoints may include:

- `POST /operator/approvals/{approval_id}/approve`
- `POST /operator/approvals/{approval_id}/reject`

Future A6.x endpoints may include:

- `GET /operator/approvals/{approval_id}/audit`
- `GET /operator/side-effects/{side_effect_id}`

## A6.1 Approval Identifier Limitation

A6.1 uses `run_id` as `approval_id` for local/demo approval inbox rows until a
distinct durable approval identifier is introduced later.

This is acceptable for the read-only local/demo inbox because the copied
skill-run graph already stores pending approval state by run id. A6.2 should
revisit this when implementing approve/reject behavior.

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

## A6.1 Test Plan

A6.1 tests cover:

- approval list returns summaries
- approval detail returns detail
- unknown approval id returns safe 404
- list/detail are read-only and do not execute tools
- operator approve/reject routes do not exist
- query-param identity/role/scope/actor spoofing is ignored
- no token or `.env` is required
- no live GitHub client is called
- fake/default execution mode is visible
- operator responses do not expose token-like values

## Block Conditions

Stop if the work requires runtime code copying, runtime refactor, API
implementation, UI implementation, Next.js, `.env`, credentials, live GitHub,
OAuth/OIDC, MCP, deployment, or broad GitHub automation.
