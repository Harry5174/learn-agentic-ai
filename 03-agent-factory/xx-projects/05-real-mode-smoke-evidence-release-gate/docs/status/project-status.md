# Project Status

**Artifact:** 05

**Title:** Artifact 05 - Real-Mode Smoke Evidence and Release Gate

**Current sprint:** A5.0 - Artifact 04 Closeout Verification and Artifact 05
Scaffold

**Status:** A5.0 scaffold created. Documentation only. No runtime behavior was
added.

## Current Claim

Artifact 05 defines a controlled manual release gate for verifying one
approval-gated real GitHub issue-comment side effect with redacted evidence.
The fake client remains default, real mode remains explicit, and any live
GitHub smoke run requires explicit Product Owner approval in the sprint that
runs it.

## A5.0 Scope

A5.0:

- verifies the Artifact 04 closeout baseline
- creates the Artifact 05 documentation scaffold
- defines strict safety invariants
- defines evidence and redaction requirements
- documents manual-only live smoke boundaries
- preserves the Artifact 04 one-operation boundary

A5.0 does not:

- run live GitHub
- require credentials
- read `.env`
- add a new adapter
- add runtime execution behavior
- push or tag

## Methodology Preserved

```text
The LLM proposes.
The harness decides.
```

The harness owns identity, authorization, validation, policy, approval, durable
state, idempotency, audit, real-tool boundaries, and failure behavior.

Every sprint must follow spec-driven and test-driven development. Before
implementation, the IDE/Codex agent must review the relevant specs, status
docs, and constitution/process rules, or state the targeted relevant specs when
the full set is too large. No sprint should proceed from implementation
intuition alone.

## Artifact 04 Closeout Rule

The final Artifact 04 tag must point to `9ef8ab8`, unless a newer closeout
commit has been explicitly approved by the Design Supervisor.

## Recommended Next Step

```text
A5.1 - Redacted Evidence Bundle and Safety Checklist
```
