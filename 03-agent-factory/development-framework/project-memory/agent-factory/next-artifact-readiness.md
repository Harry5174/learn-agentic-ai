# Next Artifact Readiness

This document assesses readiness for the next planned artifact.

---

## Artifact 07 — GitHub Repo Steward Agent

**Status:** Not Started (Candidate for next artifact).

### Why Artifact 07 is next
Phase 02 established a safe, reusable runtime for executing external side effects (like GitHub comments) and an operator workbench for approving them. However, no AI agent currently uses this system. Artifact 07 is the first vertical agent to provide real value by utilizing the Phase 02 runtime.

### What Phase 03 should prove
Phase 03 (starting with A7) should prove that the safe runtime can support useful, autonomous vertical agents without compromising human-in-the-loop control.

### What Artifact 07 should reuse from Artifacts 04–06
- The SQLite durable side-effect ledger.
- The approval binding mechanism.
- The Artifact 04 GitHub comment adapter (for executing its output).
- The Artifact 06 operator workbench (for reviewing its proposals).

### What Artifact 07 should reuse from AFDF
- The entire Design → Implement → Review lifecycle.
- AFDF bootstrap templates to prevent context drift.
- Evidence collection and green gate reviews.

### Recommended Default Mode
**Fake/Default Mode.** All initial implementation, testing, and local demos should use mock tools and mock GitHub responses. Real mode must remain explicit and release-gated.

### Expected LLM Boundary
Artifact 07 will need to talk to an LLM (e.g., to summarize an issue or suggest a label). This should be abstracted behind a service boundary so the agent logic does not hardcode OpenAI or Anthropic specifics. The LLM must NOT be given direct tool execution capabilities.

### Known Non-Goals
- Do not modify the Artifact 04 runtime logic.
- Do not redesign the Artifact 06 workbench.
- Do not build a generic "chat with your repo" feature (keep it focused on stewardship/maintenance).

### Pre-Start Checklist
- [ ] Verify Artifact 06 closeout/publish/tag state.
- [ ] Product Owner approves Artifact 07 scope.
- [ ] Run Design Supervisor session using AFDF bootstrap.

### Blockers Before Starting
- Verification of Artifact 06 state.
