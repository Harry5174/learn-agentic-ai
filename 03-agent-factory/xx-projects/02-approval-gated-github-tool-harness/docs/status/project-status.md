# Project Status

## Project

**Title:** Artifact 3 — Approval-Gated GitHub Tool Harness

**Copied baseline:** LLM-Proposed, Harness-Controlled Skill Runner

**A3.0 status:** Baseline copy and rename complete.

**A3.1 status:** Real side-effect boundary specification only.

**A3.2 status:** Isolated GitHub client and side-effect ledger boundaries.

**A3.3 status:** One approval-gated local/demo GitHub issue-comment skill path.

**A3.4 status:** Adversarial safety suite for the A3.3 GitHub comment
side-effect boundary.

**A3.5 status:** Demo and portfolio packaging for the completed local/demo
Artifact 3 evidence.

**Principle:** The LLM proposes. The harness validates, authorizes,
approval-gates, executes, and audits.

**Safety Invariant:** Identity is server-derived, policy is deterministic, and
high-risk execution cannot happen before approval.

For the current project constitution, see
[../specs/constitution/mission.md](../specs/constitution/mission.md).

## Current Artifact Status

Artifact 3 started with A3.0, a copied baseline from the finalized Artifact 2.2
project. This copied project now carries the Artifact 3 identity.

A3.1 defines the future real side-effect boundary for an approval-gated GitHub
issue-comment tool. It is documentation/specification only and does not
implement real GitHub side effects.

A3.2 adds isolated supporting boundaries for a future GitHub issue-comment
client and side-effect idempotency ledger.

A3.3 registers exactly one GitHub issue-comment skill/tool path,
`post_github_issue_comment`. It uses validated scalar `repository`,
`issue_number`, and `comment_body` arguments, a trusted local/demo repository
allowlist, high-risk approval, `validated_arguments_hash`, deterministic
`side_effect_id`, the process-local `InMemorySideEffectLedger`, and
`FakeGitHubIssueCommentClient` simulated execution.

A3.3 does not implement real GitHub API execution.

A3.4 adds adversarial tests for that one fake-client side-effect path. The
suite covers argument smuggling, unsupported object/list/nested payloads,
repository policy bypass attempts, approval bypass attempts, approval-binding
mutation behavior within the current architecture, replay and duplicate
execution behavior, fake-client failure safety, network/token safety, and audit
completeness. No implementation hardening was required by the A3.4 suite.

A3.5 packages the README, GitHub comment demo, comparison docs, status pages,
and portfolio notes so Artifact 3 can be reviewed without implying real GitHub
execution or production security infrastructure.

Artifact 3 still does not implement real GitHub API execution.

Artifact 2.2 remains the completed dry-run scalar argument validation artifact.
The current Artifact 3 baseline still inherits Artifact 2.2 local/demo dry-run
scalar argument validation behavior.

Repository folder numbering was applied after the original A3.0 copy/rename
prompt. Current source baseline folder:
`03-agent-factory/xx-projects/01-llm-proposed-skill-runner`. Current target
Artifact 3 folder:
`03-agent-factory/xx-projects/02-approval-gated-github-tool-harness`.

Artifact 2 has completed the proposal-validation, skill-execution, and
Artifact 2.1 HTTP lifecycle foundation for a local/demo skill runner.

Artifact 2.2 is complete as a local/demo safety artifact. Sprint E2.0 added the
argument contract design, Sprint E2.1 added validator argument checks, Sprint
E2.2 wired validated arguments into execution, and Sprint E2.3 added
adversarial boundary tests plus final documentation packaging.

Raw proposed arguments still do not execute directly.

Implemented:

- `SkillSpec`, `SkillStep`, and `SkillProposal` contracts
- `SkillRegistry` with default registered skills
- `ProposalValidator` for deterministic validation of untrusted proposals
- `FakeProposer` for deterministic local/test scenarios
- optional `LLMProposer` boundary using injected mocked clients in tests
- checkpointed skill execution graph in `src/app/skill_graph/`
- policy and approval integration for validated skill proposals
- dry-run tool execution through the existing `ToolRegistry`
- audit events for proposal, validation, policy, approval, and execution
- Artifact 2.1 skill-runner API routes for listing skills, creating runs,
  reading runs, approving/rejecting paused runs, and retrieving audit events
- Artifact 2.2 E2.1 validation of model-proposed scalar step arguments into a
  trusted `ValidatedSkillPlan`
- Artifact 2.2 E2.2 graph wiring so dry-run tools receive accepted validated
  step arguments only
- Artifact 2.2 E2.3 adversarial tests for argument attacks, raw non-execution,
  safe audit/API evidence, and approval preservation
- A3.2 isolated `GitHubIssueCommentClient` protocol,
  `FakeGitHubIssueCommentClient`, issue-comment request/result/failure schemas,
  deterministic side-effect id helpers, `SideEffectRecord`,
  `SideEffectLedger`, and `InMemorySideEffectLedger`
