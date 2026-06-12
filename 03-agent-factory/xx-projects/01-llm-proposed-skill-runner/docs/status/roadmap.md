# Roadmap

This roadmap is intentionally narrow. Artifact 2 is a local/demo skill-runner
harness, not a production platform plan.

For the project-level sequencing rules, see
[../specs/constitution/roadmap.md](../specs/constitution/roadmap.md).

## Completed Artifact 2 Foundation

Completed work includes:

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

Useful next steps after Artifact 2.2:

- optional demo-only script if documentation and API tests stop being enough
- richer argument schema support only after an explicit future design pass

## Future Integration Paths

Possible future work:

- MCP adapter after skill/tool contracts stabilize
- OAuth/OIDC identity integration
- durable task/run persistence
- durable audit storage
- GitHub write tools behind approval gates
- object/list/nested argument support if it is threat-modeled separately
- portfolio deployment demo

## Still Out Of Scope

- autonomous production writes without approval
- broad chatbot or RAG features
- multi-agent behavior
- production traffic control
- production deployment hardening
- model-specific business logic in route handlers
- treating prompt instructions as security controls
