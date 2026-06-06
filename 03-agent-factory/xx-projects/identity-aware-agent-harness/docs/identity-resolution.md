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

## Future FastAPI Integration
FastAPI is not implemented yet.

Later, a FastAPI dependency can read the X-API-Key header and call this pure resolver.

Example future flow only, not implemented:
```text
X-API-Key header
→ FastAPI dependency
→ resolve_identity_from_api_key
→ request-scoped IdentityContext
```

## Safety Invariant Status
- Identity is server-derived.
- Policy is not implemented yet.
- Tool execution is not implemented yet.
- High-risk execution cannot happen.
