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

## Future Module Boundary

Future operator modules should be separate from existing skill-run routes and
side-effect executors.

Proposed future modules:

- `src/app/api/operator_routes.py`: thin HTTP route layer
- `src/app/api/operator_schemas.py`: request/response contracts
- `src/app/operator/approval_views.py`: read-only inbox/detail views
- `src/app/operator/approval_actions.py`: approve/reject service boundary
- `src/app/operator/audit_views.py`: audit and side-effect evidence views

Do not put operator inbox logic into:

- `src/app/skill_graph/graph.py`
- `src/app/tools/github_comment_durable_execution.py`
- `src/app/tools/github_comment_real_execution.py`
- `src/app/github/real_client.py`

Those modules are already security-sensitive execution/runtime boundaries.

## Future Endpoint Sketch

Future endpoints may include:

- `GET /operator/approvals`
- `GET /operator/approvals/{approval_id}`
- `POST /operator/approvals/{approval_id}/approve`
- `POST /operator/approvals/{approval_id}/reject`
- `GET /operator/approvals/{approval_id}/audit`
- `GET /operator/side-effects/{side_effect_id}`

A6.0 does not implement them.

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

The approval action service must re-read the approval binding and side-effect
record before mutation. It must fail closed on stale ids, mismatched hashes,
terminal states, missing records, or insufficient scopes.

## UI Boundary

The UI is deferred until backend contracts exist.

Future static HTML workbench should be a local/demo review surface only. It
should consume operator API responses, escape comment bodies, show fake/default
mode clearly, and avoid token or secret display.

Next.js remains deferred.
