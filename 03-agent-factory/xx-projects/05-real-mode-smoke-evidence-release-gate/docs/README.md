# Artifact 05 Documentation

This directory defines the manual smoke-evidence release gate for Artifact 05.
It continues the Artifact 04 safety model without adding runtime behavior.

## Read First

- [Artifact 05 spec](specs/artifact-5-real-mode-smoke-evidence-release-gate.md)
- [Development rules](process/development-rules.md)
- [Artifact 05 constitution](specs/constitution/README.md)
- [Manual preflight gate](demos/preflight-gate.md)
- [A5.3 controlled live-smoke evidence](evidence/a5.3-controlled-live-smoke/README.md)
- [A5.4 final release-gate report](evidence/a5.4-final-release-gate-report/README.md)
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

Artifact 05 follows local process and constitution files that preserve the
Artifact 04 runtime boundary:

- [development rules](process/development-rules.md)
- [Artifact 05 constitution](specs/constitution/README.md)

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
- no live GitHub execution except the completed A5.3 manually approved smoke
- no CI live GitHub execution

Real mode remains explicit and manual. A5.3 completed one manually approved
real GitHub issue-comment smoke run with redacted evidence. A5.4 completed the
final release-gate report using offline/mocked/spy replay proof and
zero-network negative allowlist proof. Real replay against GitHub was not run.

Artifact 05 intentionally has no `src/app` package. Runtime code remains in
Artifact 04; Artifact 05 contains docs plus isolated release-gate helpers under
`tools/` and tests under `tests/`.
