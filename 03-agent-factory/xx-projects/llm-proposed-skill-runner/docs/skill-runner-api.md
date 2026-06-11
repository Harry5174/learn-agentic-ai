# Skill Runner API Contract

## Status

Sprint E1.1 implemented the first public FastAPI surface for Artifact 2.1:

- `GET /skills`
- `POST /skill-runs`

Sprint E1.2 implemented the remaining public skill-run lifecycle routes:

- `GET /skill-runs/{run_id}`
- `POST /skill-runs/{run_id}/approve`
- `POST /skill-runs/{run_id}/reject`
- `GET /skill-runs/{run_id}/audit`

The skill-runner API must preserve the Artifact 2 invariant:

```text
The LLM proposes.
The harness validates, authorizes, approval-gates, executes, and audits.
```

Clients may submit task text and optional proposer preferences, but identity,
policy, approval authority, tool trust, and execution remain server-side harness
concerns.

Sprint E1.3 documents the completed Artifact 2.1 API/demo surface. It does not
change runtime behavior.

## Implemented In E1.1

```text
GET  /skills
POST /skill-runs
```

## Implemented In E1.2

```text
GET  /skill-runs/{run_id}
POST /skill-runs/{run_id}/approve
POST /skill-runs/{run_id}/reject
GET  /skill-runs/{run_id}/audit
```

## Demo Surface In E1.3

The default HTTP API can demonstrate:

- `GET /skills`
- low-risk `POST /skill-runs`
- `GET /skill-runs/{run_id}`
- `GET /skill-runs/{run_id}/audit`
- disabled `proposer_mode: "llm"` returning `400 Bad Request`

Invalid proposal, high-risk approval, high-risk rejection, and approved
high-risk audit behavior are covered by API tests using scenario-configured fake
proposer injection. The default running HTTP API does not currently expose a
public request field for selecting those fake proposer scenarios.

See [skill-runner-demo.md](skill-runner-demo.md) for curl-oriented walkthroughs.

## Authentication And Identity

Skill-run creation, approval, and rejection use the existing server-derived
identity boundary. Clients must send identity through the configured
authentication mechanism, not through JSON request bodies.

Request bodies must not accept:

- `user_id`
- `role`
- `scopes`
- `identity`
- `api_key`
- `api_key_id`
- `policy_decision`
- `approval_decision`
- `risk_override`
- `trusted_tool_names`
- `approval_authority`

Identity, role, scopes, API key ID, rate-limit keys, and approval authority are
server-derived.

## Shared Schemas

### SkillStepSummaryResponse

```json
{
  "step_id": "inspect_issues",
  "description": "Inspect sandbox issues using dry-run data.",
  "tool_name": "inspect_sandbox_issues",
  "risk_level": "low",
  "required_scopes": ["tools:inspect"]
}
```

This response exposes safe step metadata only. It does not expose callables,
handlers, implementation objects, graph state, or tool execution functions.

### SkillSummaryResponse

```json
{
  "skill_id": "inspect_sandbox_health",
  "version": "1.0",
  "name": "Inspect sandbox health",
  "description": "Inspect predictable sandbox issue status data.",
  "required_scopes": ["tools:inspect"],
  "risk_level": "low",
  "steps": []
}
```

### SkillRunCreateRequest

```json
{
  "task": "Inspect sandbox health.",
  "proposer_mode": "fake",
  "requested_skill_id": "inspect_sandbox_health"
}
```

Allowed `proposer_mode` values:

- `fake`
- `llm`

In E1.1, omitted `proposer_mode` defaults to `fake`. `proposer_mode: "fake"`
uses the existing deterministic fake proposer through `SkillGraphService`.
`proposer_mode: "llm"` is disabled at the HTTP layer and returns a safe `400`
response without calling a live model provider.

`requested_skill_id` is accepted in the request schema for the API-facing
contract, but the current HTTP route delegates to the configured proposer. It
does not currently select fake proposer scenarios or force a specific skill from
curl.

