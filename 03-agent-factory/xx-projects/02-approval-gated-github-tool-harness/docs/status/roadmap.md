# Roadmap

This roadmap is intentionally narrow. Artifact 3 — Approval-Gated GitHub Tool
Harness starts at A3.0 as a copied baseline from the finalized Artifact 2.2
project, then uses A3.1 to define the future real side-effect boundary before
any GitHub write path is implemented.

For the project-level sequencing rules, see
[../specs/constitution/roadmap.md](../specs/constitution/roadmap.md).

## A3.0 Baseline Copy

A3.0 copies the completed Artifact 2.2 local/demo baseline into this new
Artifact 3 project folder and updates project identity/documentation only.

Artifact 2.2 remains the completed dry-run scalar argument validation artifact.
The current Artifact 3 baseline still inherits Artifact 2.2 local/demo dry-run
scalar argument validation behavior.

Artifact 3 has not yet implemented real GitHub side effects.

## A3.1 Real Side-Effect Boundary Spec

A3.1 defines the future boundary for an approval-gated GitHub issue-comment
tool named `post_github_issue_comment` with scalar arguments `repository`,
`issue_number`, and `comment_body`.

A3.1 is documentation/specification only. It does not implement GitHub
execution, a GitHub client, fake GitHub client, side-effect ledger,
`side_effect_id`, `post_github_issue_comment`, repository allowlist logic,
real-mode configuration, tool registry entries, policy implementation, graph
execution changes, API route changes, proposer changes, validator changes, or
tool execution changes.

## Inherited Artifact 2 Foundation

Inherited work includes:

- structured skill contracts
- trusted skill registry
- deterministic proposal validation
- deterministic fake proposer
- optional provider-neutral LLM proposer boundary
- checkpointed skill execution graph
- policy checks outside the model
- approval gate for high-risk execution
- dry-run tool execution
- audit evidence for proposal, validation, policy, approval, and execution

## Completed Artifact 2.1 API Surface

Artifact 2.1 exposes the skill-runner lifecycle through the local/demo FastAPI
surface:

- `GET /skills`
- `POST /skill-runs`
- `GET /skill-runs/{run_id}`
- `POST /skill-runs/{run_id}/approve`
- `POST /skill-runs/{run_id}/reject`
- `GET /skill-runs/{run_id}/audit`

Historical note: Artifact 2.1 included E1.3 documentation/demo-surface
tightening work. Current status: Artifact 2.2 is complete within local/demo
scalar-argument scope.

## Completed Artifact 2.2 Argument Boundary

Artifact 2.2 is complete as a local/demo safety artifact. It includes Sprint
E2.0 argument contract design, Sprint E2.1 validator argument checks, Sprint
E2.2 execution wiring, and Sprint E2.3 adversarial boundary evidence.

Artifact 2.2 targets:

- validated proposed tool arguments
- a raw proposed argument non-execution rule
- scalar-only V1 argument schema stubs
- central forbidden argument names
- redaction policy documentation
- deterministic validator checks for proposed scalar step arguments
- execution using accepted `ValidatedSkillPlan` arguments only
- focused adversarial tests for argument-level failures

Sprint E2.0 covers the contract design and schema stubs. Sprint E2.1 validates
proposed arguments into `ValidatedSkillPlan`. Sprint E2.2 wires accepted
validated arguments into graph/tool execution. Sprint E2.3 proves adversarial
argument-boundary behavior and updates the documentation surface.

Raw proposed arguments still do not execute directly.

Artifact 2.2 must preserve the existing safety boundary: model output remains
untrusted, and the harness validates before policy, approval, or execution.

## Near-Term Follow-Ups

Useful next steps after A3.1:

- A3.2 implementation work only if explicitly approved and scoped against the
  A3.1 boundary spec
- future tool name: `post_github_issue_comment`
- future scalar arguments: `repository`, `issue_number`, and `comment_body`
- richer argument schema support only after an explicit future design pass

## Future Integration Paths

Possible future work:

- approval-gated GitHub issue comments
- MCP adapter after skill/tool contracts stabilize
- OAuth/OIDC identity integration
- durable task/run persistence
- durable audit storage
- GitHub write tools behind approval gates
- object/list/nested argument support if it is threat-modeled separately
- portfolio deployment demo

## Still Out Of Scope

- real GitHub side effects in A3.1
- GitHub client code in A3.1
- fake GitHub client code in A3.1
- side-effect ledger or `side_effect_id` in A3.1
- `post_github_issue_comment` implementation in A3.1
- real-mode configuration in A3.1
- autonomous production writes without approval
- broad chatbot or RAG features
- multi-agent behavior
- production traffic control
- production deployment hardening
- model-specific business logic in route handlers
- treating prompt instructions as security controls
