# Artifact Map

This map outlines the status and ownership boundaries of all Agent Factory artifacts.

---

## Artifact 00 — Foundation / Local Harness
- **Purpose:** Initial stateful agent loop.
- **Status:** Complete / preserved.
- **Owned Responsibility:** Basic graph execution.
- **Not Owned Responsibility:** External side effects or approvals.
- **Known Caveat:** Superseded by later artifact patterns.

## Artifacts 01–03 — Identity, Policy, Approval, Fake Side-Effect Safety
- **Purpose:** Establish the safety primitives.
- **Status:** Complete.
- **Owned Responsibility:** SQLite ledger, approval schema, fake/mock tool execution.
- **Not Owned Responsibility:** Live execution.
- **Known Caveat:** Used primarily as local/demo artifacts.

## Artifact 04 — Approval-Gated Real GitHub Comment Adapter
- **Purpose:** Build the runtime for live GitHub comments.
- **Status:** Complete as local/demo real-comment adapter (A4.5).
- **Owned Responsibility:** Owns the runtime real-mode GitHub path, server-side token loading, repository allowlisting, and idempotency markers.
- **Not Owned Responsibility:** Does not own the release-gate evidence collection.
- **Key Evidence Path:** `xx-projects/04-approval-gated-real-github-comment-adapter/evidence/`

## Artifact 05 — Real-Mode Smoke Evidence and Release Gate
- **Purpose:** Prove Artifact 04 works in reality.
- **Status:** Complete / published / tagged evidence artifact.
- **Owned Responsibility:** Owns release-gate evidence.
- **Not Owned Responsibility:** Does not add runtime behavior.
- **Key Evidence Path:** `xx-projects/05-real-mode-smoke-evidence-release-gate/evidence/`

## Artifact 06 — Operator Approval Console / Workbench
- **Purpose:** Provide a UI for operators to review and approve side effects.
- **Status:** Complete at sprint level (A6.5) — verify publish/tag state before final closeout.
- **Owned Responsibility:** Owns the local/demo operator workbench UI and API. Defaults to fake/default execution.
- **Not Owned Responsibility:** Does not own real GitHub execution logic.
- **Key Evidence Path:** `xx-projects/06-operator-approval-workbench/evidence/`

## AFDF (Phase 02.5)
- **AFDF.0:** Framework scaffold and operating model (Complete).
- **AFDF.1:** Core bootstrap templates hardening (Complete).
- **AFDF.2:** Project memory, decision log, and evidence protocols (Complete).
- **Owned Responsibility:** Owns development workflow memory/templates/protocols.
- **Not Owned Responsibility:** Does not run agents, does not execute tools, does not modify artifact runtime code.

## Artifact 07 — GitHub Repo Steward Agent
- **Purpose:** Model a local/fake-first repository stewardship pipeline with explicit evidence gates.
- **Status:** Closed as a local/fake-first GitHub Repo Steward prototype.
- **Owned Responsibility:** Canonical local fixture intake, normalization, deterministic findings, fake proposals, policy guard, approval inbox, local operator decisions, local audit records, dry-run results, GitHub-like read adapter boundary, real-read evidence gate, and real-write readiness gate.
- **Not Owned Responsibility:** Live GitHub reads, real GitHub writes, GitHub authentication, real executor runtime, real LLM integration, durable persistence, deployment, production readiness, or next-artifact selection.
- **Key Evidence Path:** `xx-projects/07-github-repo-steward/docs/evidence/`
