# Checkpoint and Resume Design

## Purpose

Checkpointing lets the local graph pause before high-risk execution and resume later with an explicit approval decision.

## Current Implementation

The graph is compiled with LangGraph `InMemorySaver`.

```text
build_harness_graph()
→ StateGraph(HarnessGraphState)
→ compile(checkpointer=InMemorySaver())
```

Each task uses a LangGraph config containing a `thread_id`:

```text
{"configurable": {"thread_id": task_id}}
```

`HarnessGraphService` owns graph access for the API layer and tests:

- `start_task(user_query, identity)`
- `get_task(task_id)`
- `approve_task(task_id, approver, reason)`
- `reject_task(task_id, rejector, reason)`
- `get_audit(task_id)`

## Approval Pause

When policy returns `REQUIRE_APPROVAL`, the graph:

- creates an `ApprovalRequest`
- records an approval-requested audit event
- sets status to `PAUSED_FOR_APPROVAL`
- keeps `tool_result` as `None`
- interrupts before high-risk execution

## Resume Payload

Resume uses LangGraph `Command(resume=...)` with:

- `approval_decision`
- `approval_actor`

The graph validates both values before routing.

## Approved Resume

An approved decision requires an approval actor with `approval:approve`.

If valid, the graph routes to dry-run tool execution and then report generation.

## Rejected Resume

A rejected decision requires an approval actor with `approval:reject`.

If valid, the graph finalizes the task as rejected and does not execute the tool.

## Invalid Resume

The task fails safely when:

- approval request context is missing
- approval decision is missing or invalid
- approval actor is missing or invalid
- approval actor lacks the required approval scope

## Current Limitation

Checkpointing is in-memory and process-local.

Paused tasks can be resumed only while the current process and `HarnessGraphService` graph instance remain alive. Durable persistence is not implemented in the current V1/Sprint 7 state.