### SkillRunSummaryResponse

```json
{
  "run_id": "run-123",
  "status": "paused_for_approval",
  "task": "Simulate sandbox workflow.",
  "proposer_mode": "fake",
  "selected_skill_id": "simulate_sandbox_workflow",
  "selected_skill_version": "1.0",
  "validation_status": "accepted",
  "approval_required": true,
  "approval_status": "pending",
  "risk_level": "high",
  "final_report": null,
  "error_message": null,
  "created_at": "2026-06-11T00:00:00Z",
  "updated_at": "2026-06-11T00:00:00Z",
  "proposal": null,
  "validation": null,
  "execution": null
}
```

The response is a public summary. It must not expose raw graph state,
checkpointer state, LangGraph objects, server-derived identity objects,
approval actors, or internal step argument stores.

Current E1.2 limitation: read, approval, and rejection responses report
`proposer_mode: "fake"` because the HTTP layer only supports fake proposer mode
and the in-memory graph state does not persist proposer mode separately.

### SkillRunApprovalRequest

```json
{
  "reason": "Approved for dry-run execution.",
  "comment": "Reviewed for the local demo."
}
```

Approval and rejection request bodies carry explanation text only. The approving
or rejecting identity is derived server-side.

### SkillRunAuditResponse

```json
{
  "run_id": "run-123",
  "events": [
    {
      "event_type": "proposal_validated",
      "timestamp": "2026-06-11T00:00:00Z",
      "message": "Proposal was accepted.",
      "metadata": {
        "risk_level": "low",
        "approval_required": false
      }
    }
  ]
}
```

Audit event metadata must be JSON-friendly. The audit response must not expose
non-serializable objects, callables, graph internals, checkpointer internals, or
stack traces.

### SkillRunErrorResponse

```json
{
  "error_code": "skill_run_not_found",
  "message": "Skill run not found.",
  "details": {
    "run_id": "run-123"
  }
}
```

Error responses should be stable and safe for clients. They must not expose
Python stack traces, internal exception objects, checkpointer payloads, or raw
graph state.

## GET /skills

Status: implemented in E1.1.

Purpose: list public metadata for registered skills.

Request body: none.

Response shape:

```json
[
  {
    "skill_id": "inspect_sandbox_health",
    "version": "1.0",
    "name": "Inspect sandbox health",
    "description": "Inspect predictable sandbox issue status data.",
    "required_scopes": ["tools:inspect"],
    "risk_level": "low",
    "steps": []
  }
]
```

Identity handling: this E1.1 endpoint is public like `GET /tools`. The response
does not trust request body identity because this endpoint has no request body.

Approval handling: none. Listing skills does not approve, reject, or execute
anything.

Errors:

- `500 Internal Server Error` with `SkillRunErrorResponse` shape for unexpected
  server failures

Default curl behavior: with the current app configuration, fake proposer mode
creates the low-risk `inspect_sandbox_health` proposal. Other fake proposer
scenarios are exercised by tests using scenario-configured service injection.

## POST /skill-runs

Status: implemented in E1.1.

Purpose: create a new skill run from user task text.

Request shape:

```json
{
  "task": "Inspect sandbox health.",
  "proposer_mode": "fake",
  "requested_skill_id": "inspect_sandbox_health"
}
```

Response shape: `SkillRunSummaryResponse`.

Identity handling: identity is resolved server-side. The request body cannot
claim user ID, role, scopes, API key, API key ID, policy decision, approval
decision, approval authority, risk override, or trusted tool names.

Proposer handling: omitted `proposer_mode` defaults to `fake`. `fake` delegates
to the existing `SkillGraphService` default proposer. `llm` returns `400`
without invoking a provider or service run.

Validation and execution handling: the route delegates to
`SkillGraphService.start_run`. Proposal validation, policy checks, approval
gating, dry-run execution, and audit behavior remain in the existing service and
graph layers.

