# Adversarial Argument Validation

This note documents the Artifact 2.2 E2.3 adversarial boundary suite.

Artifact 2.2 proves this local/demo claim:

```text
A model-shaped SkillProposal can include runtime tool arguments,
but only registry-declared, scalar, validator-normalized arguments can reach
dry-run execution.
```

Unsafe, malformed, unknown, or control-plane arguments are rejected and audited
with safe evidence.

## Boundary Model

The argument boundary has three categories.

Untrusted:

- `SkillProposalStep.arguments`
- proposer output from fake, mocked, or future model-backed proposers
- any field names or values that try to influence identity, policy, approval,
  tool selection, or skill selection

Trusted:

- `SkillRegistry`
- `SkillSpec` and `SkillStep`
- `ToolArgumentSpec`
- registered dry-run `ToolRegistry` metadata
- server-derived `IdentityContext`

Validated:

- `ValidatedSkillPlan`
- `ValidatedStepArguments`
- scalar values accepted by `ProposalValidator`

The graph treats `ValidatedSkillPlan` as the only argument source for policy,
approval request context, and dry-run tool execution.

## Supported V1 Argument Shapes

Artifact 2.2 V1 supports only:

- string
- integer
- boolean

Validation does not coerce values. For example, `"1"` is not accepted for an
integer field, and `true` is not accepted for an integer field.

## Rejected Argument Attacks

The E2.3 adversarial suite covers:

- unknown argument names
- missing required arguments
- wrong scalar types
- bool values for integer fields
- string integers for integer fields
- overlong strings
- values outside trusted `allowed_values`
- object payloads
- list payloads

Any issue rejects the full proposed argument plan. There is no partial
acceptance state.

## Control-Plane Smuggling

Proposed arguments cannot claim harness authority.

The suite verifies rejection for control-plane names including:

- `user_id`
- `role`
- `roles`
- `scope`
- `scopes`
- `identity`
- `api_key`
- `api_token`
- `approval_authority`
- `approval_decision`
- `policy_decision`
- `policy_override`
- `risk_override`
- `risk_level`
- `requires_approval`
- `tool_name`
- `tool_id`
- `skill_id`
- `skill_version`

These are argument-name checks. They do not rely on prompt wording or model
cooperation.

## Raw Argument Non-Execution

Raw proposed arguments must never flow directly into `ToolRegistry.execute()`.

The E2.3 tests verify:

- trusted defaults from `ToolArgumentSpec` can be used when the raw proposal
  omits an optional argument
- forbidden arguments do not reach tool execution
- unknown arguments do not reach tool execution
- invalid argument proposals reject before policy or tool execution
- a missing accepted validated step fails closed

The graph calls `ToolRegistry.execute()` only after it has an accepted
`ValidatedSkillPlan` whose skill id and version match the validated skill.

## Audit And API Evidence

Audit and public API summaries expose safe argument-validation evidence:

- argument validation status
- validated argument names
- redacted argument names
- issue reason codes

Rejected raw values are not echoed in API responses or audit responses.

Sensitive accepted values are summarized by argument name only when trusted
metadata marks an argument as sensitive. The value may reach the dry-run tool if
it is valid, but public summaries and audit validation metadata do not expose
the sensitive value.

## Approval Preservation

Argument validation does not replace approval.

The E2.3 suite verifies:

- a high-risk workflow proposal with valid arguments still pauses before
  execution
- approval resumes the run and executes with validated arguments
- rejection finalizes without execution
- a proposed `approval_decision` argument is rejected instead of bypassing the
  approval gate

Authorization and approval remain harness decisions.

## Deferred Work

Artifact 2.2 does not support:

- object arguments
- list arguments
- nested object validation
- arbitrary JSON payloads
- partial acceptance
- dynamic schema engines
- external side-effecting tool adapters

Future support for richer payloads should be explicit, threat-modeled, and
covered by a new adversarial suite.
