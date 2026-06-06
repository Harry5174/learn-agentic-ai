# Project Status

## Project
**Title:** Identity-Aware Stateful Agent Harness
**Principle:** The LLM proposes. The harness decides.
**Safety Invariant:** Identity is server-derived, policy is deterministic, and high-risk execution cannot happen before approval.

## Current Approved/Implemented Sprints
- Sprint 0 approved
- Sprint 1 approved
- Sprint 2 approved
- Sprint 3 implemented
- Sprint 4 implemented
- Sprint 5 implemented and ready for architecture review

## Current Test Status
`uv run pytest`
99 passed

`uv run ruff check .`
All checks passed

## Explicitly Not Implemented Yet
- FastAPI routes
- FastAPI dependencies
- Checkpointing
- Approval resume semantics
- Database persistence
- Rate limiting
- LLM calls
- OAuth/OIDC
- JWT validation
- Frontend

## Next Recommended Sprint
Sprint 6: Checkpointing and Approval Resume Semantics

> **Note:** Do not begin Sprint 6 until Sprint 5 architecture review is approved.

## Sprint 6 Focus
- true checkpointing
- explicit interrupt/resume semantics
- ApprovalDecision injection
- approved execution path
- rejected execution path
- PAUSED_FOR_APPROVAL is suspended, not completed
