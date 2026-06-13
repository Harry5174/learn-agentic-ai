# Interview Notes

## One-Minute Summary

Artifact 3 — Approval-Gated GitHub Tool Harness started at A3.0 as a baseline
copy and rename from the finalized Artifact 2.2 project.

A3.1 defines the future real side-effect boundary for an approval-gated GitHub
issue-comment tool. It is still documentation/specification only. Artifact 3
has not implemented real GitHub API execution.

A3.2 adds isolated fake/in-memory supporting boundaries for a GitHub
issue-comment client and side-effect ledger.

A3.3 wires those boundaries into exactly one approval-gated local/demo skill
path named `post_github_issue_comment`. It uses validated scalar arguments,
a trusted repository allowlist, explicit approval, an in-memory side-effect
ledger, and fake-client simulated execution. It still does not call the real
GitHub API.

The core idea is:

```text
The LLM proposes.
The harness validates, authorizes, approval-gates, executes, and audits.
```

The model or fake proposer can suggest a structured `SkillProposal`, but the
harness controls validation, policy, approval, tool execution, and audit.

## Problem Solved

Many agent demos blur together intent, authorization, execution, and
explanation. This project separates those concerns.

The proposer is treated as an untrusted source of possible work. Its output is
validated like an external API request before anything can execute.

## What Artifact 2 Adds Over Artifact 1

Artifact 1 proved the harness foundation with deterministic task
interpretation:

- server-derived identity
- deterministic policy
- approval gate
- dry-run tools
- audit trail
- checkpointed resume

Artifact 2 adds:

- explicit skill contracts
- model-shaped `SkillProposal`
- deterministic `ProposalValidator`
- trusted `SkillRegistry`
- fake proposer scenarios
- optional mocked LLM proposer boundary
- skill execution graph
- validated model-proposed scalar tool arguments

The important design move is that adding a proposer does not give the model
authority.

## Why The Model Is Not Trusted

The model may hallucinate:

- a skill
- a tool
- a lower risk level
- missing required steps
- malformed JSON
- unsupported versions

The harness rejects those cases before policy evaluation or tool execution.

## Why ProposalValidator Exists

`ProposalValidator` checks untrusted proposals against trusted registry
metadata.

It validates:

- known skill ID
- supported skill version
- non-empty steps
- duplicate step IDs
- known registered steps
- allowed tool names
- required scopes
- risk consistency
- registry-declared scalar runtime arguments
- forbidden identity, policy, approval, risk, tool, and skill argument names

It derives final risk and approval requirement from registry metadata, not from
the model.

## What Artifact 2.2 Adds

Artifact 2.2 added validated model-proposed tool arguments and adversarial
boundary tests.

It lets a model-shaped proposal include runtime tool arguments while keeping
execution authority in the harness.

The validator accepts only registry-declared scalar arguments. Unknown,
missing, wrong-type, overlong, forbidden control-plane, object, and list
arguments are rejected. Accepted arguments are placed into `ValidatedSkillPlan`,
and the graph reads that plan for policy context, approval request arguments,
and dry-run execution.

Raw proposed arguments do not flow directly into `ToolRegistry.execute()`.

## What A3.0 Adds

A3.0 creates the Artifact 3 project identity and folder from the completed
Artifact 2.2 baseline.

It does not change runtime behavior. The copied baseline still inherits
Artifact 2.2 local/demo dry-run scalar argument validation behavior.

A3.3 introduces a local/demo approval-gated GitHub issue-comment tool named
`post_github_issue_comment` with scalar arguments `repository`, `issue_number`,
and `comment_body`. Future sprints may design real GitHub API execution behind
the same safety boundary.

## What A3.1 Adds

A3.1 defines the future real side-effect boundary before any GitHub write path
exists.

It specifies future requirements for explicit real-mode enablement,
server-side GitHub token/config handling, repository allowlist policy, approval
binding to the exact validated action, deterministic `side_effect_id`
derivation, side-effect ledger checks, GitHub issue-comment client boundaries,
dry-run vs real behavior, failure behavior, and audit evidence.

