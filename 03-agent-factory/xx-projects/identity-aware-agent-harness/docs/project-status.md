# Project Status

## Project
**Title:** Identity-Aware Stateful Agent Harness
**Principle:** The LLM proposes. The harness decides.
**Safety Invariant:** Identity is server-derived, policy is deterministic, and high-risk execution cannot happen before approval.

## State
- Sprint 0 approved.
- Sprint 1 implemented and awaiting/ready for architecture review.

## Implemented So Far
**Sprint 0**
- project skeleton
- Pydantic domain schemas
- import smoke tests
- schema validation tests

**Sprint 1**
- identity error type
- demo identity config
- pure API-key identity resolver
- identity resolver tests

## Current Test Status
`uv run pytest`
34 passed

`uv run ruff check .`
All checks passed

## Explicitly Not Implemented Yet
- FastAPI routes
- FastAPI dependencies
- LangGraph graph
- GraphState
- checkpointing
- policy guard logic
- tool registry
- dry-run tool execution
- approval service
- audit persistence
- database
- rate limiting
- LLM calls
- OAuth/OIDC
- JWT validation
- frontend

## Next Recommended Sprint
Sprint 2 / Module 3: Tool Registry and Dry-Run Tool Contracts/Implementation

> **Note:** Do not begin Sprint 2 until Sprint 1 architecture review is approved.
