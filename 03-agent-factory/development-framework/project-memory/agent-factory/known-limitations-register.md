# Known Limitations Register

This register documents current boundaries and constraints of the Agent Factory project and AFDF.

---

## 1. AFDF is Markdown-only
- **Scope:** AFDF
- **Impact:** No automated enforcement of templates or safety checks.
- **Mitigation:** Rely on manual discipline and Reviewer roles.
- **Future Sprint:** Post-Artifact 07 evaluation of AFDF tooling.

## 2. AFDF memory updates are manual
- **Scope:** AFDF
- **Impact:** Memory can drift if a sprint forgets to update it.
- **Mitigation:** Make memory updates a required checklist item in the completion report.
- **Future Sprint:** AFDF.4 (Next-Session Prompt Generation Protocol) may help.

## 3. AFDF has no schema validation
- **Scope:** AFDF
- **Impact:** Templates can be filled out incorrectly.
- **Mitigation:** Use the Template Quality Checklist during gate reviews.
- **Future Sprint:** Unplanned.

## 4. AFDF has no CLI
- **Scope:** AFDF
- **Impact:** Slower to bootstrap sessions.
- **Mitigation:** Copy/paste manually.
- **Future Sprint:** Unplanned.

## 5. Artifact 06 final publish/tag state unverified
- **Scope:** Artifact 06 / Phase 02
- **Impact:** Cannot officially close Phase 02.
- **Mitigation:** Verify state as a prerequisite to starting Artifact 07.
- **Future Sprint:** Pre-Artifact 07 design session.

## 6. Artifact 06 workbench is fake/default
- **Scope:** Artifact 06
- **Impact:** It does not execute live GitHub comments itself.
- **Mitigation:** This is by design (AF-DEC-0005). Real execution belongs to Artifact 04.
- **Future Sprint:** N/A.

## 7. Real-mode GitHub remains limited
- **Scope:** Artifact 04 / Runtime
- **Impact:** Cannot arbitrarily run against any repo.
- **Mitigation:** By design (allowlisted repositories only).
- **Future Sprint:** N/A.

## 8. First vertical agent has not started
- **Scope:** Phase 03
- **Impact:** The Phase 02 runtime provides no end-user value yet.
- **Mitigation:** Start Artifact 07.
- **Future Sprint:** Artifact 07.

## 9. LLM provider abstraction is missing
- **Scope:** Phase 03
- **Impact:** Hard to switch between OpenAI/Anthropic/Google models.
- **Mitigation:** Hardcode or use simple config in the first vertical agent, extract later.
- **Future Sprint:** Post-Artifact 07.
