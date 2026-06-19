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

Future later modules may add:

- `src/app/operator/audit_views.py`: audit and side-effect evidence views

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

A6.2 remains backend/API-only. It adds no UI, static HTML, Next.js frontend,
live GitHub execution, token loading, or `.env` access.

## UI Boundary

The UI is deferred until backend contracts exist.

Future static HTML workbench should be a local/demo review surface only. It
should consume operator API responses, escape comment bodies, show fake/default
mode clearly, and avoid token or secret display.

Next.js remains deferred.