- A3.3 `post_github_issue_comment` skill/tool registration, repository
  allowlist policy, approval-gated fake-client execution, ledger replay
  suppression, and GitHub comment audit evidence
- A3.4 adversarial GitHub comment side-effect safety suite covering smuggling,
  unsupported payloads, policy/approval bypass attempts, approval-binding
  mutation behavior, replay/duplicate execution, fake-client failure safety,
  network/token checks, and audit completeness
- A3.5 portfolio packaging, including a GitHub comment demo guide, Artifact 2
  vs Artifact 3 comparison, updated README, and final evidence summary

Historical note: Artifact 2.1 included E1.3 documentation, demo walkthrough,
and portfolio packaging work. Current status: Artifact 2.2 is complete within
local/demo scalar-argument scope.

## Inherited Artifact 2 Sprint Specs

The copied baseline still includes the Artifact 2 foundation sprint specs:

- `../specs/sprint-2-spec.md`
- `../specs/sprint-3-spec.md`
- `../specs/sprint-4-spec.md`
- `../specs/sprint-5-spec.md`

Artifact 2.1 extends that foundation with the skill-runner API lifecycle.
A3.2 adds isolated supporting boundary modules. A3.3 adds one approval-gated
local/demo GitHub issue-comment tool and skill. A3.4 adds adversarial evidence
for that fake-client side-effect boundary. A3.5 packages the completed
local/demo demo and portfolio evidence.

Copied Artifact 1 sprint specs that could mislead future IDE agents are archived
under:

```text
../specs/archive/artifact-1-sprint-specs/
```

## Inherited Foundation From Artifact 1

Artifact 2 keeps the completed Artifact 1 harness foundation:

- server-derived demo API-key identity resolver
- deterministic policy guard
- controlled dry-run tool registry
- structured in-memory audit helpers
- checkpointed approval resume behavior
- FastAPI task API
- in-memory public-demo rate limiting

Artifact 2 adds the skill proposal layer on top of that foundation. It does not
move security-relevant decisions into the model.

## Current API Status

The FastAPI surface is unchanged from the inherited baseline. It includes the
inherited local/demo task API and the completed Artifact 2.1 skill-runner
routes:

- `GET /tools`
- `GET /identity/me`
- `GET /skills`
- `POST /tasks`
- `GET /tasks/{task_id}`
- `POST /tasks/{task_id}/approve`
- `POST /tasks/{task_id}/reject`
- `GET /tasks/{task_id}/audit`
- `POST /skill-runs`
- `GET /skill-runs/{run_id}`
- `POST /skill-runs/{run_id}/approve`
- `POST /skill-runs/{run_id}/reject`
- `GET /skill-runs/{run_id}/audit`

Skill-run routes are exposed through `SkillGraphService` for process-local
demo runs.

The default HTTP skill-runner path uses fake proposer mode. HTTP
`proposer_mode: "llm"` is disabled and returns a safe `400` response without
calling a live model provider. Invalid proposal, high-risk approval, high-risk
rejection, and approved high-risk audit behavior are covered by API tests using
scenario-configured fake proposer injection.

## Current Persistence Status

The graph uses LangGraph `InMemorySaver`.

This means:

- task/run state is process-local
- checkpoints do not survive process restart
- paused tasks or skill runs can resume only while the process is alive
- audit events are not persisted to a database

## Current Test Boundary

Tests use deterministic fake outputs or mocked LLM-client outputs.

A3.3 tests use deterministic fake GitHub issue-comment clients and an
in-memory side-effect ledger only.

A3.4 tests add adversarial coverage for the GitHub comment path using fake
clients, in-memory ledgers, and in-process API calls only.

No test depends on:

- real model calls
- network access
- API keys or credentials
- GitHub write operations
- real workflow triggers

## Explicitly Not Implemented

- real GitHub client code
- GitHub client runtime wiring beyond the one fake-client comment path
- durable side-effect ledger runtime wiring
- durable side-effect ledger
- real GitHub issue comments
- real-mode environment configuration
- configurable repository allowlist logic
- OAuth/OIDC
- JWT validation
- MCP
- database persistence
- durable audit storage
- frontend
- production deployment
- multi-agent behavior
- GitHub write operations
- real workflow triggers
- provider SDK integration
- live LLM mode through HTTP

## A3.1 Boundary Spec Status

A3.1 defines future implementation requirements for:

- real execution preconditions
- explicit real-mode configuration
- GitHub token/config boundaries
- repository allowlist policy
- approval binding to the exact validated action
- deterministic `side_effect_id` derivation
- `SideEffectLedger` and `SideEffectRecord` contracts
- GitHub issue-comment client boundaries
- dry-run vs real behavior
- structured failure behavior
- audit event requirements

