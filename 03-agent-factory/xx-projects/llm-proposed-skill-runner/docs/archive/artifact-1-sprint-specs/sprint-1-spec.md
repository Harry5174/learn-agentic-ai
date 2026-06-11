# Sprint 1: Identity Resolution and API-Key Mapping

## Objective
Implement a pure, testable identity resolver that maps server-known API keys to IdentityContext objects.

## Scope
- identity config module
- identity resolver module
- identity error type
- resolver tests

## Non-Goals
- FastAPI routes
- FastAPI dependencies
- OAuth/OIDC
- JWT validation
- policy guard
- tool registry
- dry-run tools
- LangGraph
- approval logic
- database
- checkpointing
- rate limiting
- LLM calls
- GitHub API integration
- frontend

## Implemented Files
- `src/app/identity/errors.py`
- `src/app/identity/config.py`
- `src/app/identity/resolver.py`
- `tests/test_identity_resolver.py`

## V1 Demo Identity Fixtures

**Viewer:**
```yaml
api_key_id: demo-viewer-key
user_id: demo_viewer
role: VIEWER
scopes:
  - tasks:read
  - tasks:create
  - tools:inspect
```

**Operator:**
```yaml
api_key_id: demo-operator-key
user_id: demo_operator
role: OPERATOR
scopes:
  - tasks:read
  - tasks:create
  - tools:inspect
  - tools:draft
  - approval:request
```

**Admin:**
```yaml
api_key_id: demo-admin-key
user_id: demo_admin
role: ADMIN
scopes:
  - tasks:read
  - tasks:create
  - tools:inspect
  - tools:draft
  - tools:trigger_workflow
  - approval:approve
  - approval:reject
```

*Note: Admin does not bypass policy. Admin still goes through policy guard in later modules.*

## Acceptance Criteria
- valid viewer key resolves correctly
- valid operator key resolves correctly
- valid admin key resolves correctly
- invalid key raises IdentityResolutionError
- empty/whitespace key raises IdentityResolutionError
- role/scopes are derived server-side
- no request-body identity is accepted
- no FastAPI dependency is required
- tests pass
- ruff passes
- safety invariant is preserved

## Test Status
- 34 passed
- All checks passed
