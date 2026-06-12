# Sprint 3: Deterministic Policy Guard

## Objective
Implement pure deterministic authorization logic over IdentityContext and ToolSpec.

## Core Contract
IdentityContext + ToolSpec → PolicyDecision

## Scope
- evaluate_tool_permission
- missing-scope behavior
- high-risk approval requirement
- viewer/operator/admin policy tests

## Non-Goals
- graph routing
- approval service
- FastAPI
- OAuth/OIDC
- JWT validation
- database
- LLM calls
- tool execution

## Expected Decisions

**Viewer:**
- inspect_sandbox_issues → ALLOW
- draft_issue_comment → DENY
- trigger_workflow_dry_run → DENY

**Operator:**
- inspect_sandbox_issues → ALLOW
- draft_issue_comment → ALLOW
- trigger_workflow_dry_run → REQUIRE_APPROVAL

**Admin:**
- inspect_sandbox_issues → ALLOW
- draft_issue_comment → ALLOW
- trigger_workflow_dry_run → REQUIRE_APPROVAL

## High-Risk Rule
High-risk tools never return ALLOW.
They return REQUIRE_APPROVAL when eligible or DENY when not eligible.

## Admin Rule
Admin does not bypass approval.

## LLM Boundary
No LLM authorization is involved. The policy guard uses only the server-derived `IdentityContext` and the controlled `ToolSpec`.

## Output Contract
The policy guard returns one of:

- `ALLOW`
- `DENY`
- `REQUIRE_APPROVAL`

High-risk tools never return direct `ALLOW`. They require approval when the identity is eligible, or return `DENY` when it is not.
