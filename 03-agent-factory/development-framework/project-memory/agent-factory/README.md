# Agent Factory Living Memory

This folder is the **living memory instance** for the Agent Factory project. It maintains the project's state, decisions, limitations, safety rules, and evidence index.

---

## Recommended Reading Order

When bootstrapping a new session, read these files in order to build context:

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

## How Roles Use This Memory

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
