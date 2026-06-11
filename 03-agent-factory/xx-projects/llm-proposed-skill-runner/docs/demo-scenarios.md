# Demo Scenarios

These scenarios document the implemented Artifact 2 behavior. They are backed by
existing tests and do not require real model calls, network access, credentials,
real GitHub writes, or workflow triggers.

The demo boundary is:

```text
proposer -> SkillProposal -> ProposalValidator -> policy -> approval -> dry-run tools -> audit
```

## Scenario 1: Valid Low-Risk Proposal Executes Dry-Run Tool

Purpose:

Show that a valid low-risk proposal can pass validation, pass policy, execute a
controlled dry-run tool, and produce a completed result.

Implemented path:

- `FakeProposer(FakeProposalScenario.VALID_LOW_RISK)`
- proposes `inspect_sandbox_health`
- validator accepts the proposal
- policy allows `inspect_sandbox_issues`
- dry-run tool executes
- result is `completed`

Evidence:

- `tests/test_skill_execution_graph.py::test_valid_low_risk_proposal_executes_dry_run_tool`

## Scenario 2: Invalid Proposal Is Rejected Before Execution

Purpose:

Show that a structurally invalid proposal cannot reach policy or tool execution.

Implemented path:

- `FakeProposer(FakeProposalScenario.INVALID_PROPOSAL)`
- proposes a known skill with a mismatched tool
- validator rejects with `tool_not_allowed`
- policy decisions remain empty
- tool results remain empty
- no approval request is created

Evidence:

- `tests/test_skill_execution_graph.py::test_invalid_proposal_stops_before_policy_or_tool_execution`
- `tests/test_proposal_validator.py::test_tool_mismatch_is_rejected`

## Scenario 3: Hallucinated Skill Or Tool Is Rejected

Purpose:

Show that model-invented skills or tools are not trusted.

Implemented path:

- unknown skill proposals are rejected with `unknown_skill`
- hallucinated tool names are rejected with `tool_not_allowed`
- rejected proposals do not execute tools

Evidence:

- `tests/test_skill_execution_graph.py::test_unknown_skill_rejected_validation_prevents_execution`
- `tests/test_llm_proposer.py::test_hallucinated_skill_still_flows_to_validator_rejection`
- `tests/test_llm_proposer.py::test_hallucinated_tool_still_flows_to_validator_rejection`

## Scenario 4: High-Risk Proposal Pauses For Approval

Purpose:

Show that high-risk work cannot execute immediately, even if the proposal is
valid.

Implemented path:

- `FakeProposer(FakeProposalScenario.VALID_HIGH_RISK)`
- proposes `simulate_sandbox_workflow`
- validator accepts and derives `approval_required=True`
- policy returns `require_approval`
- graph creates an approval request
- graph pauses before execution
- tool results remain empty

Evidence:

- `tests/test_skill_execution_graph.py::test_high_risk_proposal_pauses_without_execution_before_approval`

## Scenario 5: Approved High-Risk Proposal Resumes And Executes

Purpose:

Show that an approved high-risk proposal can resume from checkpoint and execute
the controlled dry-run tool.

Implemented path:

- high-risk run pauses
- authorized approver submits approval
- graph resumes with approval decision and actor
- `trigger_workflow_dry_run` executes in dry-run mode
- audit includes approval granted, tool executed, and task completed events

Evidence:

- `tests/test_skill_execution_graph.py::test_approved_high_risk_proposal_resumes_and_executes`

## Scenario 6: Rejected High-Risk Proposal Does Not Execute

Purpose:

Show that rejection finalizes the run without high-risk tool execution.

Implemented path:

- high-risk run pauses
- authorized actor rejects
- graph resumes with rejection decision
- result status is `rejected`
- tool results remain empty
- audit includes approval rejected and excludes tool executed

Evidence:

- `tests/test_skill_execution_graph.py::test_rejected_high_risk_approval_does_not_execute`

## Scenario 7: Malformed LLM Output Fails Safely

Purpose:

Show that malformed model output does not crash into execution.

Implemented path:

- `LLMProposer` receives malformed JSON, missing fields, or invalid schema values
- proposer returns a malformed proposal with evidence in the rationale
- validator rejects the malformed proposal as an unknown skill
- no real model call is made

Evidence:

- `tests/test_llm_proposer.py::test_non_json_text_returns_malformed_proposal_with_evidence`
- `tests/test_llm_proposer.py::test_missing_required_fields_returns_malformed_proposal_with_evidence`
- `tests/test_llm_proposer.py::test_schema_invalid_output_returns_malformed_proposal_with_evidence`

## Demo Choice

Sprint 5 keeps these scenarios documentation-only. A separate demo script would
not add new evidence beyond the existing focused tests, and adding one would
increase maintenance surface without changing the implemented behavior.
