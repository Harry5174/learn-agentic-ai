# Safety and Scope Boundaries for Artifact 07

Before starting Artifact 07, these boundaries must be strictly observed.

## Safety Boundaries
- Artifact 07 must be fake/default first.
- Real GitHub is optional/release-gated, not default.
- No live write in tests.
- No token required for default demo.
- LLM may propose, but must not execute tools directly.
- Harness validates proposals.
- Operator approves side effects.
- Approval, audit, and ledger remain required.

## Scope Boundaries
- No OAuth in initial Artifact 07.
- No frontend/operator console deployment.
- No SaaS tenancy.
- No PR creation, branch creation, labels, milestones, or workflow dispatch in initial Artifact 07.
- Artifact 07 is allowed to explore a minimal provider-neutral LLM service boundary, but full multi-provider routing should be deferred unless explicitly approved.
