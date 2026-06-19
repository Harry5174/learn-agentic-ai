# Known Limitations

A6.5 is a local/demo documentation and evidence package. It does not make
Artifact 06 production-ready.

## Still Out Of Scope

- live GitHub execution in Artifact 06
- GitHub token loading
- `.env` reading
- OAuth/OIDC
- sessions
- deployment
- production authorization
- production-grade audit logging
- Next.js
- React
- package-managed frontend tooling
- durable multi-user operator dashboard
- distinct durable approval identifiers beyond local/demo `run_id`
- screenshots by default

## Local/Demo Limits

The workbench uses local/demo process state and copied runtime behavior. It is
useful for explaining the approval workflow, but it is not a deployed operator
console.

Side-effect/ledger visibility is limited to local state already available
through the run, audit trail, and execution result. Known side-effect ids
without available ledger records return an explicit local/demo limitation
instead of an invented record.

Audit visibility is local/demo process-state evidence, not a production-grade
audit log.
