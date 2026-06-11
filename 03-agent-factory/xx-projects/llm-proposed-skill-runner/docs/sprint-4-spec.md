# Sprint 4: Real LLM Proposer

## Objective
Add an optional real LLM proposer behind the existing proposer abstraction.

The LLM proposes a structured `SkillProposal`. The harness remains responsible
for validation, policy checks, approval gating, execution, and audit records.

## Scope
- Provider-neutral prompt/context helpers.
- Injectable `LLMProposer` client boundary.
- Safe parsing of mocked LLM output into `SkillProposal`.
- Malformed-output fallback that preserves evidence of the parse/schema failure.
- Focused proposer tests using mocked clients only.

## Non-Goals
- MCP
- OAuth/OIDC
- JWT validation
- multi-agent behavior
- real GitHub writes
- real workflow triggers
- frontend
- database persistence
- production deployment
- autonomous planning loops
- recursive planning
- skill marketplace
- YAML/JSON skill loading
- public API expansion

## Harness Authority Boundary
The LLM proposer may return only a proposed skill plan.

It must not:
- authorize
- approve
- execute tools
- bypass `ProposalValidator`
- bypass policy
- bypass approval
- invent trusted tools
- decide final risk

The invariant is:

```text
LLM output -> SkillProposal parsing -> ProposalValidator -> policy/approval/execution
```

## Test Boundary
Tests use mocked client output only.

No test requires:
- real model calls
- network access
- API credentials
- provider SDKs

`FakeProposer` remains available and remains the default graph proposer.
