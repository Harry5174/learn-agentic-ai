# Artifact 06 - Operator Approval Console / Workbench Spec

## Status

A6.0 completed the architecture baseline and scope freeze.

A6.1 added the first backend operator API surface:

```text
GET /operator/approvals
GET /operator/approvals/{approval_id}
```

A6.2 added explicit backend/API-only operator approve/reject routes:

```text
POST /operator/approvals/{approval_id}/approve
POST /operator/approvals/{approval_id}/reject
```

A6.3 adds a minimal local static workbench served by FastAPI:

```text
GET /operator/workbench
```

A6.4 added read-only status, audit, side-effect/ledger, execution-result, and
decision-history visibility:

```text
GET /operator/approvals/{approval_id}/status
GET /operator/approvals/{approval_id}/audit
GET /operator/side-effects/{side_effect_id}
```

The A6.4 UI calls only:

```text
GET /operator/approvals
GET /operator/approvals/{approval_id}
GET /operator/approvals/{approval_id}/status
GET /operator/approvals/{approval_id}/audit
GET /operator/side-effects/{side_effect_id}
POST /operator/approvals/{approval_id}/approve
POST /operator/approvals/{approval_id}/reject
```

A6.5 packages the local/demo operator workbench demo, portfolio narrative, and
evidence docs. It does not implement Next.js, a package-managed frontend, live
GitHub execution, credentials, token loading, `.env` access, new product
features, or runtime behavior changes.

Inherited Artifact 04 task/skill approval routes still exist because the
runtime baseline was copied. Those inherited routes are not the Artifact 06
operator workbench approve/reject surface. A6.2 operator workbench
approve/reject routes are explicit A6 routes. The A6.3 UI does not call the
inherited routes.

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

- implement operator approve/reject endpoints
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

A6.2 later adds:

- `POST /operator/approvals/{approval_id}/approve`
- `POST /operator/approvals/{approval_id}/reject`

## A6.2 Operator API Boundary

A6.2 uses:

- `src/app/api/operator_routes.py`
- `src/app/api/operator_schemas.py`
- `src/app/operator/approval_actions.py`

A6.2 implements:

- `POST /operator/approvals/{approval_id}/approve`
- `POST /operator/approvals/{approval_id}/reject`

A6.2 request bodies are strict and may include only:

- `decision_reason`
- `expected_side_effect_id`
- `expected_args_hash`

Request bodies cannot claim actor identity, API key id, role, scopes,
operator/admin status, or approval authority. Actor identity is derived from
the server-side API-key resolver.

For Artifact 06 local/demo identity configuration, `OPERATOR_API_KEY` has
`approval:approve` and `approval:reject` scopes. Viewer identity still cannot
approve or reject, and admin identity still has approval decision scopes.

Later A6.x endpoints may add richer durable-console views beyond A6.4:

- distinct durable approval identifiers
- production authorization/session integration
- richer durable audit filtering

## A6.4 Visibility Boundary

A6.4 uses:

- `src/app/operator/status_views.py`
- `src/app/operator/audit_views.py`
- `src/app/operator/side_effect_views.py`
- `src/app/api/operator_routes.py`
- `src/app/api/operator_schemas.py`
- `src/app/operator/static/workbench.html`
- `src/app/operator/static/workbench.css`
- `src/app/operator/static/workbench.js`

A6.4 implements:

- `GET /operator/approvals/{approval_id}/status`
- `GET /operator/approvals/{approval_id}/audit`
- `GET /operator/side-effects/{side_effect_id}`

These endpoints are read-only local/demo projections. They do not resume graph
execution, approve, reject, mutate ledgers, create side effects, write audit
events, call live GitHub, load credentials, or read `.env`.

Visibility responses expose only safe local/demo summaries of status, audit
events, decision history, execution results, and side-effect/ledger evidence
when available. Unknown ids return safe 404 responses. Known side-effect ids
without available ledger records return an explicit local/demo limitation
message rather than inventing a record.

Viewer identities may read visibility through the same local/demo read policy
as A6.1 list/detail. Viewer identities still cannot approve or reject.

