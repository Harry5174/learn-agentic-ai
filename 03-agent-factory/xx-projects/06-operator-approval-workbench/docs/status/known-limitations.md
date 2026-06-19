# Known Limitations

A6.2 is not a working operator console UI.

## Not Implemented

A6.2 does not implement:

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

## A6.2 Local/Demo Limits

- A6.1 and A6.2 use `run_id` as `approval_id` for local/demo approval rows until
  a distinct durable approval identifier is introduced later.
- A6.2 approval rows come from in-memory copied skill-run state.
- A6.2 list/detail views are read-only.
- A6.2 approve/reject routes may resume the inherited fake/default graph path
  after server-derived scope and stale/mismatch checks pass.
- Inherited Artifact 04 task/skill approval routes still exist because the
  runtime baseline was copied; those are not the A6 operator workbench routes.
- A6.2 does not provide durable operator inbox storage beyond the copied runtime
  baseline.
- For Artifact 06 local/demo identity configuration, `OPERATOR_API_KEY` has
  `approval:approve` and `approval:reject` scopes. This is demo configuration,
  not a production authorization model.

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
