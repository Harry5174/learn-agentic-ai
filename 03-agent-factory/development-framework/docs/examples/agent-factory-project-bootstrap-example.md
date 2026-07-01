# Agent Factory Project Bootstrap Example

> This is an example of a filled-in Design Supervisor bootstrap for the Agent Factory project. It shows what a real bootstrap looks like when prepared for a new design session.

---

## Project Context

**Project:** Agent Factory — Controlled AI Tool Execution Harness
**Repository:** `https://github.com/Harry5174/learn-agentic-ai`
**Workspace:** `03-agent-factory`

---

## Current Phase

**Phase:** Phase 02 complete or near-complete; Phase 03 next direction: vertical agents
**Phase goal:** Transition from foundational harness artifacts to vertical agent implementations that leverage the harness safety stack.

---

## Current Artifact

**Artifact:** Artifact 07 candidate — GitHub Repo Steward Agent
**Artifact status:** Not yet started. Pending design session.

---

## Current Sprint

**Sprint:** Pre-design / design session
**Sprint goal:** Define the scope, boundaries, and initial sprint plan for Artifact 07.
**Sprint status:** Not started.

---

## Repository Links

| Resource | Path |
|----------|------|
| Agent Factory root | `03-agent-factory/` |
| Artifact sequence | `03-agent-factory/xx-projects/` |
| Development framework | `03-agent-factory/development-framework/` |
| Latest artifact (06) | `03-agent-factory/xx-projects/06-operator-approval-workbench/` |
| Project status | `03-agent-factory/development-framework/docs/status/project-status.md` |

---

## Completed Work

### Artifact 00 — Identity-Aware Stateful Agent Harness
Server-derived identity, role/scope policy, stateful task lifecycle, approval gates, audit trail, LangGraph checkpoint/resume. **Complete / preserved.**

### Artifact 01 — LLM-Proposed, Harness-Controlled Skill Runner
Model-shaped skill proposals, proposal validation, policy and approval lifecycle, safe rejection of unsafe arguments. **Complete / tagged `artifact-2.2`.**

### Artifact 02 — Approval-Gated GitHub Tool Harness
One approval-gated GitHub issue-comment skill path with fake-client execution, validated scalar arguments, trusted repo policy, side-effect idempotency. **Complete as local/demo fake-client artifact.**

### Artifact 03 — Durable Side-Effect Ledger and Approval Binding
SQLite-backed persistence for side-effect records, approval bindings, audit events. Restart/replay duplicate suppression. **Complete as local/demo durable fake-client safety artifact.**

### Artifact 04 — Approval-Gated Real GitHub Comment Adapter
Real GitHub issue-comment adapter with repository allowlisting, server-side token loading, remote idempotency marker lookup/reconciliation, durable audit recording. Fake client remains default. **Complete as local/demo real-comment adapter (A4.5).**

### Artifact 05 — Real-Mode Smoke Evidence and Release Gate
Release-gate evidence layer. Preserves fake-client default. One controlled live smoke result with redacted evidence. Offline replay/no-duplicate and negative zero-network proof. **Complete / published / tagged evidence artifact.**

### Artifact 06 — Operator Approval Console / Workbench
Local operator workbench. Proposed actions appear in approval inbox. Operator inspects risk/scopes/context/execution mode, approves or rejects through server-controlled routes, inspects status and audit timeline. **Current local/demo workbench artifact (A6.5).**

> **Note:** Artifact 06 is complete at sprint level if A6.5 was approved; verify publish/tag state before claiming final closeout.

---

## Approved Decisions

| Decision | Date | Reference |
|----------|------|-----------|
| Fake-client is always default; real mode is opt-in | Artifact 02 | Safety boundary protocol |
| LLM proposes, harness decides, operator approves | Artifact 00 | Architecture principle |
| Server-derived identity, never client-claimed | Artifact 00 | Identity invariant |
| SQLite-backed durability for side-effect records | Artifact 03 | Durable state spec |
| Repository allowlisting for real GitHub execution | Artifact 04 | Real adapter spec |
| Development framework lives outside xx-projects | AFDF.0 | Framework location decision |

---

## Open Decisions

| Decision Needed | Context | Options |
|-----------------|---------|---------|
| Artifact 07 scope | What should the first vertical agent do? | GitHub Repo Steward (issues, PRs, labels) vs. narrower scope |
| Artifact 07 safety boundaries | What additional safety rules does a vertical agent need? | Inherit all prior + define agent-specific limits |
| Artifact 06 final closeout | Is A6.5 fully published/tagged? | Verify before claiming Phase 02 complete |

---

## Non-Goals

- Do not implement Artifact 07 in this session
- Do not modify any existing artifact runtime
- Do not add OAuth, deployment, or production infrastructure
- Do not add MCP integration

---

## Safety Invariants

- LLM proposes, harness decides, operator approves
- Fake/default first, real mode explicit only
- Do not print or expose secrets
- Approval before side effects
- CI must not run live side effects

---

## Files to Review

- `03-agent-factory/xx-projects/README.md` — current artifact index
- `03-agent-factory/development-framework/README.md` — AFDF overview
- `03-agent-factory/development-framework/docs/protocols/safety-boundary-protocol.md` — safety rules
- `03-agent-factory/xx-projects/06-operator-approval-workbench/README.md` — latest artifact state

---

## Questions to Answer

1. What is the scope of Artifact 07?
2. What safety boundaries does a vertical agent need beyond the inherited stack?
3. Is Artifact 06 fully closed out (published/tagged)?
4. What is the first sprint (A7.0) deliverable?

---

## Expected Output

- [ ] Artifact 07 scope definition
- [ ] Artifact 07 safety boundary definition
- [ ] Artifact 07 sprint plan (A7.0 through A7.N)
- [ ] Updated project memory with Artifact 07 design decisions
