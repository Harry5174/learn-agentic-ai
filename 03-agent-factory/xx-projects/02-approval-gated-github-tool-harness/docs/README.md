# Documentation Index

This directory is organized so Artifact 3 is easy to read from GitHub and easy
for future IDE agents to navigate.

Artifact 3 — Approval-Gated GitHub Tool Harness is currently in A3.0 baseline
copy and rename status only. It was copied from the finalized Artifact 2.2
baseline.

Artifact 2.2 remains the completed dry-run scalar argument validation artifact.
The current Artifact 3 baseline still inherits Artifact 2.2 local/demo dry-run
scalar argument validation behavior and has not yet implemented real GitHub
side effects.

Artifact 2.1 is the Skill Runner API and Demo Surface. It is complete as a
local/demo HTTP surface.

Artifact 2.2 is complete as a local/demo, dry-run, scalar-argument safety
artifact. It validates model-proposed runtime tool arguments before execution
and keeps raw proposed arguments out of `ToolRegistry.execute()`.

## Start Here

- [Project status](status/project-status.md): current Artifact 3 A3.0 baseline
  copy status.
- [Skill-runner API demo](demos/skill-runner-api-demo.md): primary Artifact 2.1
  curl walkthrough for `/skills` and `/skill-runs`.
- [Skill-runner API contract](api/skill-runner-api.md): public contract for the
  Artifact 2.1 skill-runner lifecycle.
- [Artifact 2.2 argument validation spec](specs/artifact-2.2-argument-validation.md):
  validated model-proposed scalar tool argument boundary.
- [Adversarial argument validation](adversarial-argument-validation.md):
  E2.3 adversarial boundary evidence for unsafe argument rejection and raw
  argument non-execution.
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

- A3.0 is only a copied baseline and rename sprint.
- Artifact 3 has not yet implemented real GitHub side effects.
- A later Artifact 3 sprint may introduce an approval-gated GitHub
  issue-comment tool named `post_github_issue_comment`.
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
- The project remains local/demo, process-local, in-memory, and dry-run only.
