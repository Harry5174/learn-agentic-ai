# Sprint 5: Local LangGraph Harness

## Objective
Implement a local LangGraph workflow connecting identity, deterministic tool selection, policy guard, audit, dry-run execution, and approval pause.

## Scope
- LangGraph dependency
- runtime graph state
- graph nodes
- conditional routing
- deterministic task interpretation
- policy-based routing
- audit integration
- dry-run tool execution for allowed paths
- approval pause state for high-risk paths
- graph tests

## Non-Goals
- FastAPI
- API routes
- API dependencies
- SQLite checkpointing
- database persistence
- rate limiting
- OAuth/OIDC
- JWT validation
- real GitHub calls
- real workflow triggers
- frontend
- LangSmith tracing
- multi-agent behavior
- LLM calls

## Implemented Files
- `src/app/graph/__init__.py`
- `src/app/graph/state.py`
- `src/app/graph/routing.py`
- `src/app/graph/nodes.py`
- `src/app/graph/builder.py`
- `tests/test_graph_allowed_path.py`
- `tests/test_graph_denied_path.py`
- `tests/test_graph_approval_pause.py`
- `tests/test_graph_audit.py`

## Implemented Flow
```text
START
→ interpret_task
→ policy_guard
    ├── ALLOW → execute_tool → generate_report → END
    ├── DENY → finalize_denial → END
    └── REQUIRE_APPROVAL → pause_for_approval → END
```

## Test Scenarios
- allowed path tested (viewer + inspect sandbox issues)
- denied path tested (viewer + draft issue comment)
- approval pause path tested (operator + trigger workflow)
- admin high-risk path tested (admin + trigger workflow)
- unknown task path tested
- audit/boundary tests passed

## Important Deferral
Sprint 5 proves `PAUSED_FOR_APPROVAL` state and non-execution of high-risk tools, but does not yet implement full checkpointed LangGraph interrupt/resume semantics.
That belongs to Sprint 6.
