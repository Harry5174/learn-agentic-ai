# Manual Real-Mode Smoke Runbook

This runbook is a future A5.x guide. It is not approval to run live GitHub.
A5.0 does not run live GitHub.

## Status

```text
documented for future use
not run in A5.0
requires explicit Product Owner approval in the sprint that runs it
```

## Live-Run Approval Rule

A5.3 may not run live GitHub unless the Product Owner explicitly approves the
live smoke step in that sprint.

No implicit live approval is allowed.

## Allowed Live Operation

The only allowed live operation is:

```text
post one GitHub issue comment
```

The operation must target one allowlisted repository and one allowlisted issue.
Do not use this runbook for PR creation, branch creation, repository file
writes, workflow dispatch, issue creation, labels, milestones, edit, delete, or
arbitrary repository support.

## Preconditions

Before any live smoke:

- confirm Product Owner live-run approval for the current sprint
- verify Artifact 04 final tag points to `9ef8ab8`, unless a newer closeout
  commit was explicitly approved by the Design Supervisor
- verify `.env` is ignored, untracked, and unstaged without printing it
- use a short-lived fine-grained PAT scoped to one allowlisted repository
- grant Issues read/write permission only
- grant no Contents permission
- grant no Actions/workflows permission
- avoid broad repo scope
- keep token server-side only
- keep fake client as default outside the explicit smoke setup
- keep automated tests mocked and credential-free

Safe `.env` tracking checks:

```bash
git status --short -- .env
git ls-files .env
git check-ignore -v .env
```

Do not run `cat .env`, do not source `.env` in automated tests, and do not print
the token.

## Fresh Side-Effect Rule

Before A5.3 live smoke, one of the following must be true:

- fresh test issue with no previous marker
- new unique validated comment body producing a new `side_effect_id`
- explicit reconciliation path if marker already exists

If the target issue already contains the marker and no reconciliation path is
approved, stop.

## Expected Safety Order

The live path must complete local gates before any network call:

```text
1. validate scalar arguments
2. enforce exact repository allowlist
3. compute validated_arguments_hash
4. compute side_effect_id
5. check local durable side-effect ledger
6. suppress if local side effect already succeeded
7. verify durable approval binding for exact side_effect_id + hash
8. verify explicit real-mode config
9. load server-side token
10. list remote issue comments
11. check remote idempotency marker
12. reconcile if marker exists, without posting
13. fail closed for mismatch, ambiguity, lookup failure, or incomplete listing
14. append marker and create one issue comment only when marker is absent
15. persist external comment id/url
16. record durable audit
```

The posted comment body must include:

```html
<!-- agent_factory:v1 side_effect_id=<side_effect_id> args_hash=<validated_arguments_hash> -->
```

The marker is idempotency evidence only. It is not authorization and does not
bypass durable approval binding.

## Negative Allowlist Proof

Before accepting a live-smoke release gate, prove that a non-allowlisted
repository or issue is rejected before network execution.

Preferred evidence:

```text
mocked/spy transport showing zero HTTP calls
```

Do not accept evidence that only shows a GitHub error after an attempted network
call.

## Expected Evidence

Collect only redacted evidence:

- Artifact 04 baseline verification
- live-run approval statement
- allowlisted repository and issue number
- side effect id
- validated arguments hash
- durable approval binding evidence
- durable side-effect ledger evidence
- remote marker lookup evidence
- external comment id/url if a post occurs
- durable audit event names
- zero-HTTP proof for negative allowlist
- redaction proof
- `.env` ignored/untracked proof

Do not collect token values, Authorization headers, `.env` contents, raw
unredacted transport exceptions, or realistic-looking secrets.

