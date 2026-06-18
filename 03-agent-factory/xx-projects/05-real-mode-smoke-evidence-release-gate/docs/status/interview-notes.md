# Interview Notes

## One-Minute Explanation

Artifact 05 is the release-gate layer after the approval-gated real GitHub
comment adapter. Artifact 04 proved the narrow real-mode path with fake/mocked
automated tests and a disabled manual smoke guide. Artifact 05 defines what
redacted evidence must exist before anyone can claim that one manual real-mode
smoke run was safely performed.

The important idea is unchanged:

```text
The LLM proposes.
The harness decides.
```

The model never directly calls GitHub, supplies credentials, enables real mode,
widens allowlists, or authorizes side effects.

Every sprint is spec-driven and test-driven. Before implementation, the
IDE/Codex agent reviews the relevant specs, status docs, and
constitution/process rules, then states exactly which files were reviewed when
the full spec set is too large.

Artifact 05 records those local rules in `docs/process/development-rules.md`
and `docs/specs/constitution/README.md`.

## What Artifact 05 Adds

Artifact 05 adds documentation for:

- the Artifact 04 closeout baseline
- explicit Product Owner live-run approval
- redacted evidence bundle structure
- token redaction checklist
- live-smoke threat model
- fresh side-effect rule before live smoke
- zero-HTTP proof for negative allowlist tests
- manual-only release-gate block conditions

It does not add a new adapter or runtime path.

Artifact 05 intentionally has no `src/app` package. That is part of the design:
Artifact 04 owns runtime execution, while Artifact 05 owns release-gate docs,
redacted evidence structure, and offline preflight helpers.

## What A5.1 Adds

A5.1 makes the evidence system stricter before any live smoke is allowed:

- safe placeholders instead of realistic secret-looking examples
- explicit token-presence recording without token values
- redaction proof requirements
- generated evidence/log scan guidance
- zero-network proof requirements for negative allowlist tests
- future A5.3 start gates
- threat-model coverage for false-positive evidence and operator copying
  mistakes

A5.1 remains non-live. It prepares the evidence packet shape; it does not
claim that the live smoke happened.

## What A5.2 Adds

A5.2 adds a test-backed offline preflight gate. It verifies that fake mode can
pass without a token, real-mode preflight requires explicit opt-in, CI blocks
real-mode preflight, token presence is reported without the token value,
allowlist failures attempt zero network calls, fresh side-effect strategy is
declared, and the marker format matches Artifact 04.

A5.2 remains non-live. It does not call GitHub and does not prove that a real
comment was posted.

## What A5.3 Adds

A5.3 completes one controlled, manually approved real GitHub issue-comment
smoke execution with redacted evidence. It posts exactly one comment to the
allowlisted test issue through the existing Artifact 04 real adapter path.

The A5.3 evidence records:

- Product Owner live-run approval
- redacted preflight output
- fresh side-effect strategy `new_unique_body`
- remote marker lookup before posting
- marker absent before the create call
- comment id and comment URL
- durable ledger status `succeeded`
- durable audit event sequence

A5.3 does not run replay/no-duplicate testing or non-allowlisted live testing.
A5.4 remains responsible for those checks and the final release-gate report.

## What To Highlight

- The fake client remains the default.
- Real mode is explicit and manual.
- No CI live GitHub execution is allowed.
- A5.3 needs explicit Product Owner approval before any live run.
- A5.1 hardens redaction and evidence readiness only.
- A5.2 is the offline manual preflight gate.
- A5.3 is the controlled manual live-smoke evidence packet.
- The release gate must prove repository allowlist rejection before network.
- The evidence bundle must include redaction proof.
- The scope remains one GitHub operation: post issue comment.

## What Not To Overclaim

- Not production-ready.
- Not arbitrary GitHub automation.
- Not a universal exactly-once guarantee.
- Not OAuth, MCP, deployment, or operator UI.
- Not a live smoke execution in A5.0 or A5.1.
- Not a live smoke execution in A5.2.
- Not proof that replay/no-duplicate or non-allowlisted live testing has run.
