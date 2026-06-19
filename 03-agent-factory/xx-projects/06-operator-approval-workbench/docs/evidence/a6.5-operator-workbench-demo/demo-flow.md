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
