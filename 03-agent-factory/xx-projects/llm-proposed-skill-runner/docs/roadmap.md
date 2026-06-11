# Roadmap

This roadmap is intentionally narrow. Artifact 2 is a local/demo skill-runner
harness, not a production platform plan.

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

## Current Sprint: Documentation And Portfolio Packaging

Sprint 5 focuses on:

- portfolio README
- architecture docs
- demo scenarios
- threat model
- known limitations
- Artifact 1 vs Artifact 2 distinction
- sprint spec hygiene

No runtime behavior is added in Sprint 5.

## Near-Term Follow-Ups

Useful next steps after Sprint 5:

- validated proposed tool arguments
- small adversarial proposal test suite
- clearer public response contract if skill-runner API endpoints are later added
- optional demo-only script if documentation stops being enough

## Future Integration Paths

Possible future work:

- MCP adapter after skill/tool contracts stabilize
- OAuth/OIDC identity integration
- durable task/run persistence
- durable audit storage
- real GitHub write tools behind approval gates
- portfolio deployment demo

## Still Out Of Scope

- autonomous production writes without approval
- broad chatbot or RAG features
- multi-agent behavior
- production traffic control
- production deployment hardening
- model-specific business logic in route handlers
- treating prompt instructions as security controls
