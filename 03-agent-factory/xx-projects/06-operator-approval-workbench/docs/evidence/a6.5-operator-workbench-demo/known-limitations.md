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

A6.5.1 adds a narrow fake-mode seeding path for the manual demo:
`POST /skill-runs` may request a server-known fake demo skill such as
`post_github_issue_comment`. The request still cannot provide identity, role,
scopes, approval status, risk level, repository policy, side-effect status,
audit data, execution results, token values, or `.env` behavior. Unknown
`requested_skill_id` values fail closed instead of falling back to a low-risk
run.

`POST /skill-runs` is limited to 5 creates per 60 seconds per
identity/route group. During repeated local demos, a `429` means the operator
should wait for `Retry-After` or restart the local dev server.

Side-effect/ledger visibility is limited to local state already available
through the run, audit trail, and execution result. Known side-effect ids
without available ledger records return an explicit local/demo limitation
instead of an invented record.

Audit visibility is local/demo process-state evidence, not a production-grade
audit log.
