# Artifact 4 vs Artifact 6

## Artifact 4

Artifact 4 is the runtime baseline for Artifact 6.

It demonstrates a local/demo approval-gated real GitHub issue-comment adapter.
The fake client remains the default. Explicit real mode can perform one
repository-allowlisted GitHub issue-comment side effect after validated scalar
arguments, durable approval binding, local durable ledger checks, remote marker
lookup/reconciliation, server-side token loading, and durable audit recording.

Artifact 4 owns:

- runtime code
- FastAPI route patterns
- GitHub client boundary
- fake-client default behavior
- real-mode config
- token provider boundary
- durable ledger
- approval binding
- audit
- side-effect execution

## Artifact 6

Artifact 6 adds operator-facing review APIs and a local static workbench on top
of a copied Artifact 4 runtime baseline.

A6.1 copied the tracked Artifact 4 runtime/test baseline so Artifact 6 can run
and test independently. A6.1 through A6.4 added the operator inbox,
approve/reject routes, static local workbench, and read-only status, audit,
side-effect/ledger, execution-result, and decision-history visibility.

A6.5 packages that local/demo workflow for demo and portfolio use. It does not
change runtime behavior, approval semantics, GitHub execution behavior, token
handling, `.env` handling, or frontend tooling.

## Boundary

Artifact 6 must not move operator UI/API concerns into Artifact 4 execution
modules such as:

- `src/app/tools/github_comment_real_execution.py`
- `src/app/skill_graph/graph.py`
- `src/app/tools/github_comment_durable_execution.py`
- `src/app/github/real_client.py`

Operator APIs should stay thin, service-oriented, and test-backed.

Artifact 6 does not claim live GitHub execution. Its default demo remains
fake/default and local/demo with no GitHub token or `.env` required.
