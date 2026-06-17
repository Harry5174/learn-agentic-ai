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

Use fake/mocked execution to prove the release-gate checklist can be completed
without credentials or network access.

Required focus:

- zero-HTTP proof for non-allowlisted repo/issue rejection
- redaction proof
- durable approval binding evidence shape
- durable side-effect ledger evidence shape
- audit event evidence shape

## A5.3 - Manual Real-Mode Smoke

Possible future scope only if the Product Owner explicitly approves the live
smoke step in that sprint.

No implicit live approval is allowed.

Before the live run, one of the following must be true:

- fresh test issue with no previous marker
- new unique validated comment body producing a new `side_effect_id`
- explicit reconciliation path if marker already exists

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
