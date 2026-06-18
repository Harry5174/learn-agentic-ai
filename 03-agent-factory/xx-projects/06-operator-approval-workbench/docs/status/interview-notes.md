# Interview Notes

Artifact 06 is the next layer in the Agent Factory sequence: an operator review
surface for high-risk actions.

The important A6.0 decision is that the project is not jumping straight into a
frontend or approval endpoint. It first freezes the architecture:

```text
The LLM proposes.
The harness decides.
The human operator approves high-risk actions.
```

Artifact 04 is the runtime baseline because it owns the approval-gated real
GitHub comment adapter, fake-client default path, durable side-effect ledger,
approval binding, audit store, token boundary, and remote marker reconciliation.

Artifact 05 is evidence context only. It proves the release-gate process around
the Artifact 04 path and packages redacted evidence. It is not runtime code for
Artifact 06.

A6.1 starts API-first by adding a read-only approval inbox:

```text
GET /operator/approvals
GET /operator/approvals/{approval_id}
```

The inbox is deliberately read-only. It can list and inspect pending local/demo
approval requests, but it cannot approve, reject, execute tools, call GitHub,
load tokens, or read `.env`.

A6.1 uses `run_id` as `approval_id` for local/demo approval rows until a
distinct durable approval identifier is introduced later.

A static local HTML workbench can come later once the backend contracts are
stable. Next.js is deferred.