Approval handling: if the validated proposal requires high-risk approval, the
route returns a paused summary with `approval_required: true` and
`approval_status: "pending"`. It does not execute high-risk tools before
approval.

Errors:

- `400 Bad Request` when `proposer_mode: "llm"` is requested but not enabled
- `422 Unprocessable Entity` for invalid request shape or forbidden body fields
- `401 Unauthorized` for missing or invalid identity
- `429 Too Many Requests` for server-derived rate-limit overflow
- `500 Internal Server Error` with `SkillRunErrorResponse` shape for unexpected
  server failures

## GET /skill-runs/{run_id}

Status: implemented in E1.2.

Purpose: fetch the current public summary for one skill run.

Request body: none.

Response shape: `SkillRunSummaryResponse`.

Identity handling: this local/demo read endpoint does not accept request body
identity, role, or scopes.

Approval handling: paused runs may include public approval status, but should
not expose approval actor identity objects or internal approval checkpoint data.

Errors:

- `404 Not Found` if the run ID is unknown

## POST /skill-runs/{run_id}/approve

Status: implemented in E1.2.

Purpose: approve and resume a paused high-risk skill run.

Request shape:

```json
{
  "reason": "Approved for dry-run execution.",
  "comment": "Reviewed for the local demo."
}
```

Response shape: `SkillRunSummaryResponse`.

Identity handling: approval authority comes from server-derived identity. The
request body cannot claim approver ID, role, scopes, approval authority, policy
override, or approval decision.

Approval handling: approval is only valid for a run paused for approval. Approval
does not bypass deterministic validation, policy checks, or dry-run tool
boundaries.

If the server-derived identity lacks the required approval scope, the existing
graph/service boundary returns a failed run summary without executing tools.

Errors:

- `400 Bad Request` for invalid request shape
- `401 Unauthorized` for missing or invalid identity
- `404 Not Found` if the run ID is unknown
- `409 Conflict` if the run is not paused for approval
- `429 Too Many Requests` for server-derived rate-limit overflow

## POST /skill-runs/{run_id}/reject

Status: implemented in E1.2.

Purpose: reject and finalize a paused high-risk skill run without executing the
pending high-risk tool action.

Request shape:

```json
{
  "reason": "Rejected during review.",
  "comment": "Do not run this workflow."
}
```

Response shape: `SkillRunSummaryResponse`.

Identity handling: rejection authority comes from server-derived identity. The
request body cannot claim rejector ID, role, scopes, approval authority, policy
override, or approval decision.

Approval handling: rejection is only valid for a run paused for approval. A
rejected run should not execute the pending high-risk tool action.

If the server-derived identity lacks the required rejection scope, the existing
graph/service boundary returns a failed run summary without executing tools.

Errors:

- `400 Bad Request` for invalid request shape
- `401 Unauthorized` for missing or invalid identity
- `404 Not Found` if the run ID is unknown
- `409 Conflict` if the run is not paused for approval
- `429 Too Many Requests` for server-derived rate-limit overflow

## GET /skill-runs/{run_id}/audit

Status: implemented in E1.2.

Purpose: return a safe public audit trail for one skill run.

Request body: none.

Response shape: `SkillRunAuditResponse`.

Identity handling: this local/demo audit endpoint does not accept request body
identity, role, scopes, or API key ID.

Approval handling: audit events may describe approval requested, granted, or
rejected events, but must not expose raw approval actor identity objects or
checkpoint resume payloads.

Errors:

- `404 Not Found` if the run ID is unknown

## Non-Implementation Statement

Sprint E1.3 does not add graph behavior, service behavior, proposer behavior,
validator behavior, policy behavior, approval semantics, tool behavior,
persistence, frontend behavior, MCP, OAuth/OIDC, JWT validation, database
support, real GitHub writes, real workflow triggers, real LLM calls, provider
frameworks, or model-proposed tool argument validation.