A3.1 does not add a GitHub client, fake GitHub client, side-effect ledger,
`side_effect_id`, `post_github_issue_comment`, registry entries, policy
implementation, real-mode config implementation, API routes, graph execution
changes, proposer changes, validator changes, or tool execution changes.

## What A3.2 Adds

A3.2 adds the isolated supporting boundaries that A3.1 specified:

- typed GitHub issue-comment request, result, and failure schemas
- `GitHubIssueCommentClient` protocol
- deterministic `FakeGitHubIssueCommentClient`
- deterministic validated argument hashing
- deterministic side-effect id generation
- `SideEffectRecord`
- `SideEffectLedger`
- `InMemorySideEffectLedger`

At A3.2, these were direct unit-test targets only. A3.2 did not register
`post_github_issue_comment`, add a GitHub comment skill, wire runtime approval
or graph execution, load tokens, or call GitHub.

## What A3.3 Adds

A3.3 registers one approval-gated GitHub issue-comment skill/tool path:
`post_github_issue_comment`.

It accepts only validated scalar arguments:

- `repository`
- `issue_number`
- `comment_body`

The skill is high risk, so valid runs pause for approval before execution. The
repository is checked against a trusted local/demo allowlist. Approved runs
compute `validated_arguments_hash` and `side_effect_id`, check
`InMemorySideEffectLedger`, and call `FakeGitHubIssueCommentClient` only if no
prior succeeded record exists.

This is simulated local/demo execution. A3.3 does not add a real GitHub API
adapter, token loading, arbitrary repository targeting, durable ledger, or
production replay protection.

## Why Policy Is Still Needed

Validation answers:

```text
Is this proposed skill structurally allowed for this registry and identity?
```

Policy answers:

```text
May this resolved identity execute or request this registered tool now?
```

That separation keeps proposal validation, authorization, approval, and
execution independently testable.

## Why High-Risk Actions Require Approval

High-risk validated proposals do not execute directly.

The graph creates an approval request, checkpoints state, and pauses. Approval
or rejection later resumes the graph.

Rejection finalizes without tool execution. Invalid approval actors fail safely.

## How The Optional LLM Boundary Works

`LLMProposer` is provider-neutral and receives an injected client. Tests use
mocked clients only.

Malformed model output becomes a malformed proposal with evidence in the
rationale, then the validator rejects it. No tests require credentials, network
access, or real model calls.

## Current API Boundary

The FastAPI routes expose the inherited deterministic task API from Artifact 1
and the completed Artifact 2.1 skill-runner lifecycle:

- `GET /skills`
- `POST /skill-runs`
- `GET /skill-runs/{run_id}`
- `POST /skill-runs/{run_id}/approve`
- `POST /skill-runs/{run_id}/reject`
- `GET /skill-runs/{run_id}/audit`

The default HTTP API uses fake proposer mode and can demonstrate low-risk
skill-run creation, summary retrieval, audit retrieval, and safe rejection of
disabled HTTP LLM mode.

Invalid proposal, high-risk approval, high-risk rejection, and approved
high-risk audit behavior are covered by API tests using scenario-configured fake
proposer injection. The default running HTTP API does not currently expose a
public request field for selecting those fake proposer scenarios.

## Current Limitations

- local/demo artifact
- one A3.3 fake-client GitHub comment skill path only
- no real GitHub client code
- no runtime GitHub client wiring beyond the fake-client comment path
- no durable side-effect ledger wiring
- no durable side-effect ledger
- no real-mode configuration
- no configurable repository allowlist runtime policy
- no OAuth/OIDC or JWT validation
- no MCP
- no database persistence
- no frontend
- no multi-agent behavior
- no real GitHub writes
- no real workflow triggers
- tools are dry-run only
- Artifact 2.2 V1 supports only scalar string/integer/boolean arguments
- no object/list/nested argument validation
- no partial acceptance of mixed valid and invalid argument plans
- HTTP `llm` proposer mode is disabled and rejected

## Strong Interview Framing

This is not merely an LLM tool-use demo.

It is a harness that accepts model-proposed skill plans and runtime arguments
while keeping identity, authorization, approval, argument validation,
execution, and audit in deterministic application layers.
