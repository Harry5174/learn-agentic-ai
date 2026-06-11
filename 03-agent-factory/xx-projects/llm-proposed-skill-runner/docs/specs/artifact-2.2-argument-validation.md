# Artifact 2.2 Argument Validation

## Artifact Version Goal

Artifact 2.2 adds the argument contract and validation boundary needed for
model-proposed runtime tool arguments.

Sprint E2.0 defined schema stubs and safety rules. Sprint E2.1 implemented
deterministic validator argument checks and produced a trusted
`ValidatedSkillPlan`. Sprint E2.2 wires accepted `ValidatedSkillPlan` arguments
into graph/tool execution.

Artifact 2.2 still has E2.3 adversarial suite and documentation follow-up
remaining before the artifact should be marked complete.

## Problem Statement

Artifact 2 already treats model-shaped skill proposals as untrusted input. The
next missing boundary is runtime tool arguments.

The rule for Artifact 2.2 is:

```text
The LLM may propose arguments.
Only validator-approved arguments may execute.
```

## Current Artifact 2.1 Limitation

Artifact 2.1 exposes the skill-runner lifecycle through the local/demo API and
executes registered dry-run tools through the harness.

Skill specs now include trusted `ToolArgumentSpec` metadata, and
`SkillProposalStep` can carry untrusted proposed arguments. Runtime arguments
proposed by a model are validated into `ValidatedSkillPlan`, and Sprint E2.2
wires accepted validated arguments into dry-run execution. Raw proposed
arguments do not execute directly.

## Trusted, Untrusted, And Validated Boundary

Artifact 2.2 separates argument data into three categories:

- Untrusted: raw proposer output, including `SkillProposalStep.arguments`.
- Trusted: static registry metadata such as skill ids, step ids, tool names,
  required scopes, risk levels, and `ToolArgumentSpec` metadata.
- Validated: scalar argument values accepted by deterministic validation.

The proposer cannot decide identity, role, scopes, policy, approval, tool
selection, skill version trust, risk level, or execution authority.

## Raw Argument Non-Execution Rule

Raw proposed arguments must never flow directly into `ToolRegistry.execute()`.

The E2.1 validator flow is:

```text
SkillProposal raw arguments
-> ProposalValidator
-> ValidatedSkillPlan
```

The E2.2 execution-wiring flow starts from `ValidatedSkillPlan`.

## Schema Concepts

Sprint E2.0 introduces these contract concepts:

- `ArgumentValueType`: V1 scalar type names.
- `ArgumentValidationStatus`: accepted or rejected only.
- `ToolArgumentSpec`: trusted metadata for one allowed argument.
- `SkillProposalStep.arguments`: raw untrusted proposed argument payload for a
  step.
- `ProposedStepArguments`: standalone contract shape for raw step arguments.
- `ValidatedStepArguments`: validator-approved scalar values for a step.
- `ArgumentValidationIssue`: safe rejection metadata without raw payload echo.
- `ValidatedSkillPlan`: future validator output for accepted or rejected
  argument plans.
- `FORBIDDEN_ARGUMENT_NAMES`: central denylist for identity and control-plane
  fields.

## ValidatedSkillPlan Shape

`ValidatedSkillPlan` is the boundary object produced by deterministic argument
validation. Sprint E2.2 makes it the graph execution argument source.

The planned shape is:

```text
status: accepted | rejected
skill_id: string
skill_version: string
step_arguments: list of ValidatedStepArguments
issues: list of ArgumentValidationIssue
```

An accepted plan may contain validated step arguments. A rejected plan may
contain safe reason codes and messages. V1 has no partial acceptance state.

## V1 Supported Types

Artifact 2.2 V1 supports only scalar argument values:

- string
- integer
- boolean

These types are intentionally small so validation can fail closed and stay
auditable.

## Deferred Types

The following are deferred:

- object payloads
- list payloads
- nested payloads
- arbitrary JSON blobs
- dynamic per-tool schema engines

Future support for those shapes should be explicit and test-backed.

## Forbidden Argument Names

Arguments cannot claim identity, authorization, approval, policy, risk, tool
selection, or skill selection.

The central forbidden-name set includes at least:

```text
user_id
role
roles
scope
scopes
identity
api_key
api_token
approval_authority
approval_decision
policy_decision
policy_override
risk_override
risk_level
requires_approval
tool_name
tool_id
selected_tool
skill_id
skill_version
```

