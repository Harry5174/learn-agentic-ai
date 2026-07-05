# Open Decisions

This register tracks decisions that need to be made in upcoming sessions.

---

## 1. Artifact 06 Final Closeout
- **Question:** Is Artifact 06 fully published and tagged?
- **Why it matters:** Required to officially close Phase 02.
- **Current recommendation:** Verify git tags and merge state.
- **Decision owner:** Product Owner / Reviewer.
- **Needed evidence:** Output of `git tag` and branch state.
- **Deadline/Trigger:** Before starting Artifact 07 design.

## 2. Artifact 07 Sprint Map
- **Status:** Resolved by Artifact 07 Sprint 7.12 closeout.
- **Resolution:** Artifact 07 closed through Sprint 7.12: design scaffold,
  fixture normalizer, analyzer, fake proposal provider, policy guard, approval
  inbox, operator decisions, local ledger/audit records, dry-run results,
  GitHub-like read adapter, real-read gate, real-write readiness gate, and
  closeout/AFDF framework update.
- **Evidence:** `xx-projects/07-github-repo-steward/docs/evidence/artifact-7.12-closeout-summary.md`.

## 3. Artifact 07 LLM Provider Mode
- **Status:** Resolved for Artifact 07.
- **Resolution:** Artifact 07 is fake/local only and includes no real LLM
  provider, provider SDK, or model-driven proposal integration.
- **Evidence:** `xx-projects/07-github-repo-steward/docs/evidence/artifact-7.12-closeout-summary.md`.

## 4. Reusable LLM Service Boundary
- **Question:** Where should a reusable LLM service boundary eventually be extracted?
- **Why it matters:** Avoids hardcoding LLM clients into every vertical agent.
- **Current recommendation:** Defer until the Product Owner selects a next
  artifact that explicitly includes real LLM provider scope. Artifact 07 did
  not implement real LLM integration.
- **Decision owner:** Design Supervisor / Product Owner.
- **Needed evidence:** Approved next-artifact scope.
- **Deadline/Trigger:** Next artifact selection.

## 5. AFDF Tooling Support
- **Question:** When should AFDF be promoted from Markdown-only to tooling-supported (CLI/Schema validation)?
- **Why it matters:** Manual updates are error-prone.
- **Current recommendation:** Product Owner should decide after reviewing
  Artifact 07 closeout evidence and any pain points from manual AFDF memory
  reconciliation.
- **Decision owner:** Product Owner.
- **Needed evidence:** Artifact 07 closeout evidence and Product Owner
  priorities for the next artifact.
- **Deadline/Trigger:** Next artifact selection.

## 6. Next Artifact Selection
- **Question:** What artifact should follow Artifact 07?
- **Why it matters:** Artifact 07 is closed as a local/fake-first prototype;
  live GitHub reads, real writes, executor runtime, durable persistence, real
  LLM integration, and deployment all require a new explicit authorization
  boundary.
- **Current recommendation:** Next artifact requires Product Owner selection.
- **Decision owner:** Product Owner.
- **Needed evidence:** Product Owner scope decision.
- **Deadline/Trigger:** Before any post-Artifact 07 implementation begins.