A6.4 audit evidence remains local/demo process-state evidence and is not a
production-grade audit log.

## A6.5 Demo Packaging Boundary

A6.5 packages the approved A6.1-A6.4 behavior for local demo and interview use.
The demo story is:

```text
Artifact 06 turns the approval-gated agent harness into a local operator workbench.

A proposed agent action appears in the approval inbox.
The operator inspects the proposed action, risk, scopes, repo/issue context, and execution mode.
The operator approves or rejects through server-controlled routes.
The backend uses server-derived identity, not request-body claims.
After decision, the operator can inspect status, audit timeline, decision history, and side-effect/ledger state.
Everything remains fake/default and local/demo. No GitHub token or live GitHub is required.
```

A6.5 may add documentation, demo runbooks, portfolio notes, evidence summaries,
status updates, roadmap updates, comparison updates, and a narrow parent index
refresh. It must not change `src/app` behavior, approval semantics, static UI
behavior, token handling, `.env` handling, or GitHub execution behavior.

Screenshots are not included by default. Future screenshots should be captured
only after confirming the page contains no secrets, no `.env` values, no
authorization headers, no absolute local filesystem paths, and no unsafe
repository data.

## A6.3 Local Static UI Boundary

A6.3 uses:

- `src/app/operator/static/workbench.html`
- `src/app/operator/static/workbench.css`
- `src/app/operator/static/workbench.js`
- `src/app/api/operator_routes.py`

A6.3 implements:

- `GET /operator/workbench`

The static assets:

- display fake/default local/demo execution mode
- ask the operator to paste a local demo API key for the page session
- send the pasted key only as `X-API-Key`
- avoid browser storage for the key
- render API data through DOM node creation and text assignment
- avoid external scripts, external CDNs, and frontend package tooling
- call only A6 operator API routes

A6.3 does not add OAuth/OIDC, sessions, broad CORS, live GitHub execution, token
loading, `.env` access, Next.js, or inherited Artifact 04 approval-route calls.

A6.4 extends the same static workbench with panels for Current Status, Decision
History, Audit Timeline, Side-Effect / Ledger, Execution Result, and Known
Local/Demo Limitations. It still uses DOM node creation and text assignment for
dynamic content, avoids browser storage, and calls only A6 operator routes.

## Approval Identifier Limitation

A6.1 and A6.2 use `run_id` as `approval_id` for local/demo approval rows until
a distinct durable approval identifier is introduced later.

This is acceptable for the local/demo operator API because the copied skill-run
graph already stores pending approval state by run id.

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

## A6.4 Test Plan

Artifact 06 tests now cover:

- approval list returns summaries
- approval detail returns detail
- unknown approval id returns safe 404
- list/detail are read-only and do not execute tools
- operator approve/reject routes exist and enforce authorization/safety
- query-param identity/role/scope/actor spoofing is ignored
- no token or `.env` is required
- no live GitHub client is called
- fake/default execution mode is visible
- operator responses do not expose token-like values
- workbench route returns static HTML
- workbench displays the local/demo safety notice
- workbench assets reference only A6 operator API routes
- status endpoint returns current status
- audit endpoint returns local/demo audit evidence
- side-effect endpoint returns local/demo ledger evidence when available
- visibility endpoints are read-only and do not mutate approval/run state
- approval followed by status read shows updated status
- rejection followed by audit/status read shows rejection evidence
- workbench includes status, decision-history, audit-timeline,
  side-effect/ledger, execution-result, and local/demo limitation panels
- workbench assets call A6 visibility endpoints
- workbench assets do not reference inherited approval routes
- no Next.js or package-managed frontend files are added
- no external scripts or CDN URLs are used
- no browser storage is used for the pasted local demo key
- dynamic content uses DOM node creation and text assignment patterns

## Block Conditions

Stop if the work requires runtime code copying, runtime refactor, Next.js,
`.env`, credentials, live GitHub, OAuth/OIDC, MCP, deployment, broad CORS, or
broad GitHub automation.
