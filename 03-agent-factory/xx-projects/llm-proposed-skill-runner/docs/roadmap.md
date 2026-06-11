# Roadmap

## Artifact 2 Sprint 0 - Baseline Copy And Rename

Sprint 0 is limited to copy verification, metadata rename, documentation
clarification, test/Ruff verification, and git status reporting.

Current baseline:

- copied from the completed Artifact 1 harness,
  `Identity-Aware Stateful Agent Harness`
- internal Python package remains `app`
- runtime behavior remains unchanged
- Artifact 2 skill-runner implementation has not started

The inherited Artifact 1 baseline includes:

- server-derived demo API-key identity
- deterministic task interpretation
- controlled dry-run tool registry
- deterministic policy guard
- structured audit events
- LangGraph task harness
- checkpointed approval resume flow
- FastAPI task API
- in-memory rate limiting
- public safety documentation
- demo flow, safety model, and interview notes

The inherited baseline proves the harness shape:

```text
The LLM proposes. The harness decides.
```

The current baseline does not call an LLM. Artifact 2 will add explicit skill
proposal contracts and validation in later sprints.

## Later Artifact 2 Sprints - Skill Proposal Layer

Planned, not implemented yet:

- `SkillSpec`
- `SkillStep`
- `SkillProposal`
- proposal validation
- fake proposer
- real LLM proposer
- skill registry changes
- skill execution graph changes

Goal:

Let an LLM propose bounded skills while deterministic harness components retain
control over validation, policy, approval, execution, and audit.

## Future Durability Upgrade

Possible next durability work:

- SQLite checkpointing for local durable demos
- Postgres checkpointing for longer-running deployments
- durable task store
- persisted audit trail
- task listing endpoints backed by durable storage
- restart-safe approval resume

Goal:

Make the local/demo harness survive process restart without changing the policy
and approval model.

## Future Identity Upgrade

Possible identity and authorization work:

- OAuth/OIDC integration
- JWT validation
- real authorization server integration
- token-derived user identity
- token-derived scopes
- key rotation and issuer/audience checks
- production-grade auth error handling

Goal:

Replace static demo API keys with production-style identity while preserving
server-derived identity and deterministic policy.

## Future Production Runtime

Possible production work:

- multi-tenant deployment
- Redis or gateway-based distributed rate limiting
- real external tool adapters
- stronger policy engine
- policy configuration management
- LangSmith or equivalent observability
- structured tracing
- deployment hardening
- operational dashboards
- incident-oriented audit export

Goal:

Move from portfolio MVP to production agent runtime while keeping high-risk execution gated by deterministic policy and approval.

## Still Out of Scope Until Needed

- multi-agent behavior
- autonomous production writes without approval
- broad RAG/chatbot features
- fine-tuning
- model-specific business logic in route handlers
