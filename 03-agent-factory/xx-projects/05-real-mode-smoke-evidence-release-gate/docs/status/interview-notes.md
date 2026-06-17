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

## What To Highlight

- The fake client remains the default.
- Real mode is explicit and manual.
- No CI live GitHub execution is allowed.
- A5.3 needs explicit Product Owner approval before any live run.
- The release gate must prove repository allowlist rejection before network.
- The evidence bundle must include redaction proof.
- The scope remains one GitHub operation: post issue comment.

## What Not To Overclaim

- Not production-ready.
- Not arbitrary GitHub automation.
- Not a universal exactly-once guarantee.
- Not OAuth, MCP, deployment, or operator UI.
- Not a live smoke execution in A5.0.
