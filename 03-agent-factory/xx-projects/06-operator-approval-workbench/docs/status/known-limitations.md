# Known Limitations

A6.0 is not a working operator console.

## Not Implemented

A6.0 does not implement:

- `src/app`
- copied Artifact 04 runtime code
- operator approval inbox API
- approve/reject API
- operator UI
- static HTML workbench
- Next.js frontend
- OAuth/OIDC
- MCP
- deployment
- live GitHub execution
- new GitHub adapter
- real token loading
- `.env` reading
- general GitHub automation
- PR creation
- issue creation
- branch creation
- repo file writes
- workflow dispatch
- labels or milestones

## Evidence Limits

The runtime inventory is source-based and line-count based. It documents module
shape and future integration candidates but does not prove a new operator API.

Artifact 05 evidence is referenced only as release-gate context. It is not a
runtime baseline and does not add an operator console.

## Future Risk Areas

Future A6 implementation must handle:

- stale approval records
- mismatched `args_hash`
- mismatched `side_effect_id`
- viewer/operator/admin authorization differences
- safe rendering of comment bodies
- audit event completeness
- fake/default mode visibility
- no-token local/demo operation
- no live GitHub calls in automated tests
