# Skill Runner API Demo Walkthrough

This walkthrough is for Artifact 2.1, the local/demo skill-runner API surface.

The demo principle is:

```text
The LLM/proposer proposes.
The harness validates, authorizes, approval-gates, executes, and audits.
```

The default HTTP API uses fake proposer mode. If `proposer_mode` is omitted,
`POST /skill-runs` defaults to `fake`.

HTTP `proposer_mode: "llm"` is intentionally disabled and returns `400 Bad
Request` without calling a live model provider. The real `LLMProposer` boundary
exists internally and is tested with mocked clients only.

## Run The Local API

```bash
uv run uvicorn app.api.main:app --reload
```

Base URL:

```text
http://127.0.0.1:8000
```

Demo API keys:

- `viewer-dev-key`
- `operator-dev-key`
- `admin-dev-key`

These are static local/demo credentials.

## List Registered Skills

```bash
curl -s http://127.0.0.1:8000/skills
```

This returns safe public skill metadata:

- skill IDs
- versions
- names and descriptions
- required scopes
- risk levels
- step metadata

It does not expose callables, registry internals, graph state, checkpointer
state, or tool implementation objects.

## Create A Low-Risk Skill Run

```bash
curl -s -X POST http://127.0.0.1:8000/skill-runs \
  -H "Content-Type: application/json" \
  -H "X-API-Key: viewer-dev-key" \
  -d '{"task": "Inspect sandbox health.", "proposer_mode": "fake"}'
```

Expected behavior:

- the fake proposer creates a structured proposal
- the validator accepts the registered low-risk skill
- policy allows the server-derived viewer identity
- the dry-run inspection tool executes
- the run completes

Representative response fields:

```json
{
  "status": "completed",
  "proposer_mode": "fake",
  "selected_skill_id": "inspect_sandbox_health",
  "validation_status": "accepted",
  "approval_required": false,
  "approval_status": "not_required",
  "risk_level": "low",
  "validation": {
    "status": "accepted",
    "argument_validation_status": "accepted",
    "validated_argument_names": {
      "inspect_issues": ["repository"]
    },
    "redacted_argument_names": {
      "inspect_issues": []
    },
    "argument_validation_issue_codes": []
  },
  "execution": {
    "attempted_step_count": 1,
    "completed_step_count": 1,
    "tool_names": ["inspect_sandbox_issues"],
    "dry_run": true
  }
}
```

Save the returned `run_id` for the next examples.

## Get A Skill Run

```bash
curl -s http://127.0.0.1:8000/skill-runs/RUN_ID
```

The summary is safe for clients. It does not expose identity objects, approval
actor objects, checkpointer internals, graph objects, or step argument stores.
It exposes argument-validation status, argument names, redaction names, and
issue codes rather than raw rejected argument values.

## Get Skill Run Audit

```bash
curl -s http://127.0.0.1:8000/skill-runs/RUN_ID/audit
```

The audit response returns JSON-friendly lifecycle evidence. Low-risk runs can
include events for creation, proposal, validation, permission checks, tool
execution, and completion.

## Disabled HTTP LLM Mode

```bash
curl -s -X POST http://127.0.0.1:8000/skill-runs \
  -H "Content-Type: application/json" \
  -H "X-API-Key: viewer-dev-key" \
  -d '{"task": "Inspect sandbox health.", "proposer_mode": "llm"}'
```

Expected response:

```json
{
  "detail": "LLM proposer mode is not enabled for this API."
}
```

This is intentional. Automated tests do not require model credentials, network
access, or live provider calls.

## Invalid Proposal Example

Invalid-proposal behavior is covered by API tests using scenario-configured fake
proposer injection.

The default running HTTP API does not currently expose a public request field
for selecting the invalid fake proposer scenario.

Test-backed behavior:

- an invalid proposal is rejected by `ProposalValidator`
- rejection happens before policy evaluation or tool execution
- the run summary reports `validation_status: "rejected"`
- argument-validation failures report safe issue codes
- execution reports zero attempted and zero completed steps

Representative response fields:

```json
{
  "status": "failed",
  "validation_status": "rejected",
  "validation": {
    "status": "rejected",
    "rejection_reasons": ["tool_not_allowed"]
  },
  "execution": {
    "attempted_step_count": 0,
    "completed_step_count": 0,
    "tool_names": [],
    "dry_run": true
  }
}
```

Evidence:

- `tests/test_api_skill_runs.py::test_invalid_proposal_is_rejected_before_execution_through_http`
- `tests/test_adversarial_argument_validation.py::test_raw_rejected_values_are_absent_from_api_response_and_audit`

## High-Risk Approval Example

High-risk approval behavior is covered by API tests using scenario-configured
fake proposer injection.

The default running HTTP API does not currently expose a public request field
for selecting the high-risk fake proposer scenario.

Test-backed pause behavior:

- the proposer selects `simulate_sandbox_workflow`
- validation accepts the registered high-risk skill
- policy returns an approval-required decision
- the run pauses with `status: "paused_for_approval"`
- no high-risk dry-run tool executes before approval

Representative paused response fields:

```json
{
  "status": "paused_for_approval",
  "selected_skill_id": "simulate_sandbox_workflow",
  "validation_status": "accepted",
  "approval_required": true,
  "approval_status": "pending",
  "risk_level": "high",
  "execution": {
    "attempted_step_count": 0,
    "completed_step_count": 0,
    "tool_names": [],
    "dry_run": true
  }
}
```

When a paused high-risk run exists, approval uses server-derived identity:

```bash
curl -s -X POST http://127.0.0.1:8000/skill-runs/RUN_ID/approve \
  -H "Content-Type: application/json" \
  -H "X-API-Key: admin-dev-key" \
  -d '{"reason": "Approved for dry-run workflow simulation.", "comment": "Reviewed for the local demo."}'
```

Representative approved response fields:

```json
{
  "status": "completed",
  "approval_status": "approved",
  "execution": {
    "attempted_step_count": 1,
    "completed_step_count": 1,
    "tool_names": ["trigger_workflow_dry_run"],
    "dry_run": true
  }
}
```

Evidence:

- `tests/test_api_skill_runs.py::test_high_risk_skill_run_is_observable_in_approval_required_state`
- `tests/test_api_skill_runs.py::test_approve_skill_run_resumes_and_executes_dry_run_tool`

## High-Risk Rejection Example

When a paused high-risk run exists, rejection uses server-derived identity:

```bash
curl -s -X POST http://127.0.0.1:8000/skill-runs/RUN_ID/reject \
  -H "Content-Type: application/json" \
  -H "X-API-Key: admin-dev-key" \
  -d '{"reason": "Rejected during dry-run review.", "comment": "Do not run this workflow."}'
```

Test-backed behavior:

- rejection finalizes the run
- the pending high-risk dry-run tool does not execute
- execution reports zero attempted and zero completed steps

Representative rejected response fields:

```json
{
  "status": "rejected",
  "approval_status": "rejected",
  "execution": {
    "attempted_step_count": 0,
    "completed_step_count": 0,
    "tool_names": [],
    "dry_run": true
  }
}
```

Evidence:

- `tests/test_api_skill_runs.py::test_reject_skill_run_prevents_dry_run_tool_execution`

## High-Risk Audit Example

Approved high-risk audit behavior is covered by API tests using
scenario-configured fake proposer injection.

Expected event types include:

- `task_created`
- `tool_selected`
- `permission_checked`
- `approval_requested`
- `approval_granted`
- `tool_executed`
- `task_completed`

Rejected high-risk runs should include rejection evidence and should not include
a high-risk `tool_executed` event.

Evidence:

- `tests/test_api_skill_runs.py::test_get_skill_run_audit_returns_lifecycle_evidence`

## Current Demo Limits

- process-local skill-run state
- in-memory checkpoints
- in-memory audit events
- in-memory rate limits
- dry-run tools only
- default HTTP API uses fake proposer mode
- HTTP `llm` mode is disabled and rejected
- model-proposed runtime tool arguments are scalar-only in Artifact 2.2 V1
- object/list/nested arguments are unsupported
- partial acceptance is unsupported
- no MCP
- no OAuth/OIDC
- no database persistence
- no real GitHub writes
- no frontend
