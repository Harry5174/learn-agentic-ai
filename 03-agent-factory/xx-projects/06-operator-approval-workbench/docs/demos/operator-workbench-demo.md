# Operator Workbench Demo

## Purpose

This runbook packages the Artifact 06 local/demo operator workflow for review,
interviews, and portfolio walkthroughs.

The demo story:

```text
AI proposes -> operator reviews -> operator approves/rejects -> harness executes safely -> status/audit/ledger evidence is visible
```

Artifact 06 remains local/demo and fake/default. It does not require a GitHub
token, `.env`, live GitHub, OAuth/OIDC, sessions, deployment, Next.js,
`package.json`, or `node_modules`.

## What The Demo Shows

The operator can:

- open the local static workbench
- paste a local demo API key for the browser page session
- load the approval inbox
- inspect approval detail
- review proposed action, risk, required scopes, target context, execution
  mode, policy decisions, and validated arguments
- approve or reject through A6 operator routes
- refresh status after the decision
- inspect decision history, local/demo audit timeline, side-effect/ledger
  visibility, execution result visibility, and known local/demo limitations

## What The Demo Does Not Show

The demo does not show:

- live GitHub execution from Artifact 06
- token loading
- `.env` reading
- OAuth/OIDC or browser sessions
- production authorization
- production-grade audit logging
- deployment
- a Next.js or React frontend
- a durable multi-user operator dashboard

## Local Demo Flow

1. Start the Artifact 06 FastAPI app using the repository's normal local
   command for this project.
2. Open the local workbench route:

```text
GET /operator/workbench
```

3. Paste a local demo API key for the page session.
4. Refresh approvals.
5. Select a pending approval.
6. Review the details:

```text
approval id
run id
task
risk level
policy status
required scopes
tool name
repo/issue target when available
side_effect_id when available
args_hash when available
fake/default execution mode
```

7. Approve or reject through the A6 operator route:

```text
POST /operator/approvals/{approval_id}/approve
POST /operator/approvals/{approval_id}/reject
```

8. Refresh the selected approval.
9. Inspect post-decision visibility:

```text
GET /operator/approvals/{approval_id}/status
GET /operator/approvals/{approval_id}/audit
GET /operator/side-effects/{side_effect_id}
```

## Route Boundary

The workbench calls only A6 operator routes:

```text
GET /operator/approvals
GET /operator/approvals/{approval_id}
GET /operator/approvals/{approval_id}/status
GET /operator/approvals/{approval_id}/audit
GET /operator/side-effects/{side_effect_id}
POST /operator/approvals/{approval_id}/approve
POST /operator/approvals/{approval_id}/reject
```

It does not call inherited Artifact 04 task/skill approval routes.

## Safety Boundary

The backend derives actor identity from server-owned API-key resolution. The
approve/reject request body cannot claim actor identity, role, scopes,
repository policy, real-mode enablement, token values, `args_hash`, or
`side_effect_id` authority.

The browser page keeps the pasted local demo API key only in page memory and
sends it only as `X-API-Key`. The static assets do not store it in browser
storage and do not embed key values.

## Screenshot Placeholder

No screenshots are included in A6.5 by default.

Before adding screenshots later, confirm they contain no real tokens, no
`.env` contents, no authorization headers, no absolute local filesystem paths,
and no unsafe repository data. Prefer redacted local/demo data only.
