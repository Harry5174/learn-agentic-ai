# Artifact 05 - Real-Mode Smoke Evidence and Release Gate

Artifact 05 defines the manual release gate for collecting redacted evidence
from one approval-gated real GitHub issue-comment side effect.

This artifact does not add runtime behavior. It preserves the Artifact 04
boundary: the fake client remains the default, real mode remains explicit, and
live GitHub execution requires separate Product Owner approval in the sprint
that performs it.

The core thesis remains:

```text
The LLM proposes.
The harness decides.
```

The harness owns identity, authorization, validation, policy, approval, durable
state, idempotency, audit, real-tool boundaries, and failure behavior.

## Process Invariant

Every sprint must follow spec-driven and test-driven development. Before
implementation, the IDE/Codex agent must review the relevant specs, status
docs, and constitution/process rules. If the full spec set is too large, the
agent must target the specific relevant specs and state exactly which files
were reviewed. No sprint should proceed from implementation intuition alone.

## What Artifact 05 Is

Artifact 05 is a documentation and evidence-planning artifact for:

- verifying the Artifact 04 closeout baseline
- defining the release gate for a future manual real-mode smoke run
- documenting safety invariants before any live execution
- defining a redacted evidence bundle structure
- making block conditions explicit

The intended live operation in a future sprint remains exactly one GitHub
operation:

```text
post one GitHub issue comment
```

## What Artifact 05 Is Not

Artifact 05 is not:

- a new GitHub adapter
- general GitHub automation
- PR creation
- branch creation
- repository file writes
- workflow dispatch
- issue creation
- labels or milestones
- an operator console
- OAuth
- MCP
- deployment
- a production-ready system
- Digital FTE behavior
- arbitrary repository support
- a universal exactly-once guarantee

## Current Status

A5.0 creates the documentation scaffold only. No live GitHub execution was run
for this scaffold sprint, no credentials were required, and no `.env` contents
were read.

## Documentation

Use [docs/README.md](docs/README.md) as the documentation index.

Key entry points:

- [Artifact 05 spec](docs/specs/artifact-5-real-mode-smoke-evidence-release-gate.md)
- [Manual real-mode smoke runbook](docs/demos/manual-real-mode-smoke-runbook.md)
- [Evidence bundle template](docs/demos/evidence-bundle-template.md)
- [Redacted evidence example](docs/demos/redacted-evidence-example.md)
- [Live smoke threat model](docs/safety/live-smoke-threat-model.md)
- [Token redaction checklist](docs/safety/token-redaction-checklist.md)
- [Project status](docs/status/project-status.md)
- [Known limitations](docs/status/known-limitations.md)
- [Roadmap](docs/status/roadmap.md)
- [Interview notes](docs/status/interview-notes.md)

## Artifact 04 Baseline Rule

The final Artifact 04 tag must point to `9ef8ab8`, unless a newer closeout
commit has been explicitly approved by the Design Supervisor.
