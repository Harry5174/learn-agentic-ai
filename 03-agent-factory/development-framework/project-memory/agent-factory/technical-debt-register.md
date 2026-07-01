# Technical Debt Register

This register tracks cleanup, refactoring, and improvements that are known but deferred.

---

## 1. Artifact 06 Closeout Verification
- **Location:** Project status / git tags
- **Risk:** Low, but prevents formal closure of Phase 02.
- **Urgency:** Medium.
- **Owner:** Product Owner / Reviewer.
- **Recommended Cleanup:** Verify `git tag` and branch state, update status docs.

## 2. AFDF Memory Update Discipline
- **Location:** AFDF Workflow
- **Risk:** High. If memory is not updated after every sprint, AFDF loses its value.
- **Urgency:** High (ongoing).
- **Owner:** Implementation Supervisor / Reviewer.
- **Recommended Cleanup:** Enforce memory updates at every green gate review.

## 3. Evidence Index Normalization
- **Location:** Artifacts 00–06 `evidence/` directories
- **Risk:** Low. Evidence formats vary across early artifacts.
- **Urgency:** Low.
- **Owner:** IDE Agent.
- **Recommended Cleanup:** Standardize evidence package formats eventually, but prioritize new work first.

## 4. Schema Validation for Completion Reports
- **Location:** AFDF Templates
- **Risk:** Medium. Humans might miss overclaims or missing evidence.
- **Urgency:** Low.
- **Owner:** Design Supervisor.
- **Recommended Cleanup:** Introduce a lightweight JSON schema or linter script in the future.

## 5. Automation for Next-Session Handoffs
- **Location:** AFDF Workflow
- **Risk:** Low. Manual assembly takes time.
- **Urgency:** Low.
- **Owner:** Design Supervisor.
- **Recommended Cleanup:** Build a prompt-generation script (planned for AFDF.4).

## 6. LLM Provider Abstraction
- **Location:** Future Artifact 07
- **Risk:** Medium. Hardcoding LLM clients creates vendor lock-in.
- **Urgency:** Low (wait until proven needed).
- **Owner:** IDE Agent.
- **Recommended Cleanup:** Extract a provider-neutral interface after Artifact 07 proves the concept.
