# Roadmap

## A6.0 - Architecture Baseline, Parent Index Cleanup, and Operator Scope Freeze

Status: current.

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

Recommended next sprint.

Potential scope:

- create operator route/schema modules
- list pending approvals
- get approval detail
- preserve server-derived identity
- enforce viewer/operator/admin boundaries
- keep fake/default execution
- add focused API tests

## A6.2 - Approval Action API

Potential later sprint.

Potential scope:

- approve endpoint
- reject endpoint
- stale id rejection
- `args_hash` and `side_effect_id` mismatch rejection
- durable audit recording
- no token required
- no live GitHub calls in tests

## A6.3 - Minimal Static HTML Workbench

Potential later sprint.

Potential scope:

- simple FastAPI-served static local workbench
- approval list/detail
- approve/reject actions through backend API
- safe comment rendering
- fake/default mode visibility

Next.js remains deferred.
