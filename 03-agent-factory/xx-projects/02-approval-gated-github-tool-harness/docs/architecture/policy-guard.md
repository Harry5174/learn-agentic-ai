# Policy Guard Design

## Purpose
The policy guard is deterministic and LLM-free. It provides strict authorization mapping.

## Current Design
```python
evaluate_tool_permission(identity, tool)
→ PolicyDecision
```

## Rules
- LOW/MEDIUM with required scopes → ALLOW
- LOW/MEDIUM missing scopes → DENY
- HIGH risk eligible identity → REQUIRE_APPROVAL
- HIGH risk ineligible identity → DENY

## Approval Eligibility
- Operator may request approval for high-risk tools because it has `approval:request`.
- Admin has broad scopes but still requires approval.
- Viewer cannot request high-risk approval.

## Boundary
- Policy guard does not execute tools.
- Policy guard does not create approval workflow.
- Policy guard does not call LLM.
- Policy guard does not import FastAPI or LangGraph.
- Policy guard does not inspect request bodies.
- Policy guard does not trust client-supplied identity.

## Contract
Input:

- server-derived `IdentityContext`
- controlled `ToolSpec`

Output:

- `ALLOW`
- `DENY`
- `REQUIRE_APPROVAL`

High-risk tools never return direct `ALLOW`; eligible identities receive `REQUIRE_APPROVAL`.
