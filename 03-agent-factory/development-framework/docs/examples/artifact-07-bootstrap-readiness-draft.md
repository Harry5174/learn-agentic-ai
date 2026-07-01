# Artifact 07 Bootstrap Readiness Draft

> **Purpose:** Show how AFDF templates will prepare the upcoming Artifact 07 design session. This is a readiness assessment, NOT the Artifact 07 design itself.
>
> **What this document is:** A lightweight draft showing that the framework is ready to bootstrap Artifact 07 design work.
>
> **What this document is NOT:** An Artifact 07 specification, implementation plan, or sprint prompt.

---

## Current Project State

| Fact | Status | Evidence |
|------|--------|----------|
| Phase 02 artifacts (00–06) are complete at sprint level | ✅ | `xx-projects/README.md` artifact index |
| Artifact 06 reached A6.5 (demo packaging) | ✅ | Completion report, git history |
| Artifact 06 publish/tag state | ⚠️ Unverified | Verify before claiming Phase 02 complete |
| AFDF framework scaffold (AFDF.0) | ✅ | `development-framework/` exists |
| AFDF core templates hardened (AFDF.1) | ✅ | Templates with anti-drift, safety, evidence blocks |

---

## AFDF Readiness for Artifact 07

The framework provides:

| Need | AFDF Support | Template |
|------|-------------|----------|
| Design session context | ✅ Design Supervisor Bootstrap | `design-supervisor-bootstrap-template.md` |
| Sprint preparation | ✅ Implementation Supervisor Bootstrap | `implementation-supervisor-bootstrap-template.md` |
| IDE Agent instructions | ✅ IDE Agent Bootstrap | `ide-agent-bootstrap-template.md` |
| Sprint prompts | ✅ Sprint Prompt Template | `sprint-prompt-template.md` |
| Evidence collection | ✅ Completion Report Template | `completion-report-template.md` |
| Gate reviews | ✅ Green Gate Review Template | `green-gate-review-template.md` |
| Session handoff | ✅ Next Session Handoff Template | `next-session-handoff-template.md` |
| Template quality validation | ✅ Quality Checklist | `template-quality-checklist.md` |

---

## Artifact 07 Context (High-Level Only)

### What is known

- Artifact 07 candidate: **GitHub Repo Steward Agent**
- It should be the first vertical agent that uses the full harness safety stack (Artifacts 00–06)
- It should use the reusable runtime and operator approval pattern from Artifact 06
- It may include an LLM service boundary for agent reasoning
- Real GitHub execution should remain optional and release-gated, not default
- Fake/default mode should remain the default for all tests and demos

### What is NOT yet decided

- Exact scope of "GitHub Repo Steward" (issues? PRs? labels? all?)
- LLM provider selection and integration pattern
- Whether Artifact 07 builds a new project folder or extends an existing one
- Sprint breakdown (A7.0, A7.1, etc.)
- Safety boundary extensions specific to vertical agents

### What must happen before Artifact 07 starts

1. Verify Artifact 06 closeout state (publish/tag)
2. Confirm Phase 02 can be considered complete
3. Product Owner approves Artifact 07 scope
4. Design Supervisor session using AFDF bootstrap template

---

## How to Start an Artifact 07 Design Session

1. Copy the [Design Supervisor Bootstrap Template](../templates/design-supervisor-bootstrap-template.md)
2. Fill in the current project state from this document and `docs/status/project-status.md`
3. Set the open decisions:
   - Artifact 07 scope
   - Artifact 07 safety boundaries
   - Sprint plan
4. Set the non-goals:
   - Do not implement Artifact 07 in the design session
   - Do not modify existing artifact runtime
5. Run the repository verification commands
6. Use the filled bootstrap as the opening context for the design session

---

## Safety Considerations for Vertical Agents

Artifact 07 should inherit all safety boundaries from Artifacts 00–06:

- LLM proposes, harness decides, operator approves
- Fake/default first, real mode explicit only
- Approval before side effects
- Server-side token loading, never client-supplied
- Repository allowlisting for real execution
- Evidence required before release claims

Additional vertical-agent safety to consider (not yet designed):

- LLM output validation before harness action
- Agent action scope limits (what the agent is allowed to do)
- Conversation/reasoning boundary (what context the LLM receives)
- Escalation rules (when the agent must stop and defer to operator)

> These are considerations for the Artifact 07 design session, not decisions made here.
