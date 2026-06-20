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

## Fresh Terminal Demo: Empty Inbox to Approved Run

Terminal 1 starts the local FastAPI server:

```bash
uv run app
```

Terminal 2 drives the demo with local demo keys:

```bash
BASE=http://127.0.0.1:8000
VIEWER_KEY=viewer-dev-key
OPERATOR_KEY=operator-dev-key
ADMIN_KEY=admin-dev-key
```

Verify identities:

```bash
curl -sS -H "X-API-Key: $VIEWER_KEY" "$BASE/identity/me"
curl -sS -H "X-API-Key: $OPERATOR_KEY" "$BASE/identity/me"
curl -sS -H "X-API-Key: $ADMIN_KEY" "$BASE/identity/me"
```

Verify the workbench assets:

```bash
curl -i -sS "$BASE/operator/workbench" | head
curl -i -sS "$BASE/operator/workbench.css" | head
curl -i -sS "$BASE/operator/workbench.js" | head
```

Create a pending local/demo GitHub comment approval:

```bash
CREATE_RESPONSE=$(curl -sS -X POST "$BASE/skill-runs" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $ADMIN_KEY" \
  -d '{
    "task": "Create a local demo approval request for posting a safe GitHub issue comment. Use fake/default execution only. Do not use live GitHub.",
    "proposer_mode": "fake",
    "requested_skill_id": "post_github_issue_comment"
  }')
printf '%s\n' "$CREATE_RESPONSE"
APPROVAL_ID=$(printf '%s' "$CREATE_RESPONSE" | uv run python -c 'import json, sys; print(json.load(sys.stdin)["run_id"])')
printf 'APPROVAL_ID=%s\n' "$APPROVAL_ID"
```

List approvals and inspect the selected approval:

```bash
curl -sS -H "X-API-Key: $OPERATOR_KEY" "$BASE/operator/approvals"
curl -sS -H "X-API-Key: $OPERATOR_KEY" "$BASE/operator/approvals/$APPROVAL_ID"
```

View status and audit before approval:

```bash
curl -sS -H "X-API-Key: $OPERATOR_KEY" "$BASE/operator/approvals/$APPROVAL_ID/status"
curl -sS -H "X-API-Key: $OPERATOR_KEY" "$BASE/operator/approvals/$APPROVAL_ID/audit"
```

Prove viewer cannot approve:

```bash
curl -i -sS -X POST "$BASE/operator/approvals/$APPROVAL_ID/approve" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $VIEWER_KEY" \
  -d '{"decision_reason": "Viewer should not be allowed to approve."}'
```

Approve as operator:

```bash
APPROVE_RESPONSE=$(curl -sS -X POST "$BASE/operator/approvals/$APPROVAL_ID/approve" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $OPERATOR_KEY" \
  -d '{"decision_reason": "Approved for the local demo."}')
printf '%s\n' "$APPROVE_RESPONSE"
SIDE_EFFECT_ID=$(printf '%s' "$APPROVE_RESPONSE" | uv run python -c 'import json, sys; print(json.load(sys.stdin).get("side_effect_id") or "")')
printf 'SIDE_EFFECT_ID=%s\n' "$SIDE_EFFECT_ID"
```

View status, audit, and side-effect/ledger visibility after approval:

```bash
curl -sS -H "X-API-Key: $OPERATOR_KEY" "$BASE/operator/approvals/$APPROVAL_ID/status"
curl -sS -H "X-API-Key: $OPERATOR_KEY" "$BASE/operator/approvals/$APPROVAL_ID/audit"
curl -sS -H "X-API-Key: $OPERATOR_KEY" "$BASE/operator/side-effects/$SIDE_EFFECT_ID"
```

Open the browser workbench:

```text
http://127.0.0.1:8000/operator/workbench
```

Paste `operator-dev-key`, refresh approvals, and select the run. After approval,
the inbox no longer lists the run as pending; use the status, audit, and
side-effect commands above to inspect terminal evidence.

`POST /skill-runs` is limited to 5 creates per 60 seconds per
identity/route group. If a local demo returns `429`, wait for the
`Retry-After` value or restart the local dev server.

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
