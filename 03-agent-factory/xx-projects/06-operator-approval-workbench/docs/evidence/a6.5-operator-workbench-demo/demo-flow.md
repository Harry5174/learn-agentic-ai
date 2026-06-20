# Demo Flow

## Operator Story

Artifact 06 turns the approval-gated agent harness into a local operator
workbench.

1. A proposed action appears in the approval inbox.
2. The operator opens the approval detail.
3. The operator reviews task, risk, required scopes, policy status, target
   context, `side_effect_id`, `args_hash`, and fake/default execution mode.
4. The operator approves or rejects through an A6 operator route.
5. The backend derives actor identity from server-side identity resolution.
6. The operator refreshes status.
7. The operator inspects decision history, local/demo audit timeline,
   side-effect/ledger visibility, execution result, and known limitations.

## Demo Routes

```text
GET /operator/workbench
GET /operator/approvals
GET /operator/approvals/{approval_id}
GET /operator/approvals/{approval_id}/status
GET /operator/approvals/{approval_id}/audit
GET /operator/side-effects/{side_effect_id}
POST /operator/approvals/{approval_id}/approve
POST /operator/approvals/{approval_id}/reject
```

## Fresh Terminal Demo: Empty Inbox to Approved Run

Start the server:

```bash
uv run app
```

Set local demo variables:

```bash
BASE=http://127.0.0.1:8000
VIEWER_KEY=viewer-dev-key
OPERATOR_KEY=operator-dev-key
ADMIN_KEY=admin-dev-key
```

Verify identities and workbench availability:

```bash
curl -sS -H "X-API-Key: $VIEWER_KEY" "$BASE/identity/me"
curl -sS -H "X-API-Key: $OPERATOR_KEY" "$BASE/identity/me"
curl -sS -H "X-API-Key: $ADMIN_KEY" "$BASE/identity/me"
curl -i -sS "$BASE/operator/workbench" | head
```

Create the pending fake/default GitHub-comment approval:

```bash
CREATE_RESPONSE=$(curl -sS -X POST "$BASE/skill-runs" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $ADMIN_KEY" \
  -d '{
    "task": "Create a local demo approval request for posting a safe GitHub issue comment. Use fake/default execution only. Do not use live GitHub.",
    "proposer_mode": "fake",
    "requested_skill_id": "post_github_issue_comment"
  }')
APPROVAL_ID=$(printf '%s' "$CREATE_RESPONSE" | uv run python -c 'import json, sys; print(json.load(sys.stdin)["run_id"])')
printf '%s\n' "$CREATE_RESPONSE"
```

Inspect pending state:

```bash
curl -sS -H "X-API-Key: $OPERATOR_KEY" "$BASE/operator/approvals"
curl -sS -H "X-API-Key: $OPERATOR_KEY" "$BASE/operator/approvals/$APPROVAL_ID"
curl -sS -H "X-API-Key: $OPERATOR_KEY" "$BASE/operator/approvals/$APPROVAL_ID/status"
curl -sS -H "X-API-Key: $OPERATOR_KEY" "$BASE/operator/approvals/$APPROVAL_ID/audit"
```

Prove viewer cannot approve, then approve as operator:

```bash
curl -i -sS -X POST "$BASE/operator/approvals/$APPROVAL_ID/approve" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $VIEWER_KEY" \
  -d '{"decision_reason": "Viewer should not be allowed to approve."}'

APPROVE_RESPONSE=$(curl -sS -X POST "$BASE/operator/approvals/$APPROVAL_ID/approve" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $OPERATOR_KEY" \
  -d '{"decision_reason": "Approved for the local demo."}')
SIDE_EFFECT_ID=$(printf '%s' "$APPROVE_RESPONSE" | uv run python -c 'import json, sys; print(json.load(sys.stdin).get("side_effect_id") or "")')
printf '%s\n' "$APPROVE_RESPONSE"
```

Inspect terminal evidence:

```bash
curl -sS -H "X-API-Key: $OPERATOR_KEY" "$BASE/operator/approvals/$APPROVAL_ID/status"
curl -sS -H "X-API-Key: $OPERATOR_KEY" "$BASE/operator/approvals/$APPROVAL_ID/audit"
curl -sS -H "X-API-Key: $OPERATOR_KEY" "$BASE/operator/side-effects/$SIDE_EFFECT_ID"
```

Open `http://127.0.0.1:8000/operator/workbench`, paste
`operator-dev-key`, refresh approvals, and inspect the same run from the local
static workbench.

`POST /skill-runs` is limited to 5 creates per 60 seconds per
identity/route group. If `429` occurs, wait for `Retry-After` or restart the
local dev server.

## Safety Checks To Mention

- The operator decision routes use server-derived identity.
- Request bodies cannot claim identity, role, scopes, approval authority,
  repository policy, real-mode enablement, token values, `args_hash`, or
  `side_effect_id` authority.
- Viewer identities may read local/demo visibility but cannot approve or
  reject.
- Stale approval ids and mismatched expected values fail safely.
- Visibility endpoints are read-only.
- The workbench calls only A6 operator routes.
- The workbench does not use browser storage for the pasted local demo key.

## Screenshot Placeholder

No screenshots are included in this evidence package. Capture screenshots later
only after redaction review and explicit approval.
