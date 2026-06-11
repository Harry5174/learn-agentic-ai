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
- FastAPI exists in Sprint 7, but graph logic remains outside route handlers.
- Checkpointing exists through `InMemorySaver`, but durable persistence does not.
- No OAuth/JWT.
- No LLM calls.
- No external HTTP calls.
- No real GitHub/workflow execution.

## Sprint 5 Limitation
Sprint 5 paused locally for approval but did not yet provide full checkpointed interrupt/resume semantics.

Sprint 6 later added `InMemorySaver`, `interrupt(...)`, and `Command(resume=...)` handling.
