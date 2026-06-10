# API Reference

## Status

The API is a local/demo FastAPI surface for the current portfolio MVP. Sprint 8 is complete.

API task state is backed by a module-level, in-memory `HarnessGraphService` and LangGraph `InMemorySaver`. Task state and checkpoints are process-local, do not survive process restart, and are not backed by durable persistence.

Public-demo abuse protection is provided by a simple in-memory fixed-window rate limiter. Rate limit state is process-local and resets on process restart.

## Authentication

Endpoints that require identity use the `X-API-Key` header.

Identity is resolved server-side by `get_current_identity`, which calls the pure API-key resolver. Clients cannot set role, scopes, or user ID through request bodies.

Missing or invalid API keys return `401`.

## Rate Limiting

Rate limiting happens after identity resolution and uses server-derived `api_key_id` values. Clients cannot influence rate limit keys through request bodies.

Protected route groups:

- task creation: `POST /tasks`, 5 requests per 60 seconds per API key
- approval actions: `POST /tasks/{task_id}/approve` and `POST /tasks/{task_id}/reject`, 10 requests per 60 seconds per API key

When a protected endpoint exceeds its limit, the API returns:

- status: `429`
- detail: `Rate limit exceeded.`

Invalid or missing API keys still return `401` before rate limiting.

## Response Summary: Task State

Task endpoints return a public task summary with these fields:

- `task_id`
- `status`
- `selected_tool_name`
- `requires_approval`
- `final_report`
- `error_message`
- `approval_request`

`approval_request` is present only while the task is paused for approval.

## `GET /tools`

Purpose:

Returns public metadata for the controlled dry-run tools.

Auth:

- none

Request body:

- none

Response summary:

- `tools`
- each tool includes name, description, risk level, and required scopes

Important error cases:

- no endpoint-specific error cases

The endpoint does not expose callables, handlers, internal graph objects, or execution functions.

## `GET /identity/me`

Purpose:

Returns the server-derived identity for the provided API key.

Auth:

- requires `X-API-Key`

Request body:

- none

Response summary:

```json
{
  "user_id": "demo_viewer",
  "role": "viewer",
  "scopes": ["tasks:read", "tasks:create", "tools:inspect"]
}
```

Important error cases:

- missing key: `401`, `Missing X-API-Key header.`
- invalid key: `401`, `Invalid API key.`

Request bodies cannot override the resolved identity.

## `POST /tasks`

Purpose:

Starts a graph task through `HarnessGraphService.start_task`.

Auth:

- requires `X-API-Key`

Request body:

```json
{
  "user_query": "inspect sandbox issues"
}
```

Response summary:

- success status: `202 Accepted`
- returns the public task summary
- allowed low-risk tasks can complete immediately
- denied tasks return a denied task summary
- unsupported tasks fail safely
- high-risk trigger workflow tasks pause for approval

Important error cases:

- missing key: `401`, `Missing X-API-Key header.`
- invalid key: `401`, `Invalid API key.`
- over task creation rate limit: `429`, `Rate limit exceeded.`

The body includes only `user_query`. Role, scopes, and user ID are ignored if provided as extra client data.

## `GET /tasks/{task_id}`

Purpose:

Returns the current public task state summary through `HarnessGraphService.get_task`.

Auth:

- none

Request body:

- none

Response summary:

- success status: `200 OK`
- returns the public task summary

Important error cases:

- missing task: `404`, `Task not found.`

## `POST /tasks/{task_id}/approve`

Purpose:

Approves and resumes a paused high-risk task through `HarnessGraphService.approve_task`.

Auth:

- requires `X-API-Key`

Request body:

Optional:

```json
{
  "reason": "Approved for dry-run execution."
}
```

Response summary:

- success status: `200 OK`
- returns the public task summary
- valid admin approval completes the task
- `requires_approval` becomes `false`
- `final_report` is present after completion

Important error cases:

- missing key: `401`, `Missing X-API-Key header.`
- invalid key: `401`, `Invalid API key.`
- over approval action rate limit: `429`, `Rate limit exceeded.`
- missing task: `404`, `Task not found.`
- non-paused task: `409`, `Task is not paused for approval.`

Approval policy is not duplicated in the route. If the approver lacks `approval:approve`, the graph/service layer fails safely and the route returns the resulting failed task summary without tool execution.

## `POST /tasks/{task_id}/reject`

Purpose:

Rejects and resumes a paused high-risk task through `HarnessGraphService.reject_task`.

Auth:

- requires `X-API-Key`

Request body:

Optional:

```json
{
  "reason": "Rejected during review."
}
```

Response summary:

- success status: `200 OK`
- returns the public task summary
- valid admin rejection marks the task `rejected`
- `requires_approval` becomes `false`
- `final_report` explains the rejection

Important error cases:

- missing key: `401`, `Missing X-API-Key header.`
- invalid key: `401`, `Invalid API key.`
- over approval action rate limit: `429`, `Rate limit exceeded.`
- missing task: `404`, `Task not found.`
- non-paused task: `409`, `Task is not paused for approval.`

Rejection policy is not duplicated in the route. If the rejector lacks `approval:reject`, the graph/service layer fails safely and the route returns the resulting failed task summary without tool execution.

## `GET /tasks/{task_id}/audit`

Purpose:

Returns the structured audit trail for an existing task through `HarnessGraphService.get_audit`.

Auth:

- none

Request body:

- none

Response summary:

```json
{
  "task_id": "task-id",
  "audit_trail": []
}
```

Approved high-risk paths include:

- `approval_requested`
- `approval_granted`
- `tool_executed`
- `task_completed`

Rejected high-risk paths include:

- `approval_requested`
- `approval_rejected`

Rejected high-risk paths exclude:

- `tool_executed`

Important error cases:

- missing task: `404`, `Task not found.`

## Current Limitations

This API should be treated as a local/demo API, not production infrastructure.

Current limitations:

- task state does not survive process restart
- paused tasks can be resumed only while the process is alive
- durable persistence is not implemented
- SQLite checkpointing is not implemented
- rate limiting is in-memory only and not distributed
- OAuth/OIDC and JWT validation are not implemented
- LLM/OpenAI behavior is not implemented
- frontend and deployment changes are not implemented
