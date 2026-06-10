# Roadmap

## V1 - Portfolio MVP

V1 is complete as a local/demo portfolio artifact.

Implemented:

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

V1 proves the harness shape:

```text
The LLM proposes. The harness decides.
```

V1 does not call an LLM. The deterministic proposer can later be replaced by an LLM without changing identity, policy, approval, execution, or audit layers.

## V1.1 - Durability Upgrade

Possible next durability work:

- SQLite checkpointing for local durable demos
- Postgres checkpointing for longer-running deployments
- durable task store
- persisted audit trail
- task listing endpoints backed by durable storage
- restart-safe approval resume

Goal:

Make the local/demo harness survive process restart without changing the policy and approval model.

## V2 - OAuth-Integrated Agent Harness

Possible identity and authorization work:

- OAuth/OIDC integration
- JWT validation
- real authorization server integration
- token-derived user identity
- token-derived scopes
- key rotation and issuer/audience checks
- production-grade auth error handling

Goal:

Replace static demo API keys with production-style identity while preserving server-derived identity and deterministic policy.

## V3 - Production Agent Runtime

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
