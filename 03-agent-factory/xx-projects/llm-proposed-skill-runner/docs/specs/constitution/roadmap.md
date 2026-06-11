# Constitution Roadmap

This roadmap records sequencing discipline for future coding agents. It does not
start Artifact 2.2.

## Completed Artifact 1

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

## Completed Artifact 2.0

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

## Completed Artifact 2.1

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

## Next Recommended Step: Artifact 2.2

The next implementation step should be:

```text
Validated Model-Proposed Tool Arguments
```

Artifact 2.2 should validate and execute model-proposed runtime tool arguments
against trusted skill/tool metadata before policy, approval, or execution.

Do not skip this step before adding infrastructure integrations.

## Sequencing Rule

Do Artifact 2.2 argument validation before:

- MCP
- database persistence
- OAuth/OIDC
- frontend/demo UI
- real GitHub writes
- live LLM demo mode exposed through HTTP

Argument validation is the missing contract between model-shaped plans and
runtime execution. Infrastructure expansion before that contract would make the
harness harder to reason about.

## Later Possible Extensions

These are future work only:

- explicit live LLM demo mode behind configuration
- durable task/run persistence
- durable audit storage
- OAuth/OIDC identity integration
- MCP tool integration
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
