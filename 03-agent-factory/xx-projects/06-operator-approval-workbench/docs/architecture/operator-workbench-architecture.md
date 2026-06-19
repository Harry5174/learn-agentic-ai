# Operator Workbench Architecture

## Purpose

This page freezes the A6.0 boundary for the future Operator Approval Console /
Workbench.

A6.0 does not implement the workbench. It defines where future operator
contracts should live and where they must not leak.

## Baseline Stack

Future Artifact 06 runtime work should start from Artifact 04, not Artifact 05.

Artifact 04 already contains the runtime layers that an operator review surface
will need:

```text
FastAPI routes
-> server-derived identity
-> proposal validation
-> deterministic policy
-> approval pause/resume
-> durable approval binding
-> durable side-effect ledger
-> fake/default execution
-> optional explicit real-mode boundary
-> durable audit
```

Artifact 05 is evidence context only. It proves and packages the release-gate
shape around Artifact 04.

## A6.1 Module Boundary

A6.1 operator modules are separate from existing skill-run routes and
side-effect executors.

A6.1 modules:

- `src/app/api/operator_routes.py`: thin HTTP route layer
- `src/app/api/operator_schemas.py`: request/response contracts
- `src/app/operator/approval_views.py`: read-only inbox/detail views

A6.2 adds:

- `src/app/operator/approval_actions.py`: approve/reject service boundary

A6.3 adds:

- `src/app/operator/static/workbench.html`: local static workbench shell
- `src/app/operator/static/workbench.css`: local static workbench styling
- `src/app/operator/static/workbench.js`: local static workbench behavior

A6.4 adds:

- `src/app/operator/status_views.py`: read-only approval/run status views
- `src/app/operator/audit_views.py`: read-only local/demo audit views
- `src/app/operator/side_effect_views.py`: read-only side-effect/ledger evidence views

Do not put operator inbox logic into:

- `src/app/skill_graph/graph.py`
- `src/app/tools/github_comment_durable_execution.py`
- `src/app/tools/github_comment_real_execution.py`
- `src/app/github/real_client.py`

Those modules are already security-sensitive execution/runtime boundaries.

## A6.1 Endpoints

A6.1 implements:

- `GET /operator/approvals`
- `GET /operator/approvals/{approval_id}`

A6.1 does not implement:

- `POST /operator/approvals/{approval_id}/approve`
- `POST /operator/approvals/{approval_id}/reject`
- `GET /operator/approvals/{approval_id}/audit`
- `GET /operator/side-effects/{side_effect_id}`

## A6.2 Endpoints

A6.2 implements explicit operator workbench decision routes:

- `POST /operator/approvals/{approval_id}/approve`
- `POST /operator/approvals/{approval_id}/reject`

These routes are separate from inherited Artifact 04 routes:

- `POST /skill-runs/{run_id}/approve`
- `POST /skill-runs/{run_id}/reject`
- `POST /tasks/{task_id}/approve`
- `POST /tasks/{task_id}/reject`

The inherited routes still exist in the copied runtime. They are not the A6
operator workbench route surface.

## A6.3 Workbench Route

A6.3 implements:

- `GET /operator/workbench`

The workbench uses narrow local asset responses under the existing operator
router and does not add broad CORS or a frontend build stack. The UI calls only:

- `GET /operator/approvals`
- `GET /operator/approvals/{approval_id}`
- `POST /operator/approvals/{approval_id}/approve`
- `POST /operator/approvals/{approval_id}/reject`

The UI does not call inherited Artifact 04 task or skill approval routes.

## A6.4 Visibility Endpoints

A6.4 implements read-only visibility routes:

- `GET /operator/approvals/{approval_id}/status`
- `GET /operator/approvals/{approval_id}/audit`
- `GET /operator/side-effects/{side_effect_id}`

These routes are thin HTTP projections over operator visibility service
modules. They read already-known local/demo skill-run state and audit evidence.
They do not resume the graph, approve, reject, mutate ledgers, create
side-effects, write audit events, call GitHub, load tokens, or read `.env`.

Viewer identities may read these visibility routes through the same local/demo
read policy as the A6.1 inbox. Operator/admin decision authority remains
restricted to the A6.2 approve/reject routes.

