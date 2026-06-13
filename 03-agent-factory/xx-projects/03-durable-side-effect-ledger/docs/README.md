# Documentation Index

This directory is organized so Artifact 4 is easy to review from GitHub and easy for future IDE agents to navigate.

Artifact 4 - Durable Side-Effect Ledger and Approval Binding starts at A4.0 as a baseline copy from the completed Artifact 3 project.

A4.0 is copy/rename plus documentation/specification only. It defines durable-state semantics, persistence boundaries, approval binding requirements, lifecycle statuses, and restart-replay proof requirements before any SQLite runtime code is implemented.

A4.0 has not implemented durable SQLite persistence. It has not implemented durable approval binding. It has not implemented a durable audit store. It has not changed graph, service, API, approval, or tool behavior. It has not enabled real GitHub execution.

## Start Here

- [Project status](status/project-status.md): current A4.0 baseline/spec status.
- [Artifact 4 durable side-effect ledger spec](specs/artifact-4-durable-side-effect-ledger.md): durable-state design and future acceptance requirements.
- [Persistence boundary](architecture/persistence-boundary.md): architecture boundary between process-local state, SQLite, and fake-client execution.
- [Artifact 3 vs Artifact 4](comparisons/artifact-3-vs-artifact-4.md): source baseline and durable-state design comparison.
- [Known limitations](status/known-limitations.md): local/demo constraints and non-goals.
- [Roadmap](status/roadmap.md): A4.x sequencing.
- [Interview notes](status/interview-notes.md): concise portfolio framing.

## Inherited Artifact 3 Evidence

The copied project still contains Artifact 3 demos, specs, adversarial evidence, and API references. Those pages are historical/source-baseline context unless an A4.0 status page says otherwise.

Useful inherited references:

- [GitHub comment tool demo](demos/github-comment-tool-demo.md): inherited Artifact 3 local/demo fake-client walkthrough.
- [Adversarial GitHub side-effect safety](adversarial-github-side-effect-safety.md): inherited evidence for the fake-client side-effect boundary.
- [Artifact 3 real tool boundary](specs/artifact-3-real-tool-boundary.md): historical Artifact 3 boundary design.
- [Skill-runner API contract](api/skill-runner-api.md): inherited local/demo API contract.
- [Architecture](architecture/architecture.md): inherited harness architecture and process-local persistence limits.

## API References

- [Skill-runner API](api/skill-runner-api.md): inherited local/demo skill-runner lifecycle.
- [Task API](api/task-api.md): inherited Artifact 1-style `/tasks` API.

## Architecture And Safety

- [Persistence boundary](architecture/persistence-boundary.md)
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
- [Artifact 3 vs Artifact 4](comparisons/artifact-3-vs-artifact-4.md)
- [Artifact 2 vs Artifact 3](comparisons/artifact-2-vs-artifact-3.md)
- [Artifact 1 vs Artifact 2](comparisons/artifact-1-vs-artifact-2.md)

## Process And Specs

- [Artifact 4 durable side-effect ledger spec](specs/artifact-4-durable-side-effect-ledger.md)
- [Development rules](process/development-rules.md)
- [Artifact 3 real tool boundary](specs/artifact-3-real-tool-boundary.md)
- [Artifact 2.2 argument validation spec](specs/artifact-2.2-argument-validation.md)

## Current Boundaries

- A4.0 is baseline/spec only.
- Artifact 4 was copied from completed Artifact 3.
- The copied runtime still inherits Artifact 3 fake-client local/demo behavior.
- SQLite persistence is planned but not implemented.
- Durable approval binding is planned but not implemented.
- Durable audit evidence is planned but not implemented.
- Real GitHub execution remains out of scope.
- GitHub token loading remains out of scope.
- The project remains local/demo, process-local, fake-client-only, and real-network disabled.
