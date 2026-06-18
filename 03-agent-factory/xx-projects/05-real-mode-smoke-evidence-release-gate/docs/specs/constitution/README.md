# Artifact 05 Constitution

Artifact 05 inherits the Artifact 04 safety constitution and narrows it to the
release-gate evidence layer.

## Mission

Prepare reviewable, redacted evidence for one future approval-gated real
GitHub issue-comment smoke run without widening the runtime capability.

The thesis remains:

```text
The LLM proposes.
The harness decides.
```

## Boundaries

- Fake/default behavior remains safe.
- Real mode remains explicit and manual.
- A5.2 preflight is offline and non-live.
- A5.3 live smoke requires separate Product Owner approval in that sprint.
- The only future live operation in scope is one issue comment.
- Evidence must be redacted and must not contain token values.
- `.env` must remain ignored and untracked.

## No `src/app` By Design

Artifact 05 intentionally has no `src/app` runtime package. The application
runtime, GitHub client boundary, real-mode config, token provider, durable
ledger, and remote marker logic belong to Artifact 04.

Artifact 05 contains docs plus isolated `tools/` and `tests/` helpers for
offline release-gate validation. This separation prevents the evidence sprint
from silently changing the real GitHub execution path.

## Sequencing

- A5.0: scaffold the Artifact 05 release-gate documentation.
- A5.1: harden redacted evidence and safety checklists.
- A5.2: add offline manual preflight evidence.
- A5.3: controlled live smoke only after Design Supervisor approval of A5.2
  and explicit Product Owner approval for live execution.
- A5.4: review redacted evidence, replay/no-duplicate evidence, negative
  allowlist evidence, and final closeout.

## Inherited Runtime Contracts

Artifact 05 relies on Artifact 04 for:

- server-owned repository allowlists
- explicit real-mode config
- server-side token provider boundary
- durable approval binding
- durable side-effect ledger
- remote marker lookup and reconciliation
- fail-closed marker ambiguity handling
- durable audit evidence

Artifact 05 documents and validates the release gate around those contracts; it
does not replace or reimplement them.
