# Roadmap

This roadmap is intentionally narrow. Artifact 05 is an evidence and release
gate layer, not a new automation layer.

## A5.0 - Artifact 04 Closeout Verification And Artifact 05 Scaffold

Status: complete.

A5.0 verifies the Artifact 04 closeout baseline and creates documentation for
future manual smoke evidence. It does not run live GitHub, require credentials,
or add runtime behavior.

## A5.1 - Redacted Evidence Bundle And Safety Checklist

Status: complete.

Define concrete evidence checklist items, redaction proof commands, and review
criteria for accepting or rejecting a future release-gate packet.

Deliverables:

- stricter evidence bundle template
- safe redacted evidence example
- token redaction checklist
- redaction proof requirements
- manual runbook start gate
- live-smoke threat-model hardening

No live GitHub execution is allowed in A5.1.

## A5.2 - Manual Preflight Gate

Status: complete.

Use fake/mocked execution to prove the release-gate checklist can be completed
without credentials or network access.

Required focus:

- zero-HTTP proof for non-allowlisted repo/issue rejection
- redaction proof
- durable approval binding evidence shape
- durable side-effect ledger evidence shape
- audit event evidence shape
- token-present-without-token-value preflight output
- explicit CI block for real-mode preflight
- Artifact 04-backed marker format check

## A5.3 - Manual Real-Mode Smoke

Status: complete.

A5.3 ran one manually approved real GitHub issue-comment smoke against the
allowlisted test issue. It used redacted preflight evidence, the existing
Artifact 04 real adapter path, remote marker lookup before posting, and durable
ledger/audit evidence.

A5.3 did not run replay/no-duplicate testing, did not run non-allowlisted live
testing, and did not perform any GitHub write besides the one issue comment.

Fresh side-effect strategy used:

```text
new_unique_body
```

## A5.4 - Evidence Review And Closeout

Review replay/no-duplicate evidence, negative allowlist evidence, redacted
evidence, pass/fail decision, known limitations, and final closeout report.
Recommend only narrow hardening if the evidence shows a real gap.

## Premature Work To Avoid

Do not add:

- new GitHub adapter
- general GitHub automation
- PR creation
- branch creation
- repo file writes
- workflow dispatch
- issue creation
- labels
- milestones
- operator console
- OAuth
- MCP
- deployment
- production-ready claims
- Digital FTE behavior
- arbitrary repository support
- universal exactly-once claims
