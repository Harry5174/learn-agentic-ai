# Project Status

**Artifact:** 06

**Title:** Operator Approval Console / Workbench

**Current sprint:** A6.1 - Approval Inbox API

**Status:** A6.1 read-only backend API implemented.

## Current Claim

Artifact 06 now has a self-contained runtime baseline copied from Artifact 04
and a read-only operator approval inbox API.

A6.1 implements:

```text
GET /operator/approvals
GET /operator/approvals/{approval_id}
```

A6.1 does not implement approve/reject endpoints, UI, static HTML, Next.js
frontend, live GitHub execution, credential loading, or `.env` access.

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

## A6.1 Limitation

A6.1 uses `run_id` as `approval_id` for local/demo approval inbox rows until a
distinct durable approval identifier is introduced later.

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
A6.2 - Approve / Reject API
```
