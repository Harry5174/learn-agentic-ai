# Constitution Roadmap

This roadmap records sequencing discipline for future coding agents.

## Completed Artifact 1 - Identity-Aware Stateful Agent Harness

Artifact 1 proved the base execution harness:

- server-derived local demo identity
- deterministic task-to-tool selection
- deterministic policy guard
- approval gate for high-risk tools
- controlled dry-run tools
- structured audit trail
- checkpointed resume behavior
- local/demo FastAPI task API
- in-memory rate limiting

Artifact 1's key lesson:

```text
Do not let request bodies control identity, policy, approval, or execution.
```

## Completed Artifact 2.0 - LLM-Proposed, Harness-Controlled Skill Runner

Artifact 2.0 added model-shaped skill proposals while keeping authority in the
harness:

- `SkillSpec`, `SkillStep`, and `SkillProposal` contracts
- trusted `SkillRegistry`
- deterministic `ProposalValidator`
- deterministic fake proposer scenarios
- optional provider-neutral `LLMProposer` boundary with mocked-client tests
- checkpointed skill execution graph
- policy, approval, dry-run tools, and audit for skill proposals

Artifact 2.0's key lesson:

```text
The proposer proposes. The harness decides.
```

## Completed Artifact 2.1 - Skill Runner API and Demo Surface

Artifact 2.1 exposes the skill-runner lifecycle through the local/demo FastAPI
surface:

- `GET /skills`
- `POST /skill-runs`
- `GET /skill-runs/{run_id}`
- `POST /skill-runs/{run_id}/approve`
- `POST /skill-runs/{run_id}/reject`
- `GET /skill-runs/{run_id}/audit`

Artifact 2.1 supports:

- registered skill listing
- low-risk skill-run creation
- invalid proposal rejection
- high-risk approval pause
- approved high-risk resume
- rejected high-risk prevention
- audit retrieval
- server-derived identity
- safe public schemas
- fake proposer default over HTTP
- disabled/rejected HTTP LLM mode

## Completed Artifact 2.2 - Validated Model-Proposed Tool Arguments

Artifact 2.2 validates model-proposed runtime tool arguments while preserving
the harness boundary:

```text
A model-shaped SkillProposal can include runtime tool arguments,
but only registry-declared, scalar, validator-normalized arguments can reach
dry-run execution.
```

Artifact 2.2 includes:

- E2.0 - argument contract schemas and spec
- E2.1 - validator argument checks
- E2.2 - execution with validated arguments only
- E2.3 - adversarial argument-boundary suite and docs

Raw proposed arguments must never flow directly into `ToolRegistry.execute()`.

## Artifact 3 A3.0 - Baseline Copy and Rename

A3.0 creates Artifact 3 — Approval-Gated GitHub Tool Harness by copying the
finalized Artifact 2.2 project into a new sibling project folder and updating
project identity/documentation only.

Artifact 2.2 remains the completed dry-run scalar argument validation artifact.
The current Artifact 3 baseline still inherits Artifact 2.2 local/demo dry-run
scalar argument validation behavior.

A3.0 has not implemented real GitHub side effects, a GitHub client,
side-effect ledger, `side_effect_id`, `post_github_issue_comment`, real-mode
configuration, live LLM mode, OAuth/OIDC, MCP, database persistence, or
frontend behavior.

## Next Recommended Step

Prepare an explicit A3.1/A3.2 proposal before adding any GitHub side-effect
behavior.

## Sequencing Rule

Do not add these as incidental cleanup:

- MCP
- database persistence
- OAuth/OIDC
- frontend/demo UI
- real GitHub writes
- live LLM demo mode exposed through HTTP

Any future infrastructure expansion must preserve validation, approval, audit,
redaction, and raw-argument non-execution boundaries.

## Later Possible Extensions

These are future work only:

- approval-gated GitHub issue-comment tool named `post_github_issue_comment`
- scalar arguments for that future tool: `repository`, `issue_number`, and
  `comment_body`
- explicit live LLM demo mode behind configuration
- durable task/run persistence
- durable audit storage
- OAuth/OIDC identity integration
- MCP tool integration
- richer argument schemas after a separate threat-modeling pass
- frontend or demo UI
- real GitHub write tools behind strong approval and audit gates
- deployment demo

Future agents should keep these as separate, explicit project steps. They should
not be introduced as incidental cleanup while editing docs, schemas, routes, or
tests.

## Premature Work To Avoid

Avoid:

- provider frameworks before a clear live-LLM demo requirement
- database work before state and audit contracts are ready
- real side-effecting tools before validation and approval boundaries are
  stronger
- frontend work before the API demo story is stable
- production-readiness claims
- prompt-only safety controls
