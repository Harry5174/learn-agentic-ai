# Sprint 5: Documentation, Demo Scenarios, and Portfolio Packaging

## Status

Sprint 5 is the documentation and portfolio packaging sprint for Artifact 2.

It does not add runtime behavior.

## Goal

Turn Artifact 2 into a clear, honest, evaluator-ready portfolio artifact for
AI/backend interviews, mentor review, agentic software learning, and future
Agent Factory direction.

The central message is:

```text
The LLM proposes.
The harness validates, authorizes, approval-gates, executes, and audits.
```

## Current Implemented Artifact 2 Behavior

Artifact 2 now includes:

- structured `SkillSpec`, `SkillStep`, and `SkillProposal` contracts
- a default `SkillRegistry` with allowed skill and tool metadata
- deterministic `ProposalValidator` checks for untrusted proposals
- a deterministic `FakeProposer` for tests and local demos
- an optional provider-neutral `LLMProposer` boundary with mocked-client tests
- a checkpointed skill execution graph in `src/app/skill_graph/`
- dry-run tool execution through the existing `ToolRegistry`
- deterministic policy checks through the existing policy guard
- approval pause/resume for high-risk validated proposals
- structured audit events for proposal, validation, policy, approval, and execution

## Sprint 5 Scope

Sprint 5 updates documentation only:

- portfolio README
- project status
- architecture documentation
- API boundary documentation
- threat model
- demo scenarios
- Artifact 1 vs Artifact 2 comparison
- known limitations
- roadmap
- interview notes
- sprint spec hygiene

## Non-Goals

Sprint 5 does not implement:

- new API endpoints
- new UI or frontend
- MCP
- OAuth/OIDC
- JWT validation
- database persistence
- production deployment
- real GitHub writes
- real workflow triggers
- multi-agent behavior
- new skill execution capabilities
- argument schema framework
- new LLM provider framework
- evaluation harness
- external tool integrations

Sprint 5 does not change:

- runtime behavior
- identity semantics
- policy semantics
- approval/checkpoint semantics
- tool execution behavior
- `FakeProposer` behavior
- mocked-test setup

## Documentation Requirements

Sprint 5 documentation must explain:

- what Artifact 2 is
- why it exists
- how it differs from Artifact 1
- the implemented proposal-to-execution architecture
- the LLM/harness trust boundary
- the role of `ProposalValidator`
- approval gate behavior
- audit behavior
- demo scenarios
- known limitations
- narrow future roadmap

## Architecture Flow To Document

```text
Client/task
-> proposer
-> SkillProposal
-> ProposalValidator
-> SkillRegistry
-> policy guard
-> approval gate
-> dry-run ToolRegistry
-> audit
-> SkillRunResult
```

## Demo Scenarios To Document

Sprint 5 documentation must cover:

- valid low-risk proposal executes a dry-run tool
- invalid proposal is rejected before policy or execution
- hallucinated skill or tool is rejected
- high-risk proposal pauses for approval
- approved high-risk proposal resumes and executes
- rejected high-risk proposal does not execute
- malformed LLM output fails safely

These scenarios are documentation-only for Sprint 5. They are backed by the
existing fake proposer, LLM proposer, proposal validator, and skill graph tests.

## Known Limitations To Document

Sprint 5 must keep the following limits explicit:

- local/demo artifact
- no production deployment
- no OAuth/OIDC
- no MCP
- no real GitHub writes
- no database persistence
- no frontend
- no multi-agent behavior
- no real workflow triggers
- tool arguments remain limited and harness-owned defaults are used
- real LLM proposer is optional and tests use mocked outputs
- tools remain dry-run

## Sprint Spec Hygiene

The active Artifact 2 sprint specs are:

- `docs/sprint-2-spec.md`
- `docs/sprint-3-spec.md`
- `docs/sprint-4-spec.md`
- `docs/sprint-5-spec.md`

Copied Artifact 1 sprint specs that could mislead future IDE agents should live
under:

```text
docs/archive/artifact-1-sprint-specs/
```

## Acceptance Criteria

Sprint 5 is complete when:

- README accurately describes implemented Artifact 2 behavior
- README avoids production-readiness claims
- architecture flow is documented
- LLM/harness boundary is documented
- `ProposalValidator` role is documented
- approval gate behavior is documented
- audit behavior is documented
- required demo scenarios are documented
- Artifact 1 vs Artifact 2 distinction is documented
- known limitations are documented
- future roadmap is narrow and honest
- tool-argument limitation is documented
- stale Artifact 1 sprint specs are archived or clearly removed from the active docs path
- no runtime behavior is changed
- no real model calls are required
- no new dependencies are added
- full test suite passes
- Ruff passes
