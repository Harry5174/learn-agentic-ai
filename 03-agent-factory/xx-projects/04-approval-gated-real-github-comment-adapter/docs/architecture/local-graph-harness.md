# Local Graph Harness Design

## Purpose

This document distinguishes the inherited deterministic task graph from the
Artifact 1 skill execution graph.

## Inherited Task Graph

The inherited task graph remains in:

```text
src/app/graph/
```

It powers the current FastAPI task API.

Flow:

```text
Identity
-> deterministic tool selection
-> policy guard
-> conditional routing
-> audit
-> dry-run execution or denial or approval pause
```

Current simple mapping:

- `inspect` / `issue` / `issues` -> `inspect_sandbox_issues`
- `draft` / `comment` -> `draft_issue_comment`
- `trigger` / `workflow` -> `trigger_workflow_dry_run`

## Artifact 1 Skill Execution Graph

The Artifact 1 skill graph lives in:

```text
src/app/skill_graph/
```

Flow:

```text
task
-> proposer
-> SkillProposal
-> ProposalValidator
-> policy guard
-> approval gate when required
-> dry-run tools
-> audit
-> SkillRunResult
```

## Approval Pause

For high-risk paths:

- an approval request is created
- status becomes `paused_for_approval`
- tool results remain empty
- `tool_executed` audit is absent before approval
- approval or rejection resumes checkpointed state

## Boundary

- FastAPI routes currently use the inherited task graph.
- Artifact 1 skill-runner behavior is exercised through `SkillGraphService` and tests.
- Checkpointing uses `InMemorySaver`.
- Durable persistence is not implemented.
- No OAuth/JWT.
- No MCP.
- No external HTTP calls.
- No real GitHub/workflow execution.

## Current Limitation

The skill graph validates proposed skill, step, tool, scope, and risk structure.
It still uses harness-owned default arguments for dry-run tool execution.
