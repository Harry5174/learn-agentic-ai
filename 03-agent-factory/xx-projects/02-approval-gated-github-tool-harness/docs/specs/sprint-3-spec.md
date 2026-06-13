# Sprint 3: Fake Proposer and Skill Execution Graph

## Objective
Connect the existing skill contracts and proposal validator into a controlled
execution workflow using a fake deterministic proposer and a LangGraph-based
skill execution graph.

The proposer proposes. The harness validates, authorizes, approval-gates,
executes dry-run tools, and audits.

## Scope
- minimal proposer interface
- deterministic fake proposer scenarios
- separate skill execution graph state and service
- proposal validation before policy or execution
- policy evaluation through the existing tool policy guard
- checkpointed approval pause/resume for high-risk validated proposals
- dry-run tool execution through the existing `ToolRegistry`
- audit events using the existing audit event style and structured metadata
- focused proposer and skill graph tests

## Non-Goals
- real LLM proposer
- prompt templates
- model/provider configuration
- MCP
- OAuth/OIDC
- JWT validation
- public API routes
- existing task API changes
- identity semantics changes
- policy semantics changes
- tool registry behavior changes
- real GitHub writes
- real workflow triggers
- frontend
- database persistence
- production deployment
- multi-agent behavior
- autonomous planning loops
- dependencies

## Planned Files
- `src/app/proposer/__init__.py`
- `src/app/proposer/base.py`
- `src/app/proposer/fake.py`
- `src/app/skill_graph/__init__.py`
- `src/app/skill_graph/state.py`
- `src/app/skill_graph/graph.py`
- `src/app/skill_graph/service.py`
- `tests/test_fake_proposer.py`
- `tests/test_skill_execution_graph.py`

## Acceptance Criteria
- fake proposer exists
- proposer abstraction exists
- skill execution graph exists
- graph validates proposal before policy/execution
- graph rejects invalid proposal without execution
- graph executes valid low-risk proposal using dry-run tools
- graph marks high-risk proposal as approval-required
- high-risk proposal does not execute before approval
- approval/rejection behavior is covered by tests
- audit records proposal and validation outcome
- audit records policy/approval outcome
- audit records execution outcome when execution occurs
- no real LLM code is added
- no prompt-template/model-provider logic is added
- no MCP/OAuth/JWT/frontend/database behavior is added
- no real external side effects are added
- existing identity semantics are preserved
- existing policy semantics are preserved
- existing tests pass
- Ruff passes
