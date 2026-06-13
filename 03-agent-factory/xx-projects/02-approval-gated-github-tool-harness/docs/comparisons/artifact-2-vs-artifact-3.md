# Artifact 2 vs Artifact 3

## Summary

Artifact 2 proves the model-proposed skill runner.

Artifact 3 applies that runner shape to one approval-gated local/demo GitHub
issue-comment path.

The shared principle is:

```text
The LLM proposes.
The harness validates, authorizes, approval-gates, executes, and audits.
```

## Artifact 2: Skill Runner Boundary

Artifact 2 introduced the skill-runner layer:

- structured `SkillSpec`, `SkillStep`, and `SkillProposal` contracts
- trusted `SkillRegistry`
- deterministic `ProposalValidator`
- deterministic `FakeProposer`
- optional provider-neutral `LLMProposer` tested with mocked clients
- checkpointed skill execution graph
- skill-runner HTTP lifecycle
- scalar runtime argument validation
- raw proposed argument non-execution
- adversarial argument-boundary evidence

Artifact 2.2's key contribution is that model-shaped proposals may include
runtime arguments, but only registry-declared scalar arguments accepted by the
validator can reach controlled dry-run execution.

## Artifact 3: Approval-Gated GitHub Tool Harness

Artifact 3 starts from the completed Artifact 2.2 baseline and focuses on a
narrow GitHub side-effect boundary.

It adds:

- A3.1 real side-effect boundary specification
- A3.2 GitHub issue-comment client protocol, fake client, request/result/failure
  schemas, side-effect id helpers, and in-memory ledger boundary
- A3.3 one approval-gated local/demo GitHub issue-comment skill path:
  `post_github_issue_comment`
- A3.4 adversarial side-effect safety suite
- A3.5 demo and portfolio packaging

The implemented Artifact 3 path is:

```text
model-shaped proposal
-> proposal validation
-> scalar argument validation
-> repository policy
-> approval gate
-> side_effect_id computation
-> in-memory ledger check
-> fake GitHub client
-> audit evidence
```

## What Changed From Artifact 2

Artifact 2 demonstrated generic skill-runner safety.

Artifact 3 adds a concrete side-effect-shaped path:

- GitHub issue-comment request/result/failure schemas
- `GitHubIssueCommentClient` protocol
- `FakeGitHubIssueCommentClient`
- `validated_arguments_hash`
- deterministic `side_effect_id`
- `InMemorySideEffectLedger`
- repository allowlist policy
- GitHub-comment-specific audit evidence
- adversarial tests for credentials, client config, repository bypass,
  approval bypass, replay, and fake-client failure behavior

## What Stayed The Same

Artifact 3 keeps the Artifact 2 trust boundary:

- the model does not authorize
- the model does not approve
- the model does not select arbitrary tools
- raw proposed arguments do not execute directly
- high-risk work pauses before execution
- identity is server-derived
- policy is deterministic
- audit evidence is structured

## What Artifact 3 Still Does Not Do

Artifact 3 is still local/demo only.

It does not implement:

- real GitHub API adapter
- GitHub token loading
- arbitrary repository targeting
- workflow dispatch
- PR creation
- branch creation
- issue creation
- repo file writes
- durable audit storage
- durable ledger storage
- OAuth/OIDC
- MCP
- frontend
- production deployment

## Portfolio Framing

Artifact 2 answers:

```text
Can a harness accept model-shaped skill plans without trusting the model to
authorize or execute?
```

Artifact 3 answers:

```text
Can that harness shape be extended toward a real side-effect boundary while
keeping execution fake-client-only, approval-gated, idempotency-checked, and
audited?
```

The answer in Artifact 3 is yes, within local/demo scope. It is not a real
GitHub write system.
