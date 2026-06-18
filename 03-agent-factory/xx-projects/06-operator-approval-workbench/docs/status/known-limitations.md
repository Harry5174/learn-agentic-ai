# Known Limitations

A6.1 is not a working operator console UI.

## Not Implemented

A6.1 does not implement:

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

## A6.1 Local/Demo Limits

- A6.1 uses `run_id` as `approval_id` for local/demo approval inbox rows until a
  distinct durable approval identifier is introduced later.
- A6.1 approval rows come from in-memory copied skill-run state.
- A6.1 list/detail views are read-only and do not mutate graph or ledger state.
- A6.1 does not provide durable operator inbox storage beyond the copied runtime
  baseline.

## Evidence Limits

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
