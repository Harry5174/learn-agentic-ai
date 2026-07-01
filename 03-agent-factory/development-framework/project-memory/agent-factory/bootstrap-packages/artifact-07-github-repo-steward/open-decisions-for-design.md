# Open Decisions for Artifact 07 Design

The Design Supervisor must resolve these decisions before Artifact 07 implementation begins.

## 1. Start Timing
**Question:** Whether to start Artifact 07 immediately after AFDF.3?
**Why it matters:** Ensures the framework is fully stable before introducing new artifact complexity.
**Recommended default:** Yes.
**Evidence/source to inspect:** AFDF.3 completion report.
**Decision owner:** Product Owner.
**Blocking status:** Blocking.

## 2. Sprint Map
**Question:** What is the exact Artifact 07 sprint map?
**Why it matters:** Controls scope and prevents sprawling implementations.
**Recommended default:** Break down into A7.1 (scaffold), A7.2 (core logic), etc.
**Evidence/source to inspect:** Project phase map.
**Decision owner:** Design Supervisor.
**Blocking status:** Blocking.

## 3. LLM Mode
**Question:** Whether Artifact 07 uses fake LLM only or optional real provider manual mode?
**Why it matters:** Cost, safety, and deterministic testing.
**Recommended default:** Fake LLM only initially.
**Evidence/source to inspect:** Safety invariants.
**Decision owner:** Product Owner.
**Blocking status:** Blocking.

## 4. LLM Service Boundary
**Question:** Where to place minimal LLM service boundary?
**Why it matters:** Keeps the system provider-neutral and decoupled.
**Recommended default:** A simple abstraction layer separating prompt from execution.
**Evidence/source to inspect:** Artifact 02 architecture.
**Decision owner:** Design Supervisor.
**Blocking status:** Blocking.

## 5. Artifact 06 Relationship
**Question:** Whether Artifact 07 copies Artifact 06 runtime or references it?
**Why it matters:** Code duplication vs. coupling.
**Recommended default:** Copy runtime as a baseline to maintain artifact isolation.
**Evidence/source to inspect:** Phase map and Artifact 06 source.
**Decision owner:** Design Supervisor.
**Blocking status:** Blocking.

## 6. Workbench Integration
**Question:** How Artifact 07 integrates with operator approval workbench?
**Why it matters:** UX for side-effect approval.
**Recommended default:** Use the existing sqlite ledger and console interface.
**Evidence/source to inspect:** Artifact 06 console.
**Decision owner:** Design Supervisor.
**Blocking status:** Blocking.

## 7. Intake Source
**Question:** What issue intake source to use first: local fixture, fake GitHub client, or real read-only GitHub?
**Why it matters:** Testability and safety.
**Recommended default:** Fake GitHub client.
**Evidence/source to inspect:** Safety invariants.
**Decision owner:** Design Supervisor.
**Blocking status:** Blocking.

## 8. Allowed Side Effects
**Question:** What side effects remain allowed in default mode?
**Why it matters:** Prevents accidental destructive actions.
**Recommended default:** Only dry-run logging or local SQLite writes.
**Evidence/source to inspect:** Artifact 04 safety boundary.
**Decision owner:** Product Owner.
**Blocking status:** Blocking.

## 9. Real GitHub Policy
**Question:** Whether real GitHub remains manual/release-gated only?
**Why it matters:** Production safety.
**Recommended default:** Yes.
**Evidence/source to inspect:** Safety invariants.
**Decision owner:** Product Owner.
**Blocking status:** Blocking.

## 10. Evidence Reuse
**Question:** How evidence from Artifact 04/05/06 should be reused?
**Why it matters:** Prevents redundant testing and re-proving known capabilities.
**Recommended default:** Reference existing evidence indexes; do not rebuild.
**Evidence/source to inspect:** Evidence index.
**Decision owner:** Design Supervisor.
**Blocking status:** Blocking.
