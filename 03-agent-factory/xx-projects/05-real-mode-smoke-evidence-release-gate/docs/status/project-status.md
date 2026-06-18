# Project Status

**Artifact:** 05

**Title:** Artifact 05 - Real-Mode Smoke Evidence and Release Gate

**Current sprint:** A5.4 - Replay, Negative Case, and Final Release Gate Report

**Status:** A5.0 scaffold complete. A5.1 redacted evidence and safety
checklist hardening complete. A5.2 manual preflight gate complete. A5.3
controlled live smoke complete. A5.4 final release-gate report complete.

## Current Claim

Artifact 05 defines a controlled manual release gate for verifying one
approval-gated real GitHub issue-comment side effect with redacted evidence.
The fake client remains default, real mode remains explicit, and any live
GitHub smoke run requires explicit Product Owner approval in the sprint that
runs it.

A5.3 demonstrated one controlled, manually approved real GitHub issue-comment
smoke execution with redacted evidence. It posted exactly one issue comment to
the allowlisted test issue. It did not run replay/no-duplicate testing, did not
run non-allowlisted live testing, and did not perform any GitHub write besides
the one issue comment.

A5.4 added the final release-gate evidence report. It used offline/mocked/spy
replay proof and zero-network negative allowlist proof. Real replay against
GitHub was not approved and was not run. No second GitHub comment was posted.

## Completed A5.0 Scope

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

## A5.1 Scope

A5.1 completed:

- strengthens the evidence bundle template
- adds explicit redaction proof requirements
- defines safe token-presence recording
- separates intentional safety-documentation pattern matches from generated
  evidence/log scans
- strengthens manual runbook preconditions for A5.3
- strengthens the threat model for evidence leakage, false-positive proof, and
  accidental network execution

A5.1 does not:

- run live GitHub
- require credentials
- read `.env`
- add runtime execution behavior
- create a new GitHub adapter
- prove that a live smoke run occurred

## A5.2 Scope

A5.2 completed:

- adds an isolated Artifact 05 preflight helper
- adds tests for fake mode, explicit real-mode opt-in, CI blocking,
  token-presence redaction, allowlist checks, fresh side-effect strategy, and
  marker-format alignment
- keeps `network_calls_attempted` at `0` for all preflight paths
- uses the Artifact 04 token environment name `AGENT_FACTORY_GITHUB_TOKEN`
- documents preflight output as redacted evidence, not live smoke proof

A5.2 does not:

- run live GitHub
- require credentials
- read `.env`
- change Artifact 04 runtime behavior
- create a new GitHub adapter
- prove that a real GitHub comment was posted

## A5.3 Scope

A5.3 completed:

- recorded explicit Product Owner live-run approval
- used fresh side-effect strategy `new_unique_body`
- ran the redacted A5.2 preflight gate
- loaded the token for local smoke using the approved test-only `.env`
  exception without printing or recording the token value
- used the existing Artifact 04 approval-gated real adapter path
- performed remote marker lookup before posting
- posted exactly one GitHub issue comment after the marker was absent
- recorded the comment id, comment URL, durable ledger success, and audit
  event sequence
- ran redaction checks against the evidence bundle

A5.3 does not:

- run replay/no-duplicate testing
- run non-allowlisted live testing
- add a new GitHub adapter or live runner
- perform any GitHub write besides the one issue comment
- claim production readiness or arbitrary GitHub automation

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
Artifact 05 final closeout review and optional tag decision
```
