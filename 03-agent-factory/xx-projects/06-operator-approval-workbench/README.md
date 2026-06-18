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

Current sprint: A6.0 - Architecture Baseline, Parent Index Cleanup, and
Operator Scope Freeze.

A6.0 does not implement runtime behavior, API routes, approve/reject endpoints,
UI, static HTML, Next.js, live GitHub execution, credentials, or `.env` access.

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

## A6.0 Deliverables

- parent artifact index cleanup
- Artifact 06 documentation scaffold
- runtime baseline and evidence-role decision
- measurable Artifact 04 module inventory
- future operator API boundary sketch
- API-first UI strategy
- safety requirements and future test plan

## Future Direction

A6.1 should implement an Approval Inbox API only after the A6.0 boundaries are
accepted. Future implementation must preserve:

- server-derived identity
- role/scope policy
- approval binding
- `args_hash` and `side_effect_id` consistency
- durable audit evidence
- fake/default execution
- no token required for default local/demo use
- no live GitHub by default

## Documentation

Use [docs/README.md](docs/README.md) as the documentation index.
