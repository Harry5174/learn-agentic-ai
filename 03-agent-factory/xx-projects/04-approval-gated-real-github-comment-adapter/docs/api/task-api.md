# Task API Reference

This page documents the inherited Artifact 1-style task API that remains
available in Artifact 2.

The primary Artifact 2.1 API is the skill-runner lifecycle documented in
[skill-runner-api.md](skill-runner-api.md).

Base URL for local development:

```text
http://127.0.0.1:8000
```

## Authentication

Endpoints that require identity use the `X-API-Key` header.

Demo keys:

| Key | User | Role | Notes |
| --- | --- | --- | --- |
| `viewer-dev-key` | `demo_viewer` | `viewer` | can inspect low-risk issues |
| `operator-dev-key` | `demo_operator` | `operator` | can request high-risk workflow approval |
| `admin-dev-key` | `demo_admin` | `admin` | can approve or reject paused high-risk tasks |

Identity is resolved server-side. Clients cannot set role, scopes, user ID, or
API key ID through request bodies.

## Rate Limiting

Task creation is limited to 5 requests per 60 seconds per API key.

Approval actions are limited to 10 requests per 60 seconds per API key.

Rate limit keys use server-derived `api_key_id` values.

## Endpoint List

- `GET /identity/me`
- `GET /tools`
- `POST /tasks`
- `GET /tasks/{task_id}`
- `POST /tasks/{task_id}/approve`
- `POST /tasks/{task_id}/reject`
- `GET /tasks/{task_id}/audit`

## `GET /identity/me`

Returns the server-derived identity for the provided API key.

```bash
curl -s http://127.0.0.1:8000/identity/me \
  -H "X-API-Key: viewer-dev-key"
```

## `GET /tools`

Returns public metadata for controlled dry-run tools.

```bash
curl -s http://127.0.0.1:8000/tools
```

The endpoint returns tool names, descriptions, risk levels, and required scopes.
It does not expose callables, handlers, graph objects, or execution functions.

## `POST /tasks`

Starts a task through the inherited deterministic task graph.

```bash
curl -s -X POST http://127.0.0.1:8000/tasks \
  -H "Content-Type: application/json" \
  -H "X-API-Key: viewer-dev-key" \
  -d '{"user_query": "inspect sandbox issues"}'
```

Response behavior:

- low-risk allowed task -> `completed`
- policy-denied task -> `denied`
- unsupported task -> `failed`
- high-risk task -> `paused_for_approval`

## `GET /tasks/{task_id}`

Returns the current public task summary.

```bash
curl -s http://127.0.0.1:8000/tasks/TASK_ID
```

## `POST /tasks/{task_id}/approve`

Approves and resumes a paused high-risk task.

```bash
curl -s -X POST http://127.0.0.1:8000/tasks/TASK_ID/approve \
  -H "Content-Type: application/json" \
  -H "X-API-Key: admin-dev-key" \
  -d '{"reason": "Approved for dry-run execution."}'
```

Approval authority is derived from the `X-API-Key` identity. Request bodies do
not define approver identity or scopes.

## `POST /tasks/{task_id}/reject`

Rejects and resumes a paused high-risk task without executing the tool.

```bash
curl -s -X POST http://127.0.0.1:8000/tasks/TASK_ID/reject \
  -H "Content-Type: application/json" \
  -H "X-API-Key: admin-dev-key" \
  -d '{"reason": "Rejected during review."}'
```

## `GET /tasks/{task_id}/audit`

Returns structured audit events for an existing task.

```bash
curl -s http://127.0.0.1:8000/tasks/TASK_ID/audit
```

## Demo Guide

For a curl-oriented walkthrough of this inherited task API, see
[../demos/task-api-demo.md](../demos/task-api-demo.md).

For the primary Artifact 2.1 skill-runner demo, see
[../demos/skill-runner-api-demo.md](../demos/skill-runner-api-demo.md).