These are documented future contracts only. They are not runtime behavior in
A3.1.

## A3.2 Boundary Module Status

A3.2 implements only isolated support boundaries:

- `GitHubIssueCommentRequest`
- `GitHubIssueCommentResult`
- `GitHubIssueCommentFailure`
- `GitHubIssueCommentClient`
- `FakeGitHubIssueCommentClient`
- deterministic `validated_arguments_hash`
- deterministic side-effect id generation
- `SideEffectRecord`
- `SideEffectLedger`
- `InMemorySideEffectLedger`

At A3.2, these boundaries were tested directly and were not registered as
tools or used by the skill graph, approval flow, API routes, runtime config, or
repository policy logic. A3.3 wires the fake client and in-memory ledger into
the one local/demo path described below.

## A3.3 GitHub Comment Skill Status

A3.3 implements one local/demo skill path:

- skill/tool name: `post_github_issue_comment`
- required scalar arguments: `repository`, `issue_number`, `comment_body`
- default allowed repository: `Harry5174/learn-agentic-ai`
- required scope: `tools:post_github_comment`
- risk level: high
- approval required before fake-client execution
- fake client: `FakeGitHubIssueCommentClient`
- replay guard: process-local `InMemorySideEffectLedger`

The path computes `validated_arguments_hash` and `side_effect_id` before the
fake-client call. If the same approved action already has a succeeded ledger
record, the fake-client call is skipped and returned as a cached/skipped local
result.

The current approval schema binds approval to the validated tool arguments in
the checkpointed graph state. It does not persist `validated_arguments_hash` or
`side_effect_id` inside `ApprovalDecision`; stronger persisted approval binding
is deferred.

This is not real GitHub execution and does not load GitHub tokens.

## A3.4 Adversarial Safety Status

A3.4 adds `tests/test_adversarial_github_side_effect_safety.py` and
`docs/adversarial-github-side-effect-safety.md`.

The suite proves that the one A3.3 fake-client GitHub issue-comment path
rejects or blocks:

- credential and control-plane argument smuggling
- object/list/nested payloads
- arbitrary JSON blobs
- repository allowlist bypass attempts
- model-proposed policy and approval overrides
- approval attempts by identities without approval scope
- duplicate approval after completion
- duplicate fake-client execution after a succeeded ledger hit
- fake-client failures that might otherwise be misreported as success

The suite also checks that the GitHub comment runtime path has no automatic
GitHub token loading and no real network implementation.

A3.4 did not add real GitHub execution, durable persistence, a second GitHub
tool, or broader automation behavior.

## A3.5 Demo And Portfolio Packaging Status

A3.5 adds or updates documentation only:

- README as the Artifact 3 portfolio entry point
- `docs/demos/github-comment-tool-demo.md`
- `docs/comparisons/artifact-2-vs-artifact-3.md`
- status, roadmap, limitations, interview, architecture, spec, and adversarial
  documentation consistency updates

The GitHub comment demo separates runnable public HTTP commands from
representative/test-backed GitHub-comment lifecycle evidence. This is necessary
because the default public HTTP API can list the registered
`post_github_issue_comment` skill, but it does not expose a request field that
selects the GitHub-comment fake proposer scenario from curl.

A3.5 does not add runtime behavior, real GitHub execution, token loading,
durable persistence, frontend, OAuth/OIDC, MCP, or a second GitHub tool.

## Final Artifact 3 Evidence Summary

- A3.0: baseline copy and rename from the completed Artifact 2.2 project.
- A3.1: real side-effect boundary specification only.
- A3.2: isolated GitHub issue-comment client and side-effect ledger
  boundaries.
- A3.3: one approval-gated local/demo GitHub issue-comment skill path using
  validated scalar arguments, repository policy, approval, in-memory ledger
  checks, fake-client execution, and audit evidence.
- A3.4: adversarial safety suite for smuggling, unsupported payloads, policy
  bypass attempts, approval bypass attempts, replay behavior, fake-client
  failure behavior, network/token safety, and audit completeness.
- A3.5: demo and portfolio packaging for the completed local/demo evidence.

Latest A3.5 validation evidence:

- `uv run pytest`: 449 tests passed
- `uv run ruff check .`: all checks passed

## Current Limitation To Keep Visible

Skill specs contain trusted argument metadata, and the proposal validator now
checks model-proposed scalar runtime arguments. The skill execution graph now
passes accepted `ValidatedSkillPlan` arguments to dry-run tools after proposal
validation, policy checks, and any required approval gate.

Raw proposed arguments do not flow directly to `ToolRegistry.execute()`. Public
API and audit summaries expose safe argument-validation status, argument names,
redaction names, and issue codes without raw rejected values.

Artifact 2.2 V1 remains intentionally narrow: no object/list/nested argument
support, no arbitrary JSON payload validation, and no partial acceptance.
