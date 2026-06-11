# Sprint 2: Proposal Validator

## Objective
Implement a deterministic validator for untrusted `SkillProposal` objects before
any policy, approval, graph execution, or tool execution can happen.

The proposal validator treats model output like an external API request: it must
be schema-valid, registry-allowed, identity-authorized, and risk-consistent
before anything can execute.

## Scope
- validator result contract
- structured rejection reasons
- `ProposalValidator`
- skill/version validation through `SkillRegistry`
- proposed step and tool validation against registered `SkillSpec` metadata
- scope checks against `IdentityContext.scopes`
- risk derivation from registry metadata
- approval-required derivation for high-risk validated skills or steps
- focused validator tests

## Non-Goals
- fake proposer
- real LLM proposer
- proposer interfaces
- skill execution
- tool invocation
- LangGraph nodes
- FastAPI routes
- approval flow changes
- policy behavior changes
- identity behavior changes
- tool registry behavior changes
- audit persistence changes
- OAuth/OIDC
- JWT validation
- database persistence
- frontend
- production deployment
- dependencies

## Planned Files
- `src/app/skills/schemas.py`
- `src/app/skills/validator.py`
- `tests/test_proposal_validator.py`

## Acceptance Criteria
- `ProposalValidator` exists
- validation result type exists
- structured rejection reasons exist
- validator uses `SkillRegistry`
- validator accepts valid proposals for known skills
- validator rejects unknown skills
- validator rejects unsupported versions
- validator rejects empty steps
- validator rejects duplicate step IDs
- validator rejects unknown steps
- validator rejects tool mismatches or disallowed tools
- validator rejects missing required scopes
- validator rejects risk understatement from proposed step metadata
- validator derives risk from registry metadata
- validator derives `approval_required=True` for high-risk validated skills or steps
- validator does not execute tools
- validator does not call LLMs
- validator does not wire LangGraph
- validator does not modify API behavior
- validator does not change identity semantics
- validator does not change policy semantics
- focused tests pass
- full test suite passes
- Ruff passes