Side-effect visibility is fail-safe. Unknown side-effect ids return 404. Known
side-effect ids without available local ledger records return an explicit
local/demo limitation instead of inventing records.

## A6.1 Read-Only Data Source

A6.1 derives pending approval rows from copied `SkillGraphService` state. It
adds a read-only `list_runs()` helper and builds approval views only from runs
paused for approval.

A6.1 uses `run_id` as `approval_id` for local/demo approval inbox rows until a
distinct durable approval identifier is introduced later.

List/detail views do not resume the graph, approve, reject, execute tools, call
GitHub, mutate ledgers, require token access, or read `.env`.

A6.2 approve/reject actions still use `run_id` as `approval_id` for local/demo
decisions. The action service re-reads the pending run, checks optional expected
`side_effect_id` and `args_hash` values before mutation, enforces server-derived
`approval:approve` or `approval:reject` scopes, and only then reuses the copied
`SkillGraphService` approval/rejection behavior.

For Artifact 06 local/demo identity configuration, `OPERATOR_API_KEY` has
`approval:approve` and `approval:reject` scopes. This is demo configuration,
not a production authorization model.

## Authority Boundary

The future operator API must derive identity from the server-owned identity
resolver. Request bodies may include operator intent such as a rejection reason,
but must not claim:

- user id
- role
- scopes
- approval actor
- allowlist
- token
- real-mode enablement
- trusted `side_effect_id` or `args_hash` authority

A6.2 approval action service must re-read the approval binding and side-effect
record before mutation. It must fail closed on stale ids, mismatched hashes,
terminal states, missing records, or insufficient scopes.

A6.2 remains backend/API-only. A6.3 adds only the local static workbench; it
adds no Next.js frontend, live GitHub execution, token loading, or `.env`
access.

## UI Boundary

A6.3 is a local/demo review surface only. It consumes operator API responses,
renders API-provided content with DOM node creation and text assignment, shows
fake/default mode clearly, and avoids token or secret display.

The pasted local demo API key is held only in page memory and sent only as the
`X-API-Key` request header. The static assets do not store it in browser
storage and do not embed any demo key values.

Next.js remains deferred.

## A6.4 UI Visibility Boundary

A6.4 extends the static workbench with panels for Current Status, Decision
History, Audit Timeline, Side-Effect / Ledger, Execution Result, and Known
Local/Demo Limitations.

The UI calls only A6 operator routes:

- `GET /operator/approvals`
- `GET /operator/approvals/{approval_id}`
- `GET /operator/approvals/{approval_id}/status`
- `GET /operator/approvals/{approval_id}/audit`
- `GET /operator/side-effects/{side_effect_id}`
- `POST /operator/approvals/{approval_id}/approve`
- `POST /operator/approvals/{approval_id}/reject`

It still uses DOM node creation and text assignment for dynamic content. It
does not add external scripts, browser storage, Next.js, React, package files,
frontend build tooling, live GitHub calls, token loading, or `.env` access.

A6.4 audit visibility remains local/demo process-state evidence. It is not a
production-grade audit system.

## A6.5 Packaging Layer

A6.5 is a documentation and demo-evidence layer on top of the existing A6.1
through A6.4 runtime surface. It does not introduce a new execution path or a
new frontend stack.

The packaged local/demo workflow is:

```text
operator inbox
-> approval detail
-> approve/reject
-> status refresh
-> audit timeline
-> decision history
-> side-effect/ledger visibility
-> execution result visibility
```

The architecture boundary remains unchanged:

- operator authority is derived from server-side identity resolution
- request bodies cannot claim actor identity, role, scopes, repository policy,
  real-mode enablement, tokens, `args_hash`, or `side_effect_id` authority
- the static workbench calls only A6 operator routes
- local/demo audit evidence remains process-state evidence
- Artifact 06 does not require a GitHub token or `.env`
- Artifact 06 does not perform live GitHub execution

Screenshots are intentionally absent from the default A6.5 package. If future
demo screenshots are approved, capture only redacted local/demo views with no
token values, authorization headers, `.env` values, absolute local filesystem
paths, or unsafe repository data.
