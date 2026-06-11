# Public Safety

## Scope

This project is a local/demo artifact. Public safety controls are intentionally
small and in-memory.

For the broader safety model, see `docs/security-model-v1.md` and
`docs/threat-model.md`.

## Identity Boundary

The demo API uses API-key identity resolved by the server from `X-API-Key`.

It does not implement:

- OAuth/OIDC
- JWT validation
- external identity providers
- user-managed accounts

Clients and model outputs cannot set role, scopes, user ID, or rate-limit
identity.

## Rate Limiting

The API uses a simple in-memory fixed-window rate limiter.

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

Production or distributed deployments should use infrastructure such as Redis,
an API gateway, or platform-level traffic controls.

## Model Output Safety

The model is not trusted to choose executable work.

Artifact 2 uses deterministic validation before policy or execution. Unknown
skills, hallucinated tools, malformed output, missing scopes, and risk
understatement are rejected before tool execution.

## Tool Safety

The harness does not perform real external GitHub writes or real workflow
triggers.

All tools remain controlled dry-run tools. High-risk dry-run execution still
requires approval before tool execution.

## Non-Goals

This project does not add:

- Redis
- distributed rate limiting
- OAuth/OIDC
- JWT validation
- database persistence
- MCP
- frontend behavior
- deployment hardening
- real GitHub writes
- real workflow triggers

Production-oriented upgrades are listed in `docs/roadmap.md`.
