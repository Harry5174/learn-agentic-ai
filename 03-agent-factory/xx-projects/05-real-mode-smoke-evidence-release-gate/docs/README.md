# Artifact 05 Documentation

This directory defines the manual smoke-evidence release gate for Artifact 05.
It continues the Artifact 04 safety model without adding runtime behavior.

## Read First

- [Artifact 05 spec](specs/artifact-5-real-mode-smoke-evidence-release-gate.md)
- [Manual preflight gate](demos/preflight-gate.md)
- [Manual real-mode smoke runbook](demos/manual-real-mode-smoke-runbook.md)
- [Evidence bundle template](demos/evidence-bundle-template.md)
- [Redacted evidence example](demos/redacted-evidence-example.md)
- [Live smoke threat model](safety/live-smoke-threat-model.md)
- [Token redaction checklist](safety/token-redaction-checklist.md)
- [Project status](status/project-status.md)
- [Known limitations](status/known-limitations.md)
- [Roadmap](status/roadmap.md)
- [Interview notes](status/interview-notes.md)

## Practical Constitution

Artifact 05 follows the explicit constitution-style files inherited in Artifact
04:

- `docs/specs/constitution/mission.md`
- `docs/specs/constitution/roadmap.md`
- `docs/specs/constitution/tech-stack.md`
- `docs/process/development-rules.md`

It also follows the practical constitution established by the Artifact 04
README, spec, remote idempotency documentation, manual smoke guide, status
notes, known limitations, roadmap, and interview notes.

## Current Runtime Boundary

The default runtime remains:

- local/demo
- fake-client default
- approval-gated
- policy-checked
- durable-state aware
- no token required
- no live GitHub execution
- no CI live GitHub execution

Real mode remains explicit and manual. A future live smoke run requires explicit
Product Owner approval in that sprint.
