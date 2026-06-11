# Documentation Index

This directory is organized so Artifact 2.1 is easy to read from GitHub and easy
for future IDE agents to navigate.

Artifact 2.1 is the Skill Runner API and Demo Surface. It is complete as a
local/demo HTTP surface; this documentation packaging patch does not start
Artifact 2.2.

## Start Here

- [Skill-runner API demo](demos/skill-runner-api-demo.md): primary Artifact 2.1
  curl walkthrough for `/skills` and `/skill-runs`.
- [Skill-runner API contract](api/skill-runner-api.md): public contract for the
  Artifact 2.1 skill-runner lifecycle.
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

- The default HTTP skill-runner API uses fake proposer mode.
- HTTP `proposer_mode: "llm"` is disabled and rejected.
- Invalid-proposal and high-risk skill-run examples are test-backed with
  scenario-configured fake proposer injection when default curl cannot trigger
  them.
- Runtime tool argument validation for model-proposed arguments is future
  Artifact 2.2 work.
- The project remains local/demo, process-local, in-memory, and dry-run only.
