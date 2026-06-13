# Sprint 6: Checkpointed Approval Resume Flow

## Objective

Make high-risk approval pauses resumable through LangGraph checkpointing while preserving the safety invariant.

## Scope

- LangGraph `InMemorySaver` checkpointer.
- Required `thread_id` config for task checkpoints.
- Approval interrupt/resume semantics.
- `Command(resume=...)` injection.
- Approved high-risk resume path.
- Rejected high-risk resume path.
- Invalid approval actor handling.
- `HarnessGraphService` wrapper for starting, fetching, approving, rejecting, and auditing tasks.

## Non-Goals

- FastAPI routes.
- OAuth/OIDC.
- JWT validation.
- database persistence.
- SQLite checkpointing.
- rate limiting.
- LLM calls.
- real GitHub calls.
- real workflow triggers.
- frontend.

## Implemented Flow

```text
start_task
→ graph invoke with thread_id
→ policy requires approval
→ pause_for_approval
→ handle_approval_decision
→ interrupt(...)
→ checkpointed PAUSED_FOR_APPROVAL state
```

On approval:

```text
approve_task
→ Command(resume={approval_decision, approval_actor})
→ validate approval actor has approval:approve
→ execute dry-run tool
→ generate final report
```

On rejection:

```text
reject_task
→ Command(resume={approval_decision, approval_actor})
→ validate approval actor has approval:reject
→ finalize rejection
→ no tool execution
```

## Safety Rules

- High-risk execution does not occur before approval.
- Admin does not bypass approval.
- Invalid or missing approval decisions fail safely.
- Invalid or under-scoped approval actors fail safely.
- Rejected tasks do not execute tools.

## Persistence Limitation

Sprint 6 uses `InMemorySaver`.

This means checkpoints are local to the running process. State does not survive process restart, and no durable database-backed checkpointing is implemented.

## Acceptance Criteria Status

- allowed path remains supported.
- denied path remains supported.
- high-risk path pauses before execution.
- approved resume executes the dry-run tool.
- rejected resume does not execute the tool.
- invalid resume inputs fail safely.
- service can fetch current checkpointed task state.
