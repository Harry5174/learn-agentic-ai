# Portfolio Story

## Short Version

Artifact 06 turns the approval-gated agent harness into a local operator
workbench.

A proposed agent action appears in the approval inbox. The operator inspects
the proposed action, risk, scopes, repo/issue context, and execution mode. The
operator approves or rejects through server-controlled routes. The backend uses
server-derived identity, not request-body claims. After the decision, the
operator can inspect status, audit timeline, decision history, and
side-effect/ledger state.

Everything remains fake/default and local/demo. No GitHub token, `.env`, or
live GitHub execution is required for Artifact 06.

## Interview Walkthrough

The Agent Factory sequence starts with a simple rule:

```text
The LLM proposes.
The harness decides.
The human operator approves high-risk actions.
```

Artifact 06 focuses on the third line. It gives a human operator a small local
review surface for high-risk actions proposed by the harness lineage.

The important design choice is that the UI is not the authority. The UI only
sends operator intent to explicit A6 routes. Identity and decision authority
come from server-derived identity resolution and scope checks. The request body
cannot declare "I am an admin" or "I have approval authority."

The local workbench is deliberately modest: static HTML, CSS, and JavaScript
served by FastAPI. It avoids frontend package tooling while the backend
contracts are still the focus. It uses DOM node creation and text assignment
for dynamic content, keeps the pasted local demo key in page memory only, and
does not use browser storage.

After a decision, the operator can inspect the evidence trail that matters for
the demo:

- current status
- decision history
- local/demo audit timeline
- side-effect/ledger visibility when available
- execution result summary
- known local/demo limitations

## What To Emphasize

- Operator-facing workbench, not autonomous production execution.
- Approval-gated backend routes, not UI-owned authority.
- Server-derived identity, not request-body identity claims.
- Fake/default execution for Artifact 06 demos.
- Local/demo audit evidence, not a production-grade audit system.
- No GitHub token or `.env` required.
- No live GitHub execution in Artifact 06.

## What Not To Claim

Do not describe Artifact 06 as:

- production-ready
- enterprise-grade
- secure multi-user production software
- deployed
- OAuth/session-authenticated
- a Digital FTE product
- an autonomous production agent
- a live GitHub execution system

## Continuity With Earlier Artifacts

Artifact 04 remains the runtime baseline lineage for approval-gated GitHub
comment behavior, fake/default execution, durable side-effect records, approval
binding, audit, and optional real-mode boundaries.

Artifact 05 remains release-gate evidence context. It proves how one controlled
real-mode smoke path was handled elsewhere. Artifact 06 does not copy Artifact
05 as runtime code and does not add live GitHub behavior.

Artifact 06 adds the operator review layer on top of the copied Artifact 04
runtime baseline.
