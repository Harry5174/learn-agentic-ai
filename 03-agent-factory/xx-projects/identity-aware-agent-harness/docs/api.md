# API Reference

## Status

The API is a local/demo FastAPI surface for the V1 portfolio MVP.

Base URL for local development:

```text
http://127.0.0.1:8000
```

V1 uses deterministic task interpretation to prove the harness. It does not call an LLM.

## Authentication

Endpoints that require identity use the `X-API-Key` header.

Demo keys:

| Key | User | Role | Notes |
| --- | --- | --- | --- |
| `viewer-dev-key` | `demo_viewer` | `viewer` | can inspect low-risk issues |
| `operator-dev-key` | `demo_operator` | `operator` | can request high-risk workflow approval |
| `admin-dev-key` | `demo_admin` | `admin` | can approve or reject paused high-risk tasks |

Identity is resolved server-side by `get_current_identity`. Clients cannot set role, scopes, user ID, or API key ID through request bodies.

Authentication errors:

- missing key: `401`, `Missing X-API-Key header.`
- invalid key: `401`, `Invalid API key.`

## Rate Limiting

Rate limiting happens after identity resolution and uses server-derived `api_key_id` values. Clients cannot influence rate limit keys through request bodies.

Protected route groups:

- task creation: `POST /tasks`, 5 requests per 60 seconds per API key
- approval actions: `POST /tasks/{task_id}/approve` and `POST /tasks/{task_id}/reject`, 10 requests per 60 seconds per API key

Rate limit response:

```json
{
  "detail": "Rate limit exceeded."
}
```

Status:

- `429 Too Many Requests`

Invalid or missing API keys still return `401` before rate limiting.

## Endpoint List

- `GET /identity/me`
- `GET /tools`
- `POST /tasks`
- `GET /tasks/{task_id}`
- `POST /tasks/{task_id}/approve`
- `POST /tasks/{task_id}/reject`
- `GET /tasks/{task_id}/audit`

## Task Summary Response

Task endpoints return a public task summary:

```json
{
  "task_id": "task-id",
  "status": "completed",
  "selected_tool_name": "inspect_sandbox_issues",
  "requires_approval": false,
  "final_report": "Task completed successfully using dry-run execution.",
  "error_message": null,
  "approval_request": null
}
```

`approval_request` is present only while the task is paused for approval.

## `GET /identity/me`

Purpose:

Returns the server-derived identity for the provided API key.

Auth:

- requires `X-API-Key`

Example:

```bash
curl -s http://127.0.0.1:8000/identity/me \
  -H "X-API-Key: viewer-dev-key"
```

Response:

```json
{
  "user_id": "demo_viewer",
  "role": "viewer",
  "scopes": ["tasks:read", "tasks:create", "tools:inspect"]
}
```

Status codes:

- `200 OK`
- `401 Unauthorized`

## `GET /tools`

Purpose:

Returns public metadata for the controlled dry-run tools.

Auth:

- none

Example:

```bash
curl -s http://127.0.0.1:8000/tools
```

Response summary:

- `tools`
- each tool includes name, description, risk level, and required scopes

The endpoint does not expose callables, handlers, internal graph objects, or execution functions.

Status codes:

- `200 OK`

## `POST /tasks`

Purpose:

Starts a graph task through `HarnessGraphService.start_task`.

Auth:

- requires `X-API-Key`

Example:

```bash
curl -s -X POST http://127.0.0.1:8000/tasks \
  -H "Content-Type: application/json" \
  -H "X-API-Key: viewer-dev-key" \
  -d '{"user_query": "inspect sandbox issues"}'
```

Request body:

```json
{
  "user_query": "inspect sandbox issues"
}
```

Response behavior:

- low-risk allowed task -> `completed`
- policy-denied task -> `denied`
- unsupported task -> `failed`
- high-risk task -> `paused_for_approval`

Status codes:

- `202 Accepted`
- `401 Unauthorized`
- `429 Too Many Requests`

## `GET /tasks/{task_id}`

Purpose:

Returns the current public task summary through `HarnessGraphService.get_task`.

Auth:

- none

Example:

```bash
curl -s http://127.0.0.1:8000/tasks/TASK_ID
```

Status codes:

- `200 OK`
- `404 Not Found`

Missing task response:

```json
{
  "detail": "Task not found."
}
```

## `POST /tasks/{task_id}/approve`

Purpose:

Approves and resumes a paused high-risk task through `HarnessGraphService.approve_task`.

Auth:

- requires `X-API-Key`

Example:

```bash
curl -s -X POST http://127.0.0.1:8000/tasks/TASK_ID/approve \
  -H "Content-Type: application/json" \
  -H "X-API-Key: admin-dev-key" \
  -d '{"reason": "Approved for dry-run execution."}'
```

Optional request body:

```json
{
  "reason": "Approved for dry-run execution."
}
```

Response behavior:

- valid admin approval -> `completed`
- invalid approver -> failed task summary without tool execution
- missing task -> `404`
- non-paused task -> `409`
- over approval rate limit -> `429`

Approval policy is not duplicated in the route.

Status codes:

- `200 OK`
- `401 Unauthorized`
- `404 Not Found`
- `409 Conflict`
- `429 Too Many Requests`

## `POST /tasks/{task_id}/reject`

Purpose:

Rejects and resumes a paused high-risk task through `HarnessGraphService.reject_task`.

Auth:

- requires `X-API-Key`

Example:

```bash
curl -s -X POST http://127.0.0.1:8000/tasks/TASK_ID/reject \
  -H "Content-Type: application/json" \
  -H "X-API-Key: admin-dev-key" \
  -d '{"reason": "Rejected during review."}'
```

Optional request body:

```json
{
  "reason": "Rejected during review."
}
```

Response behavior:

- valid admin rejection -> `rejected`
- rejected tasks do not execute the high-risk tool
- invalid rejector -> failed task summary without tool execution
- missing task -> `404`
- non-paused task -> `409`
- over approval action rate limit -> `429`

Rejection policy is not duplicated in the route.

Status codes:

- `200 OK`
- `401 Unauthorized`
- `404 Not Found`
- `409 Conflict`
- `429 Too Many Requests`

## `GET /tasks/{task_id}/audit`

Purpose:

Returns the structured audit trail for an existing task through `HarnessGraphService.get_audit`.

Auth:

- none

Example:

```bash
curl -s http://127.0.0.1:8000/tasks/TASK_ID/audit
```

Response shape:

```json
{
  "task_id": "task-id",
  "audit_trail": [
    {
      "event_id": "event-id",
      "task_id": "task-id",
      "event_type": "task_created",
      "actor_id": "demo_viewer",
      "message": "Task was created.",
      "timestamp": "2026-01-01T00:00:00Z",
      "tool_name": null,
      "metadata": {}
    }
  ]
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

Status codes:

- `200 OK`
- `404 Not Found`

## Approval and Rejection Flow

1. `operator-dev-key` creates a high-risk trigger workflow task.
2. The graph returns `paused_for_approval` and an `approval_request`.
3. `admin-dev-key` approves or rejects the task.
4. Approval resumes and executes the dry-run tool.
5. Rejection resumes and finalizes without tool execution.
6. Invalid approvers fail safely without tool execution.

## Known Demo Limitations

- API-key identity is static demo identity, not OAuth/OIDC.
- Task state and checkpoints are in-memory and process-local.
- Audit events are not persisted to a database.
- Rate limiting is in-memory and not distributed.
- Rate limits reset on process restart.
- Tools are dry-run only.
- No real GitHub writes happen.
- No real workflow triggers happen.
- No LLM/OpenAI call happens in V1.
