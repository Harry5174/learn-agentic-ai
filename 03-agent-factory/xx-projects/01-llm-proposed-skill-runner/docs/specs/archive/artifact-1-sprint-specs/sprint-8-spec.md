# Sprint 8: Rate Limiting and Public Safety

## Status

Sprint 8 is complete.

## Goal

Add local/demo public safety controls through simple in-memory API rate limiting.

The goal is to reduce repeated task creation, approval/rejection spam, and accidental public misuse while keeping the implementation V1-appropriate.

## Completed Scope

Sprint 8 added:

- `src/app/api/rate_limiter.py`
- in-memory fixed-window rate limiting
- rate-limit dependencies in the API layer
- protection for `POST /tasks`
- protection for `POST /tasks/{task_id}/approve`
- protection for `POST /tasks/{task_id}/reject`
- public safety documentation
- focused rate-limiting tests

## Rate Limiter Design

The rate limiter is a simple in-memory fixed-window limiter.

It is intentionally local and boring:

- no Redis
- no external service
- no database
- no distributed coordination
- no sleep-based tests

Tests use an injectable time provider so window reset behavior is deterministic.

## Protected Endpoints

Protected endpoints:

- `POST /tasks`
- `POST /tasks/{task_id}/approve`
- `POST /tasks/{task_id}/reject`

The read endpoints remain unprotected in V1:

- `GET /tools`
- `GET /identity/me`
- `GET /tasks/{task_id}`
- `GET /tasks/{task_id}/audit`

## Rate Limits

Configured limits:

- task creation: 5 requests per 60 seconds per API key
- approval actions: 10 requests per 60 seconds per API key

Approval actions include:

- approve
- reject

## Identity Rule

Rate limiting runs after identity resolution.

Rate limit keys are derived from server-resolved identity:

```text
identity.api_key_id:route_group
```

Clients cannot influence rate limit identity through request bodies.

Invalid or missing identity returns `401` before rate limiting is applied.

## Error Behavior

Over-limit protected requests return:

```text
429 Too Many Requests
```

Response detail:

```json
{
  "detail": "Rate limit exceeded."
}
```

Blocked requests do not create tasks and do not resume approval/rejection work.

## Acceptance Criteria

Sprint 8 is complete because:

- in-memory rate limiter exists
- `POST /tasks` is rate-limited
- approval/rejection endpoints are rate-limited
- exceeding a limit returns `429`
- invalid/missing API key still returns `401`
- rate limit key uses server-derived `identity.api_key_id`
- blocked requests do not create or resume work
- tests pass
- ruff passes
- public safety limitations are documented

## Limitations

The Sprint 8 limiter is local/demo infrastructure only.

Limitations:

- process-local
- in-memory only
- limits reset on process restart
- limits are not shared across workers
- limits are not shared across machines
- not production distributed traffic control

Production or distributed deployments should use Redis, an API gateway, or platform-level traffic controls.

## Non-Goals

Sprint 8 did not add:

- OAuth/OIDC
- JWT validation
- Redis
- distributed rate limiting
- database persistence
- LLM behavior
- OpenAI dependency
- frontend
- deployment changes
- real GitHub calls
- real workflow triggers
- LangSmith tracing