The E2.1 validator rejects proposals containing these argument names.

## Redaction Policy

Non-sensitive validated argument values may appear in local/demo audit output.

Arguments marked `sensitive=True` must be replaced with `[REDACTED]` in audit
output and public API summaries.

Rejected raw argument values should not be echoed back by default.

Audit and API output may include argument names and reason codes, but should not
leak raw rejected payloads.

Sprint E2.1 tracks sensitive accepted argument names in
`ValidatedStepArguments.redacted_argument_names`. Sprint E2.2 exposes safe
argument-validation summaries in audit/API output without exposing raw rejected
payloads or sensitive values.

## Existing Dry-Run Tool Argument Audit

`inspect_sandbox_issues`

- Current harness-owned/default arguments: `repository = "sandbox/demo-repo"`.
- Likely future model-proposed argument: `repository`.
- V1 type: string.
- Likely status: optional because the dry-run tool has a safe default.
- Sensitive: false.

`draft_issue_comment`

- Current harness-owned/default arguments: `issue_id = 1`,
  `comment_body = "Draft response generated by skill graph."`.
- Likely future model-proposed arguments: `issue_id`, `comment_body`.
- V1 types: integer and string.
- Likely status: required in a future validator contract for meaningful drafts.
- Sensitive: false by default, with future support for sensitive comment-like
  fields if needed.

`trigger_workflow_dry_run`

- Current harness-owned/default arguments: `workflow_name = "ci.yml"`,
  `ref = "main"`.
- Likely future model-proposed arguments: `workflow_name`, `ref`.
- V1 types: string and string.
- Likely status: required in a future validator contract for high-risk work.
- Sensitive: false.

Argument validity is not authorization. Scope checks and approval gates remain
harness decisions.

## Sprint E2.1 Validator Behavior

Sprint E2.1 wires the argument schema contract into deterministic proposal
validation.

Implemented validator behavior:

- compare proposed arguments against trusted skill/tool metadata
- reject unknown argument names
- reject forbidden argument names
- reject unsupported value types
- reject missing required arguments
- reject malformed scalar values without coercion
- reject invalid allowed values
- reject overlong strings
- reject invalid trusted argument specs
- produce a `ValidatedSkillPlan`
- avoid echoing raw rejected values in public or audit-facing summaries
- reject the proposal on any argument issue without partial acceptance

## Sprint E2.2 Execution Wiring

Sprint E2.2 updates execution wiring so tools receive only validator-approved
arguments.

The graph should continue to preserve these boundaries:

- proposal before validation
- validation before policy
- policy before approval or execution
- approval before high-risk execution
- execution through registered dry-run tools only

Implemented E2.2 behavior:

- graph validation acceptance requires an accepted `ValidatedSkillPlan`
- policy and approval requests use validated step arguments
- `ToolRegistry.execute()` receives validator-approved arguments
- missing accepted validated arguments fail closed
- raw proposal arguments are not read by execution
- audit/API summaries expose safe argument-validation evidence only

## Planned Sprint E2.3 Adversarial Suite

Sprint E2.3 should add adversarial tests for argument-level attacks:

- identity or scope smuggling
- tool-name override attempts
- skill-id or skill-version override attempts
- risk or approval override attempts
- unknown argument names
- unsupported payload shapes
- raw rejected payload leakage
- high-risk execution without approval

## Strict Non-Goals

Artifact 2.2 does not add:

- live LLM HTTP mode
- MCP
- OAuth/OIDC
- JWT validation
- database persistence
- frontend
- deployment
- GitHub write operations
- real workflow triggers
- multi-agent behavior
- dynamic tool registration
- new dependencies
- new scripts

Sprint E2.2 does not change:

- `ToolRegistry` behavior
- proposer behavior
- policy behavior
- approval behavior

## Acceptance Definition For Artifact 2.2

Artifact 2.2 is accepted only when:

- raw proposed arguments cannot execute
- argument validation fails closed
- V1 scalar support is deterministic and test-backed
- forbidden control-plane fields are rejected
- only accepted validated arguments can reach tool execution
- audit and public summaries avoid leaking rejected raw payloads
- existing local/demo dry-run boundaries remain intact

Sprint E2.1 satisfies the deterministic validator-check slice of that
definition. Sprint E2.2 satisfies the execution-wiring slice. E2.3 adversarial
suite and documentation follow-up still remain before Artifact 2.2 should be
marked complete.
