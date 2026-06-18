# Development Rules

1. Prefer small, reviewable changes.
2. Define contracts before implementation.
3. Keep one sprint at a time.
4. Keep fake/default behavior before real execution.
5. Keep request bodies from claiming identity, role, or scopes.
6. Keep the LLM outside authorization, approval, and execution authority.
7. Require explicit approval before high-risk side effects.
8. Keep routes thin.
9. Do not add UI before backend contracts are stable.
10. Do not add live GitHub behavior without explicit Product Owner approval.

## A6.0 Process Invariant

Every sprint must follow spec-driven and test-driven development. Before
implementation, the IDE/Codex agent must review the relevant specs, status
docs, and constitution/process rules. If the full spec set is too large, the
agent must target the specific relevant specs and state exactly which files
were reviewed. No sprint should proceed from implementation intuition alone.

## A6.0 Escalate Before

Escalate before:

- creating `src/app`
- copying Artifact 04 runtime code
- adding operator API routes
- adding approve/reject endpoints
- adding static HTML
- adopting Next.js
- changing graph flow
- changing approval semantics
- changing token handling
- reading `.env`
- running live GitHub
- adding OAuth/OIDC
- adding MCP
- adding deployment behavior

## A6.0 Stop Rule

Stop if the task requires runtime implementation, frontend implementation,
credentials, `.env`, live GitHub, Next.js, OAuth/OIDC, MCP, deployment, or broad
GitHub automation.
