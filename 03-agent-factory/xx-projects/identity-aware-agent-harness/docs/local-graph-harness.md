# Local Graph Harness Design

## Purpose
This is the first local stateful harness loop connecting the core components together.

## Current Design
```text
Identity
→ deterministic tool selection
→ policy guard
→ conditional routing
→ audit
→ dry-run execution or denial or approval pause
```

## Runtime State
`HarnessGraphState` is a TypedDict and is separate from Pydantic domain contracts.

## Deterministic Interpreter
Current simple mapping:
- `inspect`/`issue`/`issues` → `inspect_sandbox_issues`
- `draft`/`comment` → `draft_issue_comment`
- `trigger`/`workflow` → `trigger_workflow_dry_run`

## Routing
- `ALLOW` route executes tool
- `DENY` route finalizes denial
- `REQUIRE_APPROVAL` route pauses for approval

## Approval Pause
- `approval_request` is created
- status becomes `PAUSED_FOR_APPROVAL`
- `tool_result` remains `None`
- `TOOL_EXECUTED` audit is absent

## Boundary
- No FastAPI.
- No persistence.
- No OAuth/JWT.
- No LLM calls.
- No external HTTP calls.
- No real GitHub/workflow execution.

## Sprint 6 Carry-Forward
Sprint 6 should focus on checkpointing and true interrupt/resume semantics.
