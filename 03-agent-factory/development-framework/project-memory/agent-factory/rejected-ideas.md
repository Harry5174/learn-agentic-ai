# Rejected Ideas

This register tracks ideas that were proposed but rejected, along with the reasoning.

---

## 1. Making AFDF Artifact 07
- **Idea:** Treat the framework as a numbered artifact.
- **Why rejected now:** AFDF is cross-cutting process infrastructure, not a runtime artifact. It supports all artifacts.
- **When it may become valid:** Never.
- **Related Phase/Artifact:** Phase 02.5.

## 2. Creating another dedicated smoke-test artifact
- **Idea:** Build another Artifact 05-style smoke test artifact.
- **Why rejected now:** Real-mode evidence exists. We should assume the Artifact 04 runtime works and focus on vertical logic.
- **When it may become valid:** If the runtime architecture changes significantly.
- **Related Phase/Artifact:** Post-Artifact 05.

## 3. Starting with a full LLM gateway before the first vertical agent
- **Idea:** Build a complex, multi-provider LLM abstraction layer before building an agent.
- **Why rejected now:** YAGNI (You Aren't Gonna Need It). We don't know the exact requirements until we build the first vertical agent.
- **When it may become valid:** After Artifact 07 proves the need for provider abstraction.
- **Related Phase/Artifact:** Phase 03.

## 4. Letting LLMs execute tools directly
- **Idea:** Give the LLM direct access to the GitHub API token.
- **Why rejected now:** Violates the core safety principle of the project.
- **When it may become valid:** Never. LLMs propose; harness decides; operator approves.
- **Related Phase/Artifact:** All artifacts.

## 5. Making real GitHub the default for tests
- **Idea:** Run live integration tests against GitHub by default.
- **Why rejected now:** Slows down tests, risks accidental side effects, and risks LLM drift.
- **When it may become valid:** Never. Fake/default first.
- **Related Phase/Artifact:** All artifacts.

## 6. Adding Next.js to Artifact 06
- **Idea:** Use a heavy React framework for the operator workbench.
- **Why rejected now:** Overcomplicates a local/demo tool. Vanilla HTML/JS is sufficient and faster to build with AI.
- **When it may become valid:** If operator workbench is promoted to a production SaaS.
- **Related Phase/Artifact:** Artifact 06.

## 7. Adding OAuth/deployment/multi-user SaaS before vertical agents
- **Idea:** Build production infrastructure now.
- **Why rejected now:** Defocuses from the core goal of proving agent value.
- **When it may become valid:** Phase 04 or later.
- **Related Phase/Artifact:** Phase 03/04.

## 8. Building AFDF CLI/database/automation early
- **Idea:** Build tooling to enforce AFDF templates.
- **Why rejected now:** The process is not yet proven. Building tooling for an unproven process leads to rework.
- **When it may become valid:** After AFDF is proven through the Artifact 07 lifecycle.
- **Related Phase/Artifact:** Phase 02.5.
