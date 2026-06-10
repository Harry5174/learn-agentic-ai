# Public Safety

## Sprint 8 Status

Sprint 8 adds basic public-demo safety for the FastAPI API through in-memory rate limiting.

For the broader V1 safety model, see `docs/security-model-v1.md`.

## Identity Boundary

V1 uses API-key identity resolved by the server from `X-API-Key`.

It does not implement:

- OAuth/OIDC
- JWT validation
- external identity providers
- user-managed accounts

Clients cannot set role, scopes, user ID, or rate limit identity through request bodies.

## Rate Limiting

V1 uses a simple in-memory fixed-window rate limiter.

Protected route groups:

- task creation: `POST /tasks`, 5 requests per 60 seconds per API key
- approval actions: `POST /tasks/{task_id}/approve` and `POST /tasks/{task_id}/reject`, 10 requests per 60 seconds per API key

Rate limit keys are derived from server-resolved identity:

```text
api_key_id:route_group
```

Invalid or missing API keys fail with `401` before rate limiting is applied.

## Local/Demo Limitation

Rate limit state is in memory and process-local.

This means:

- limits reset on process restart
- limits are not shared across processes
- limits are not shared across machines
- the limiter is suitable for local/demo abuse reduction only

Production or distributed deployments should use V2 infrastructure such as Redis, an API gateway, or platform-level traffic controls.

## Tool Safety

V1 does not perform real external GitHub writes or real workflow triggers.

All tools remain controlled dry-run tools. High-risk dry-run execution still requires approval before tool execution.

## Non-Goals

Sprint 8 does not add:

- Redis
- distributed rate limiting
- OAuth/OIDC
- JWT validation
- database persistence
- LLM/OpenAI calls
- frontend behavior
- deployment hardening

Production-oriented upgrades are listed in `docs/roadmap.md`.
