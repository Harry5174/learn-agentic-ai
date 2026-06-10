# Identity Resolution Design

## Purpose
The identity layer converts a server-known API key into an IdentityContext.

## Current Design
```text
api_key: str
→ resolve_identity_from_api_key(api_key)
→ IdentityContext
```

## Important Boundary
The resolver accepts only:
- `api_key: str`

It does not accept:
- `role`
- `scopes`
- `user_id`
- `api_key_id`
- request body identity data

## Files
- `config.py`: stores V1 demo API-key-to-identity mappings
- `errors.py`: defines IdentityResolutionError
- `resolver.py`: exposes resolve_identity_from_api_key

## Error Behavior
- missing/empty/whitespace key raises IdentityResolutionError
- invalid key raises IdentityResolutionError

## Mutation Safety
The resolver returns a copied IdentityContext so mutation of returned scopes does not affect future resolver calls.

## FastAPI Integration

Sprint 7 adds a FastAPI dependency that reads the `X-API-Key` header and calls this pure resolver.

```text
X-API-Key header
→ FastAPI dependency
→ resolve_identity_from_api_key
→ request-scoped IdentityContext
```

## Safety Invariant Status
- Identity is server-derived.
- Policy is deterministic.
- Tool execution is controlled through the registry and graph.
- High-risk execution cannot happen before approval.
