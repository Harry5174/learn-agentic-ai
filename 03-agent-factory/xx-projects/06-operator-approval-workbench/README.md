# Artifact 06 - Operator Approval Console / Workbench

Artifact 06 will add an operator-facing approval review layer on top of the
approval-gated harness lineage.

A6.0 is an architecture baseline and scope-freeze sprint only. It prepares the
project for later operator API work by recording the runtime baseline,
documenting module boundaries, and freezing what future sprints may and may not
implement.

The core thesis expands to:

```text
The LLM proposes.
The harness decides.
The human operator approves high-risk actions.
```

## Current Status

Current sprint: A6.1 - Approval Inbox API.

A6.1 adds a backend/API-only, read-only operator approval inbox:

```text
GET /operator/approvals
GET /operator/approvals/{approval_id}
```

A6.1 does not implement operator approve/reject actions, UI, static HTML,
Next.js, live GitHub execution, credentials, or `.env` access.

A6.1 added no operator approve/reject routes. The A6.1 operator endpoints are
read-only. Inherited Artifact 04 task/skill approval routes may still exist
because the runtime baseline was copied; those inherited routes are not the
Artifact 06 operator workbench approve/reject surface. A6.2 will add the
operator approve/reject API explicitly.

## Runtime Baseline Decision

Artifact 06 runtime baseline: Artifact 04.

Artifact 04 owns:

- application runtime
- FastAPI service boundaries
- GitHub client boundary
- fake-client default behavior
- real-mode config boundary
- token provider boundary
- durable side-effect ledger
- approval binding
- audit evidence
- remote idempotency marker and reconciliation

Artifact 05 role: release-gate evidence context only.

Artifact 05 proves and packages one controlled manual release-gate path around
Artifact 04. It intentionally has no `src/app` package and must not be copied as
the Artifact 06 runtime baseline.

## A6.1 Runtime Baseline Copy

A6.1 copies the tracked Artifact 04 runtime/test baseline into Artifact 06 so
the operator API can run and test independently:

- `pyproject.toml`
- `uv.lock`
- `.python-version`
- `src/app/`
- `tests/`

A6.1 intentionally does not copy Artifact 04 `.env`, `.env.example`, `.venv`,
cache directories, docs, or README.

The copied runtime preserves fake/default behavior. Real mode remains disabled
unless explicitly configured by trusted server-side code, and the A6.1 operator
inbox does not use real mode.

## A6.0 Deliverables

- parent artifact index cleanup
- Artifact 06 documentation scaffold
- runtime baseline and evidence-role decision
- measurable Artifact 04 module inventory
- future operator API boundary sketch
- API-first UI strategy
- safety requirements and future test plan

## A6.1 Operator API

A6.1 exposes pending approval rows derived from copied skill-run state. In
local/demo A6.1, `run_id` is used as `approval_id` until a distinct durable
approval identifier is introduced later.

The API preserves:

- server-derived identity
- role/scope policy
- approval binding
- `args_hash` and `side_effect_id` consistency
- durable audit evidence
- fake/default execution
- no token required for default local/demo use
- no live GitHub by default

## Future Direction

A6.2 should add approve/reject API behavior. A6.3 should add a minimal static
HTML workbench. Next.js remains deferred.

## Documentation

Use [docs/README.md](docs/README.md) as the documentation index.
