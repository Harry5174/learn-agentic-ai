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

Status: current / implemented.

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

A6.1 does not implement operator approve/reject actions or UI. Inherited
Artifact 04 task/skill approval routes may still exist because the runtime
baseline was copied; those inherited routes are not the Artifact 06 operator
workbench approve/reject surface.

## A6.2 - Approval Action API

Recommended next sprint.

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
