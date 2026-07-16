# Historical Agent Factory Memory — Frozen AFDF Records

> **Frozen historical records:** This folder describes the earlier `learn-agentic-ai` Agent Factory program. It is not canonical AFEF framework memory and is not current GitHub Steward repository memory.

The records remain owned by `learn-agentic-ai` for traceability. They were not migrated into the canonical [Agent Factory Engineering Framework](https://github.com/Harry5174/agent-factory-engineering-framework), must not be copied there as framework-owned operational state, and must not be treated as GitHub Steward adoption records. New projects own their own pinned AFEF adoption records. GitHub Steward adoption has not started. See the [legacy transition record](../../LEGACY.md).

---

## Recommended Reading Order

When reproducing or studying historical Agent Factory work, read these files in order:

1. [project-memory.md](project-memory.md) - High-level project state and current phase
2. [phase-map.md](phase-map.md) - The overarching phase structure
3. [artifact-map.md](artifact-map.md) - Status and ownership of each artifact
4. [decision-log.md](decision-log.md) - Settled decisions and their rationale
5. [safety-invariants.md](safety-invariants.md) - Core safety rules and artifact inheritance
6. [evidence-index.md](evidence-index.md) - Index of proven claims and evidence paths
7. [next-artifact-readiness.md](next-artifact-readiness.md) - Readiness for the next vertical artifact
8. [open-decisions.md](open-decisions.md) - Decisions still pending
9. [known-limitations-register.md](known-limitations-register.md) - Current boundaries and constraints

---

## Historical Role Context

The role notes below describe how this memory was used during the AFDF era; they are not current AFEF bootstrap instructions.

### Design Supervisor
- **Reads:** `project-memory.md`, `open-decisions.md`, `next-artifact-readiness.md`
- **Updates:** Resolves open decisions, updates `decision-log.md`, defines next steps.

### Implementation Supervisor
- **Reads:** `decision-log.md`, `safety-invariants.md`, `known-limitations-register.md`
- **Uses it to:** Create safe, well-scoped sprint prompts that don't violate past decisions.

### IDE Agent
- **Reads:** Receives a subset of this memory via the IDE Agent Bootstrap template.
- **Uses it to:** Understand safety invariants, avoid rejected ideas, and respect existing architecture.

### Reviewer / Evaluator
- **Reads:** `evidence-index.md`, `phase-map.md`, `artifact-map.md`
- **Uses it to:** Ensure new completion reports provide sufficient evidence and do not overclaim against existing project state.
