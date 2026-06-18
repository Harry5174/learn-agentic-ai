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

Artifact 6 will add operator-facing review APIs and, later, a local workbench
on top of an Artifact 4-style runtime.

A6.0 does not copy Artifact 4 runtime code. It only records Artifact 4 as the
baseline and identifies where future operator modules should integrate.

## Boundary

Artifact 6 must not move operator UI/API concerns into Artifact 4 execution
modules such as:

- `src/app/tools/github_comment_real_execution.py`
- `src/app/skill_graph/graph.py`
- `src/app/tools/github_comment_durable_execution.py`
- `src/app/github/real_client.py`

Future operator APIs should stay thin, service-oriented, and test-backed.
