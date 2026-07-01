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
- **Question:** What is the exact sprint breakdown (A7.0, A7.1, etc.) for Artifact 07?
- **Why it matters:** Required to start implementation.
- **Current recommendation:** Unknown; needs Design Supervisor session.
- **Decision owner:** Design Supervisor.
- **Needed evidence:** Approved A7 design spec.
- **Deadline/Trigger:** Artifact 07 design session.

## 3. Artifact 07 LLM Provider Mode
- **Question:** Does Artifact 07 include a real LLM provider in manual mode, or fake LLM only?
- **Why it matters:** Impacts cost, speed, and safety boundaries of A7.
- **Current recommendation:** Start with fake LLM, add real LLM behind an explicit flag.
- **Decision owner:** Design Supervisor.
- **Needed evidence:** A7 design spec.
- **Deadline/Trigger:** Artifact 07 design session.

## 4. Reusable LLM Service Boundary
- **Question:** Where should a reusable LLM service boundary eventually be extracted?
- **Why it matters:** Avoids hardcoding LLM clients into every vertical agent.
- **Current recommendation:** Build it specifically for A7 first, then extract if successful.
- **Decision owner:** Design Supervisor / Product Owner.
- **Needed evidence:** Successful A7 implementation.
- **Deadline/Trigger:** Post-Artifact 07.

## 5. AFDF Tooling Support
- **Question:** When should AFDF be promoted from Markdown-only to tooling-supported (CLI/Schema validation)?
- **Why it matters:** Manual updates are error-prone.
- **Current recommendation:** After Artifact 07 proves the manual workflow works end-to-end.
- **Decision owner:** Product Owner.
- **Needed evidence:** Pain points recorded in Technical Debt register during A7.
- **Deadline/Trigger:** After Artifact 07 completion.
