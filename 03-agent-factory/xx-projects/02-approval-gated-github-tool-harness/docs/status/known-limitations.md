# Known Limitations

This file lists current limits so the project stays honest as a portfolio
artifact.

## Local/Demo Scope

Artifact 3 — Approval-Gated GitHub Tool Harness started as an A3.0 baseline
copy from the finalized Artifact 2.2 project.

The project is still a local/demo harness. A3.2 adds isolated fake/in-memory
supporting boundaries only.

Artifact 2.2 remains the completed dry-run scalar argument validation artifact.
The current Artifact 3 baseline still inherits Artifact 2.2 local/demo dry-run
scalar argument validation behavior.

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
- the A3.2 side-effect ledger is in-memory only and not wired into runtime
- rate limit windows reset on process restart

## API Surface

The current FastAPI routes expose the inherited task API plus skill-run
metadata, creation, read, approval, rejection, and audit endpoints.

Current local/demo limitations:

- skill-run state is process-local
- skill-run audit is in-memory only
- skill-run approval and rejection use demo API-key identity
- default HTTP skill-run creation uses fake proposer mode
- HTTP `proposer_mode: "llm"` is disabled and rejected with `400`
- default curl requests cannot select invalid or high-risk fake proposer
  scenarios

Invalid proposal, high-risk approval, high-risk rejection, and approved
high-risk audit behavior are covered by API tests using scenario-configured fake
proposer injection.

## Tool Execution

Tools are dry-run only.

Artifact 3 has not implemented real GitHub side effects. A3.1 defines the
future boundary for an approval-gated GitHub issue-comment tool named
`post_github_issue_comment` with scalar arguments `repository`, `issue_number`,
and `comment_body`. A3.2 adds isolated GitHub issue-comment client and
side-effect ledger boundaries for later use.

Not implemented:

- real GitHub client code
- GitHub client runtime integration
- side-effect ledger runtime integration
- durable side-effect ledger
- `post_github_issue_comment`
- approval-gated GitHub comment skill
- real-mode environment configuration
- repository allowlist runtime policy
- real GitHub writes
- real issue comments
- real workflow triggers
- external side-effecting tool adapters

## Tool Arguments

Skill specs include trusted argument-schema metadata. The proposal validator
accepts only registry-declared scalar string/integer/boolean arguments and the
skill graph passes accepted `ValidatedSkillPlan` arguments to dry-run tools.

Not implemented yet:

- object argument support
- list argument support
- nested object validation
- arbitrary JSON payload validation
- partial acceptance of mixed valid and invalid argument plans
- a general argument schema framework

## LLM Provider Boundary

`LLMProposer` is optional and provider-neutral. Tests use mocked clients.

The HTTP API does not enable live LLM mode. Requests with
`proposer_mode: "llm"` return a safe `400` response without calling a provider.

Not implemented:

- provider SDK integration
- API credential loading
- real model calls in tests
- live LLM calls through the HTTP API
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
It should not be described as production security infrastructure.

A3.2 does not provide production replay protection. It adds a process-local
idempotency boundary that future implementation can wire into a runtime path
after separate approval.
