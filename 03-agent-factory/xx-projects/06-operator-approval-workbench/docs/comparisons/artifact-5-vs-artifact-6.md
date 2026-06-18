# Artifact 5 vs Artifact 6

## Artifact 5

Artifact 5 is the release-gate evidence layer for the Artifact 4 runtime.

It provides:

- redacted live-smoke evidence
- offline preflight proof
- replay/no-duplicate evidence
- negative zero-network proof
- final release-gate report
- token and `.env` safety documentation

Artifact 5 intentionally has no `src/app` runtime package.

## Artifact 6

Artifact 6 will become the operator approval console/workbench artifact.

A6.0 uses Artifact 5 as evidence context only. It does not copy Artifact 5
helpers as runtime, does not add live GitHub behavior, and does not treat
release-gate docs as application code.

## Boundary

Artifact 5 answers:

```text
How do we prove one controlled real-mode smoke path safely and with redacted evidence?
```

Artifact 6 asks:

```text
How should a human operator review and decide high-risk actions before execution?
```

The answer in A6.0 is architecture only. Implementation starts later.
