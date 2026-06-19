# Project Status

**Artifact:** 06

**Title:** Operator Approval Console / Workbench

**Current sprint:** A6.5 - Demo Packaging and Portfolio Story

**Status:** A6.5 local/demo demo package and portfolio story implemented.

## Current Claim

Artifact 06 now has a self-contained runtime baseline copied from Artifact 04,
a read-only operator approval inbox API, explicit backend operator
approve/reject API routes, a minimal local static operator workbench, read-only
operator visibility for status, audit, side-effect/ledger evidence, execution
results, and decision history, plus A6.5 demo and portfolio packaging.

A6.1 implemented:

```text
GET /operator/approvals
GET /operator/approvals/{approval_id}
```

A6.2 implements:

```text
POST /operator/approvals/{approval_id}/approve
POST /operator/approvals/{approval_id}/reject
```

A6.3 implements:

```text
GET /operator/workbench
```

A6.4 implements:

```text
GET /operator/approvals/{approval_id}/status
GET /operator/approvals/{approval_id}/audit
GET /operator/side-effects/{side_effect_id}
```

A6.5 adds documentation and demo evidence only:

```text
docs/demos/operator-workbench-demo.md
docs/demos/portfolio-story.md
docs/evidence/a6.5-operator-workbench-demo/
```

A6.5 makes the local/demo story easier to run and explain:

```text
AI proposes -> operator reviews -> operator approves/rejects -> harness executes safely -> status/audit/ledger evidence is visible
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

A6.5 does not implement Next.js frontend, live GitHub execution, credential
loading, token loading, `.env` access, package-managed frontend files, runtime
behavior changes, approval semantic changes, or new product features.

Inherited Artifact 04 task/skill approval routes still exist because the
runtime baseline was copied. Those inherited routes are not the Artifact 06
operator workbench approve/reject surface. A6.2 operator workbench
approve/reject routes are explicit A6 routes. The A6.4 UI does not call the
inherited routes.

## A6.1 Runtime Copy

A6.1 copied these tracked Artifact 04 baseline items:

```text
pyproject.toml
uv.lock
.python-version
src/app/
tests/
```

A6.1 intentionally did not copy:

```text
.env
.env.example
.venv
.pytest_cache
.ruff_cache
Artifact 04 docs/README
```

## A6.2 Local/Demo Identity

For Artifact 06 local/demo identity configuration, `OPERATOR_API_KEY` has
`approval:approve` and `approval:reject` scopes. Viewer identity still cannot
approve or reject. Admin identity still has approval decision scopes.

## A6.2 Limitation

A6.1 and A6.2 use `run_id` as `approval_id` for local/demo approval rows until
a distinct durable approval identifier is introduced later.

## A6.3 Local/Demo UI Boundary

The A6.3 workbench is static HTML, CSS, and JavaScript served by FastAPI. It
requires the operator to paste a local demo API key for the browser page
session, sends that value only as `X-API-Key`, and does not store it in browser
storage.

The page displays:

```text
Local demo workbench. Fake/default execution only. No live GitHub execution. No GitHub token or .env required.
```

The UI renders dynamic data with DOM node creation and text assignment, uses no
external scripts or CDN URLs, adds no frontend package files, and performs no
live GitHub calls.

## A6.4 Visibility Boundary

A6.4 adds read-only status, audit, side-effect/ledger, execution-result, and
decision-history visibility. The visibility endpoints read local/demo
skill-run state and audit evidence only.

Visibility reads do not approve, reject, resume graph execution, mutate ledger
state, create side effects, write audit events, call live GitHub, load tokens,
or read `.env`.

Viewer identities may read the visibility endpoints under the same local/demo
read policy as the A6.1 inbox. Viewer identities still cannot approve or
reject.

Side-effect visibility exposes available local/demo evidence. Unknown
side-effect ids return safe 404 responses, and known ids without available
ledger records return an explicit local/demo limitation instead of invented
records.

Audit visibility remains local/demo process-state evidence and does not claim
production-grade audit or production readiness.

## A6.5 Demo Package

The A6.5 package explains the end-to-end local operator workflow without
requiring screenshots, secrets, real tokens, `.env`, authorization headers,
absolute local filesystem paths, or live GitHub calls.

The default demo should be described as local/demo, fake/default execution,
operator-facing, approval-gated, server-derived identity, no GitHub token
required, no `.env` required, not deployed, and not production-ready.

## Files Reviewed Before Implementation

Parent index and Artifact 06 package docs:

```text
README.md
06-operator-approval-workbench/README.md
06-operator-approval-workbench/docs/README.md
06-operator-approval-workbench/docs/specs/artifact-6-operator-approval-workbench.md
06-operator-approval-workbench/docs/architecture/operator-workbench-architecture.md
06-operator-approval-workbench/docs/architecture/runtime-baseline-inventory.md
06-operator-approval-workbench/docs/process/development-rules.md
06-operator-approval-workbench/docs/status/project-status.md
06-operator-approval-workbench/docs/status/known-limitations.md
06-operator-approval-workbench/docs/status/roadmap.md
06-operator-approval-workbench/docs/status/interview-notes.md
06-operator-approval-workbench/docs/comparisons/artifact-4-vs-artifact-6.md
06-operator-approval-workbench/docs/comparisons/artifact-5-vs-artifact-6.md
06-operator-approval-workbench/src/app/api/operator_routes.py
06-operator-approval-workbench/src/app/api/operator_schemas.py
06-operator-approval-workbench/src/app/operator/approval_views.py
06-operator-approval-workbench/src/app/operator/approval_actions.py
06-operator-approval-workbench/src/app/operator/status_views.py
06-operator-approval-workbench/src/app/operator/audit_views.py
06-operator-approval-workbench/src/app/operator/side_effect_views.py
06-operator-approval-workbench/src/app/operator/static/workbench.html
06-operator-approval-workbench/src/app/operator/static/workbench.css
06-operator-approval-workbench/src/app/operator/static/workbench.js
06-operator-approval-workbench/tests/test_api_operator_approvals.py
06-operator-approval-workbench/tests/test_operator_workbench_ui.py
06-operator-approval-workbench/tests/test_api_audit.py
06-operator-approval-workbench/tests/test_durable_side_effect_ledger.py
06-operator-approval-workbench/tests/test_side_effect_ledger.py
```

## Runtime Baseline

Artifact 04 is the runtime baseline lineage. Artifact 05 is release-gate
evidence context only.

## Recommended Next Sprint

```text
A6.6 - Distinct Durable Approval Identifiers or Production Auth Planning
```
