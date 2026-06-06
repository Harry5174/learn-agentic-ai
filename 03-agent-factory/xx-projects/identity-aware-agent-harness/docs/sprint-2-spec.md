# Sprint 2: Tool Registry and Dry-Run Tools

## Objective
Implement a controlled tool registry and deterministic dry-run tools so future agent execution cannot call arbitrary functions.

## Scope
- ToolExecutionResult schema
- custom tool registry error
- controlled ToolRegistry
- default V1 registry
- deterministic dry-run tools
- registry tests
- dry-run behavior tests

## Non-Goals
- policy guard
- permission checks
- approval logic
- LangGraph
- FastAPI
- OAuth/OIDC
- JWT validation
- database
- checkpointing
- rate limiting
- LLM calls
- real GitHub calls
- real workflow triggers

## Implemented Files
- `src/app/tools/errors.py`
- `src/app/tools/dry_run_tools.py`
- `src/app/tools/registry.py`
- `src/app/tools/schemas.py`
- `tests/test_dry_run_tools.py`
- `tests/test_tool_registry.py`

## Approved V1 Tools

1. `inspect_sandbox_issues`
   - **Risk:** LOW
   - **Required Scope:** `tools:inspect`
   - **Behavior:** returns predictable sandbox issue data

2. `draft_issue_comment`
   - **Risk:** MEDIUM
   - **Required Scope:** `tools:draft`
   - **Behavior:** returns dry-run comment payload; does not post anything

3. `trigger_workflow_dry_run`
   - **Risk:** HIGH
   - **Required Scope:** `tools:trigger_workflow`
   - **Behavior:** returns simulated workflow trigger payload; does not trigger anything

## Acceptance Criteria Status
- controlled ToolRegistry tests passed
- V1 tools metadata tests passed
- UnknownToolError tests passed
- dry-run execution tests passed

## Important Boundary
The registry does not perform authorization.
Policy belongs to Sprint 3.
