# API Reference

## Status

The FastAPI surface is a local/demo API. It exposes the inherited deterministic
task harness and the first Artifact 2.1 skill-runner routes.

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

Identity is resolved server-side by `get_current_identity`. Clients cannot set
role, scopes, user ID, or API key ID through request bodies.

Authentication errors:

- missing key: `401`, `Missing X-API-Key header.`
- invalid key: `401`, `Invalid API key.`

## Rate Limiting

Rate limiting happens after identity resolution and uses server-derived
`api_key_id` values. Clients cannot influence rate limit keys through request
bodies.

Protected route groups:

- task creation: `POST /tasks`, 5 requests per 60 seconds per API key
- skill-run creation: `POST /skill-runs`, 5 requests per 60 seconds per API key
- approval actions: `POST /tasks/{task_id}/approve`,
  `POST /tasks/{task_id}/reject`, `POST /skill-runs/{run_id}/approve`, and
  `POST /skill-runs/{run_id}/reject`, 10 requests per 60 seconds per API key

Rate limit response:

```json
{
  "detail": "Rate limit exceeded."
}
```

Invalid or missing API keys return `401` before rate limiting.

## Endpoint List

- `GET /identity/me`
- `GET /tools`
- `GET /skills`
- `POST /tasks`
- `GET /tasks/{task_id}`
- `POST /tasks/{task_id}/approve`
- `POST /tasks/{task_id}/reject`
- `GET /tasks/{task_id}/audit`
- `POST /skill-runs`
- `GET /skill-runs/{run_id}`
- `POST /skill-runs/{run_id}/approve`
- `POST /skill-runs/{run_id}/reject`
- `GET /skill-runs/{run_id}/audit`

## `GET /identity/me`

Returns the server-derived identity for the provided API key.

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

Returns public metadata for controlled dry-run tools.

Example:

```bash
curl -s http://127.0.0.1:8000/tools
```

The endpoint returns tool names, descriptions, risk levels, and required scopes.
It does not expose callables, handlers, graph objects, or execution functions.

Status codes:

- `200 OK`

## `GET /skills`

Returns public metadata for registered skills.

Example:

```bash
curl -s http://127.0.0.1:8000/skills
```

The endpoint returns skill IDs, versions, names, descriptions, risk levels,
required scopes, and safe step metadata. It does not expose callables, registry
internals, graph objects, checkpointer state, or tool implementation objects.

Status codes:

- `200 OK`

## `POST /tasks`

Starts a task through the inherited deterministic task graph.

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

Returns the current public task summary.

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

Approves and resumes a paused high-risk task.

Example:

```bash
curl -s -X POST http://127.0.0.1:8000/tasks/TASK_ID/approve \
  -H "Content-Type: application/json" \
  -H "X-API-Key: admin-dev-key" \
  -d '{"reason": "Approved for dry-run execution."}'
```

Response behavior:

- valid admin approval -> `completed`
- invalid approver -> failed task summary without tool execution
- missing task -> `404`
- non-paused task -> `409`
- over approval rate limit -> `429`

Status codes:

- `200 OK`
- `401 Unauthorized`
- `404 Not Found`
- `409 Conflict`
- `429 Too Many Requests`

## `POST /tasks/{task_id}/reject`

Rejects and resumes a paused high-risk task without executing the tool.

Example:

```bash
curl -s -X POST http://127.0.0.1:8000/tasks/TASK_ID/reject \
  -H "Content-Type: application/json" \
  -H "X-API-Key: admin-dev-key" \
  -d '{"reason": "Rejected during review."}'
```

Status codes:

- `200 OK`
- `401 Unauthorized`
- `404 Not Found`
- `409 Conflict`
- `429 Too Many Requests`

## `GET /tasks/{task_id}/audit`

Returns structured audit events for an existing task.

Example:

```bash
curl -s http://127.0.0.1:8000/tasks/TASK_ID/audit
```

Status codes:

- `200 OK`
- `404 Not Found`

## `POST /skill-runs`

Starts a skill run through the Artifact 2 skill graph.

Example:

```bash
curl -s -X POST http://127.0.0.1:8000/skill-runs \
  -H "Content-Type: application/json" \
  -H "X-API-Key: viewer-dev-key" \
  -d '{"task": "Inspect sandbox health.", "proposer_mode": "fake"}'
```

Request body:

```json
{
  "task": "Inspect sandbox health.",
  "proposer_mode": "fake",
  "requested_skill_id": "inspect_sandbox_health"
}
```

Response behavior:

- omitted `proposer_mode` defaults to `fake`
- `fake` uses the existing deterministic proposer through `SkillGraphService`
- `llm` returns a safe `400` response without calling a live model provider
- invalid proposals are rejected before policy evaluation or tool execution
- low-risk accepted proposals execute dry-run tools
- high-risk accepted proposals pause for approval instead of executing

Status codes:

- `202 Accepted`
- `400 Bad Request`
- `401 Unauthorized`
- `422 Unprocessable Entity`
- `429 Too Many Requests`

## `GET /skill-runs/{run_id}`

Returns the current public summary for a process-local skill run.

Status codes:

- `200 OK`
- `404 Not Found`

Missing skill-run response:

```json
{
  "detail": "Skill run not found."
}
```

## `POST /skill-runs/{run_id}/approve`

Approves and resumes a paused high-risk skill run using the server-derived
identity from `X-API-Key`.

Response behavior:

- valid admin approval -> `completed`
- invalid approver -> failed skill-run summary without tool execution
- missing run -> `404`
- non-paused run -> `409`
- over approval rate limit -> `429`

Status codes:

- `200 OK`
- `401 Unauthorized`
- `404 Not Found`
- `409 Conflict`
- `422 Unprocessable Entity`
- `429 Too Many Requests`

## `POST /skill-runs/{run_id}/reject`

Rejects and resumes a paused high-risk skill run without executing the pending
high-risk dry-run tool.

Status codes:

- `200 OK`
- `401 Unauthorized`
- `404 Not Found`
- `409 Conflict`
- `422 Unprocessable Entity`
- `429 Too Many Requests`

## `GET /skill-runs/{run_id}/audit`

Returns a JSON-safe public audit trail for a process-local skill run.

Status codes:

- `200 OK`
- `404 Not Found`

## Public Task Summary Shape

Task endpoints return:

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

## Current Skill-Runner Boundary

Artifact 2 skill-runner behavior lives in:

- `src/app/skills/`
- `src/app/proposer/`
- `src/app/skill_graph/`

It is exposed through `GET /skills`, `POST /skill-runs`,
`GET /skill-runs/{run_id}`, `POST /skill-runs/{run_id}/approve`,
`POST /skill-runs/{run_id}/reject`, and `GET /skill-runs/{run_id}/audit`, and
is verified by tests such as:

- `tests/test_proposal_validator.py`
- `tests/test_fake_proposer.py`
- `tests/test_llm_proposer.py`
- `tests/test_skill_execution_graph.py`
- `tests/test_api_skill_runs.py`

## Known API Limitations

- process-local task state
- in-memory checkpoints
- in-memory audit events
- in-memory rate limits
- static demo API keys
- no OAuth/OIDC
- no JWT validation
- no database persistence
- no real GitHub writes
- no real workflow triggers
