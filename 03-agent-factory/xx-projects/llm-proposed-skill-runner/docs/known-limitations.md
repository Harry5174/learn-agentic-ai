# Known Limitations

This file lists current limits so the project stays honest as a portfolio
artifact.

## Local/Demo Scope

The project is a local/demo harness.

It does not include:

- production deployment
- production traffic controls
- production identity provider integration
- durable storage
- operational monitoring

## Identity

Current identity uses static demo API keys.

Not implemented:

- OAuth/OIDC
- JWT validation
- external identity provider integration
- user-managed accounts
- key rotation

## Persistence

State is process-local.

Current limits:

- checkpoints do not survive process restart
- task/run state is not stored in a database
- audit events are not durably persisted
- rate limit windows reset on process restart

## API Surface

The current FastAPI routes expose the inherited task API plus `GET /skills` and
`POST /skill-runs`.

Not implemented:

- skill-run fetch API
- skill-run approval API
- skill-run rejection API
- skill-run audit API

## Tool Execution

Tools are dry-run only.

Not implemented:

- real GitHub writes
- real issue comments
- real workflow triggers
- external side-effecting tool adapters

## Tool Arguments

Skill specs include argument-schema metadata, but current skill execution uses
harness-owned default arguments for registered dry-run tools.

Not implemented yet:

- validation of model-proposed runtime tool arguments
- execution using model-proposed runtime tool arguments
- a general argument schema framework

## LLM Provider Boundary

`LLMProposer` is optional and provider-neutral. Tests use mocked clients.

Not implemented:

- provider SDK integration
- API credential loading
- real model calls in tests
- model-specific retry or streaming behavior

## Product Surface

Not implemented:

- frontend
- multi-agent behavior
- MCP
- evaluation harness
- production deployment demo

## Security Claim

This project demonstrates a safer harness shape for model-proposed execution.
It should not be described as production-ready security infrastructure.
