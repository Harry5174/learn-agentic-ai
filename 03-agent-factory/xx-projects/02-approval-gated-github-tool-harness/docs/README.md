# Documentation Index

This directory is organized so Artifact 3 is easy to read from GitHub and easy
for future IDE agents to navigate.

Artifact 3 — Approval-Gated GitHub Tool Harness started at A3.0 as a baseline
copy and rename from the finalized Artifact 2.2 baseline.

A3.1 is documentation/specification only. It defines the future real
side-effect boundary for an approval-gated GitHub issue-comment tool, but it
does not implement GitHub execution.

A3.2 adds isolated GitHub issue-comment client and side-effect ledger
boundaries.

A3.3 adds exactly one approval-gated local/demo GitHub issue-comment skill
path, `post_github_issue_comment`. It uses validated scalar arguments, a
trusted repository allowlist, explicit approval, an in-memory side-effect
ledger, and fake-client simulated execution.

A3.4 adds adversarial safety tests and documentation for that one fake-client
GitHub comment path. It proves smuggling, unsupported payload, policy bypass,
approval bypass, replay, fake-client failure, network/token, and audit
completeness behavior without adding real GitHub execution.

Artifact 3 still has not implemented real GitHub API execution.

Artifact 2.1 is the Skill Runner API and Demo Surface. It is complete as a
local/demo HTTP surface.

Artifact 2.2 is complete as a local/demo, dry-run, scalar-argument safety
artifact. It validates model-proposed runtime tool arguments before execution
and keeps raw proposed arguments out of `ToolRegistry.execute()`.

## Start Here

- [Project status](status/project-status.md): current Artifact 3 A3.3
  approval-gated fake-client GitHub comment skill status.
- [Artifact 3 real tool boundary](specs/artifact-3-real-tool-boundary.md):
  future real side-effect boundary for approval-gated GitHub issue comments.
- [Skill-runner API demo](demos/skill-runner-api-demo.md): primary Artifact 2.1
  curl walkthrough for `/skills` and `/skill-runs`.
- [Skill-runner API contract](api/skill-runner-api.md): public contract for the
  Artifact 2.1 skill-runner lifecycle.
- [Artifact 2.2 argument validation spec](specs/artifact-2.2-argument-validation.md):
  validated model-proposed scalar tool argument boundary.
- [Adversarial argument validation](adversarial-argument-validation.md):
  E2.3 adversarial boundary evidence for unsafe argument rejection and raw
  argument non-execution.
- [Adversarial GitHub side-effect safety](adversarial-github-side-effect-safety.md):
  A3.4 adversarial evidence for the local/demo GitHub comment side-effect
  boundary.
- [Architecture](architecture/architecture.md): harness flow, trust boundaries,
  graph behavior, state, and persistence limits.
- [Known limitations](status/known-limitations.md): local/demo constraints and
  non-goals.
- [Interview notes](status/interview-notes.md): concise portfolio framing.

## API References

- [Skill-runner API](api/skill-runner-api.md): Artifact 2.1 routes.
- [Task API](api/task-api.md): inherited Artifact 1-style `/tasks` API.

## Demo Guides

- [Skill-runner API demo](demos/skill-runner-api-demo.md): primary Artifact 2.1
  demo guide.
- [Task API demo](demos/task-api-demo.md): inherited task-harness demo.
- [Demo scenarios](demos/demo-scenarios.md): test-backed scenario evidence for
  proposal validation, approval, rejection, and audit behavior.

## Architecture And Safety

- [Architecture](architecture/architecture.md)
- [Security model](architecture/security-model.md)
- [Threat model](architecture/threat-model.md)
- [Audit trail](architecture/audit-trail.md)
- [Tool registry](architecture/tool-registry.md)
- [Local graph harness](architecture/local-graph-harness.md)
- [Checkpoint and resume](architecture/checkpoint-resume.md)
- [Identity resolution](architecture/identity-resolution.md)
- [Policy guard](architecture/policy-guard.md)
- [Public safety](architecture/public-safety.md)

## Status And Portfolio

- [Project status](status/project-status.md)
- [Roadmap](status/roadmap.md)
- [Known limitations](status/known-limitations.md)
- [Interview notes](status/interview-notes.md)
- [Artifact 1 vs Artifact 2](comparisons/artifact-1-vs-artifact-2.md)

## Process And Specs

- [Development rules](process/development-rules.md)
- [Artifact 3 real tool boundary](specs/artifact-3-real-tool-boundary.md)
- [Artifact 2.2 argument validation spec](specs/artifact-2.2-argument-validation.md)
- [Sprint 2 spec](specs/sprint-2-spec.md)
- [Sprint 3 spec](specs/sprint-3-spec.md)
- [Sprint 4 spec](specs/sprint-4-spec.md)
- [Sprint 5 spec](specs/sprint-5-spec.md)
- [Archived Artifact 1 sprint specs](specs/archive/artifact-1-sprint-specs/)

## Constitution

- [Mission](specs/constitution/mission.md)
- [Tech Stack](specs/constitution/tech-stack.md)
- [Roadmap](specs/constitution/roadmap.md)

## Current Boundaries

- A3.0 was only a copied baseline and rename sprint.
- A3.1 was documentation/specification only.
- A3.2 added isolated fake/in-memory supporting boundaries only.
- A3.3 adds one approval-gated fake-client GitHub issue-comment skill.
- A3.4 adds adversarial tests and evidence for the A3.3 fake-client GitHub
  comment boundary.
- Artifact 3 has not implemented real GitHub API execution.
- A3.1 defines the future boundary for an approval-gated GitHub issue-comment
  tool named `post_github_issue_comment`.
- A3.3 wires `FakeGitHubIssueCommentClient` and `InMemorySideEffectLedger`
  into that one local/demo runtime skill path.
- The default HTTP skill-runner API uses fake proposer mode.
- HTTP `proposer_mode: "llm"` is disabled and rejected.
- Invalid-proposal and high-risk skill-run examples are test-backed with
  scenario-configured fake proposer injection when default curl cannot trigger
  them.
- Model-proposed runtime tool arguments are validated against trusted
  `ToolArgumentSpec` metadata before dry-run execution.
- Only registry-declared scalar string/integer/boolean arguments can reach
  execution; object/list/nested payloads and partial acceptance are not
  supported.
- The project remains local/demo, process-local, in-memory, and real-network
  disabled.
