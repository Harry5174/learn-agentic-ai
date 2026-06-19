# Project Status

**Artifact:** 06

**Title:** Operator Approval Console / Workbench

**Current sprint:** A6.4 - Status, Ledger, and Audit Visibility

**Status:** A6.4 status, ledger, audit, execution-result, and decision-history
visibility implemented.

## Current Claim

Artifact 06 now has a self-contained runtime baseline copied from Artifact 04,
a read-only operator approval inbox API, explicit backend operator
approve/reject API routes, a minimal local static operator workbench, and
read-only operator visibility for status, audit, side-effect/ledger evidence,
execution results, and decision history.

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

A6.4 does not implement Next.js frontend, live GitHub execution, credential
loading, token loading, or `.env` access.

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

## Files Reviewed Before Implementation

Parent index:

```text
README.md
```

Artifact 04 runtime baseline:

```text
04-approval-gated-real-github-comment-adapter/README.md
04-approval-gated-real-github-comment-adapter/docs/README.md
04-approval-gated-real-github-comment-adapter/docs/specs/artifact-4-real-github-comment-adapter.md
04-approval-gated-real-github-comment-adapter/docs/architecture/architecture.md
04-approval-gated-real-github-comment-adapter/docs/architecture/remote-idempotency-reconciliation.md
04-approval-gated-real-github-comment-adapter/docs/process/development-rules.md
04-approval-gated-real-github-comment-adapter/docs/specs/constitution/mission.md
04-approval-gated-real-github-comment-adapter/docs/specs/constitution/roadmap.md
04-approval-gated-real-github-comment-adapter/docs/specs/constitution/tech-stack.md
04-approval-gated-real-github-comment-adapter/src/app
04-approval-gated-real-github-comment-adapter/tests
```

Artifact 05 evidence/reference context:

```text
05-real-mode-smoke-evidence-release-gate/README.md
05-real-mode-smoke-evidence-release-gate/docs/README.md
05-real-mode-smoke-evidence-release-gate/docs/specs/artifact-5-real-mode-smoke-evidence-release-gate.md
05-real-mode-smoke-evidence-release-gate/docs/status/project-status.md
05-real-mode-smoke-evidence-release-gate/docs/status/roadmap.md
05-real-mode-smoke-evidence-release-gate/docs/status/known-limitations.md
05-real-mode-smoke-evidence-release-gate/docs/evidence/a5.4-final-release-gate-report/README.md
05-real-mode-smoke-evidence-release-gate/docs/evidence/a5.4-final-release-gate-report/artifact-5-release-gate-summary.md
05-real-mode-smoke-evidence-release-gate/docs/evidence/a5.4-final-release-gate-report/portfolio-summary.md
```

## Runtime Baseline

Artifact 04 is the future runtime baseline. Artifact 05 is release-gate
evidence context only.

## Recommended Next Sprint

```text
A6.5 - Demo Packaging and Portfolio Story
```
