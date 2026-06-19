# Known Limitations

A6.4 is a local static operator workbench with read-only status, audit,
side-effect/ledger, execution-result, and decision-history visibility. It is
not a production operator console.

## Not Implemented

A6.4 does not implement:

- Next.js frontend
- OAuth/OIDC
- sessions
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

## A6.4 Local/Demo Limits

- A6.1 and A6.2 use `run_id` as `approval_id` for local/demo approval rows until
  a distinct durable approval identifier is introduced later.
- A6.4 visibility uses `run_id` as `approval_id` for local/demo status and audit
  views.
- A6.4 approval rows and visibility views come from copied local/demo skill-run
  state.
- A6.2 list/detail views are read-only.
- A6.4 visibility endpoints are read-only.
- A6.2 approve/reject routes may resume the inherited fake/default graph path
  after server-derived scope and stale/mismatch checks pass.
- Inherited Artifact 04 task/skill approval routes still exist because the
  runtime baseline was copied; those are not the A6 operator workbench routes.
- A6.2 does not provide durable operator inbox storage beyond the copied runtime
  baseline.
- A6.4 audit visibility is local/demo process-state evidence, not a
  production-grade audit log.
- A6.4 side-effect/ledger visibility is limited to local state already available
  through the run, audit trail, and execution result.
- A6.4 does not create side-effect records to satisfy visibility reads.
- For Artifact 06 local/demo identity configuration, `OPERATOR_API_KEY` has
  `approval:approve` and `approval:reject` scopes. This is demo configuration,
  not a production authorization model.
- A6.4 stores no browser session and has no login flow.
- A6.4 requires the operator to paste a local demo API key into the page for
  each browser page session.
- A6.4 calls only A6 operator routes and does not call inherited Artifact 04
  approval routes.
- A6.4 provides a local review UI only; it is not a durable operator dashboard.

## Evidence Limits

Artifact 05 evidence is referenced only as release-gate context. It is not a
runtime baseline and does not add this operator workbench.

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
