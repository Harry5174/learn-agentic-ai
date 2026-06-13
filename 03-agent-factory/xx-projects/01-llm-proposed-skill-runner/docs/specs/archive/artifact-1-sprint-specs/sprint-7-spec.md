# Sprint 7: FastAPI Task API

## Status

Sprint 7 is complete.

The completed implementation exposes a local/demo FastAPI API over the existing deterministic harness. It includes tool metadata, server-derived identity, task creation, task retrieval, approval, rejection, and audit endpoints.

## Objective

Add a thin FastAPI API layer without moving identity, policy, approval, tool execution, or graph behavior into route handlers.

## Completed Scope

- FastAPI application skeleton.
- `GET /tools`
- `X-API-Key` identity dependency.
- `GET /identity/me`
- `HarnessGraphService` wrapper.
- `POST /tasks`
- `GET /tasks/{task_id}`
- `POST /tasks/{task_id}/approve`
- `POST /tasks/{task_id}/reject`
- `GET /tasks/{task_id}/audit`
- Public API response schemas.
- Focused API tests for tools, identity, tasks, approval, rejection, and audit.

## API Boundary

Correct route shape:

```text
route
-> get_current_identity dependency where identity is required
-> HarnessGraphService
-> response schema
```

Routes must not:

- accept role/scopes/user_id from request bodies
- inspect role/scopes manually
- evaluate policy manually
- execute tools manually
- implement approval semantics directly

Approval and rejection routes delegate to `HarnessGraphService.approve_task` and `HarnessGraphService.reject_task`. Invalid approvers or rejectors fail safely in the graph/service layer and return the resulting public task summary.

## Implemented Endpoints

### `GET /tools`

Returns public metadata for registered tools:

- name
- description
- risk level
- required scopes

It does not expose callables or internal handlers.

### `GET /identity/me`

Requires `X-API-Key`.

Returns server-derived identity:

- user ID
- role
- scopes

Missing or invalid API keys return `401`.

### `POST /tasks`

Requires `X-API-Key`.

Request body:

```json
{
  "user_query": "inspect sandbox issues"
}
```

Starts a task through `HarnessGraphService.start_task` and returns `202 Accepted` with a public task summary.

Request bodies do not control identity.

### `GET /tasks/{task_id}`

Returns the current public task summary from `HarnessGraphService.get_task`.

Missing task IDs return `404`.

### `POST /tasks/{task_id}/approve`

Requires `X-API-Key`.

Optional request body:

```json
{
  "reason": "Approved for dry-run execution."
}
```

Resumes a paused task through `HarnessGraphService.approve_task` and returns a public task summary.

Important outcomes:

- valid admin approval completes the task
- invalid approver returns a failed task summary without tool execution
- missing task returns `404`
- non-paused task returns `409`

### `POST /tasks/{task_id}/reject`

Requires `X-API-Key`.

Optional request body:

```json
{
  "reason": "Rejected during review."
}
```

Resumes a paused task through `HarnessGraphService.reject_task` and returns a public task summary.

Important outcomes:

- valid admin rejection marks the task `rejected`
- rejected tasks do not execute the high-risk tool
- invalid rejector returns a failed task summary without tool execution
- missing task returns `404`
- non-paused task returns `409`

### `GET /tasks/{task_id}/audit`

Returns structured audit events for an existing task through `HarnessGraphService.get_audit`.

The response includes:

- `task_id`
- `audit_trail`

Missing task IDs return `404`.

Approved high-risk paths include approval and tool execution events. Rejected high-risk paths include rejection events and exclude tool execution events.

## Current State Limitation

The Sprint 7 API uses a module-level, in-memory `HarnessGraphService` instance for the local/demo API.

Task state and checkpoints are process-local. They do not survive process restart, and durable persistence is not implemented.

## Verification

Current checks:

```bash
uv run pytest
# 143 passed

uv run ruff check .
# All checks passed!
```

## Next Sprint

Sprint 8 is next: Rate Limiting and Public Safety.

## Non-Goals

- database persistence
- SQLite checkpointing
- OAuth/OIDC
- JWT validation
- rate limiting
- LLM calls
- real GitHub calls
- real workflow triggers
- frontend
- production deployment
