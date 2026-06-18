# Artifact 05 - Real-Mode Smoke Evidence and Release Gate

## Status

A5.0 created the Artifact 05 documentation scaffold. A5.1 hardened the
redacted evidence bundle, token redaction checklist, manual runbook,
live-smoke threat model, and status wording. A5.2 added an offline manual
preflight gate with tests and redacted output. A5.3 completed one controlled,
manually approved real GitHub issue-comment smoke execution with redacted
evidence.

A5.2 does not run live GitHub, require credentials, inspect `.env`, add a new
adapter, or change Artifact 04 runtime execution behavior. It creates
preflight readiness only.

A5.3 posted exactly one approved real GitHub issue comment to the allowlisted
test issue after preflight and explicit Product Owner approval. A5.3 did not
run replay/no-duplicate testing, did not run non-allowlisted live testing, and
did not perform any GitHub write besides the one issue comment. The read-only
list-comments call was used only for remote marker lookup before posting.

A5.4 completed the final release-gate report using offline/mocked/spy replay
proof and zero-network negative allowlist proof. Real replay against GitHub was
not run, no second GitHub comment was posted, and no non-allowlisted live test
was run.

## Purpose

Controlled manual release gate for verifying one approval-gated real GitHub
issue-comment side effect with redacted evidence.

## Relationship To Artifact 04

Artifact 04 implemented a local/demo approval-gated real GitHub issue-comment
adapter. The fake client remains the default. Explicit real mode can perform
one repository-allowlisted GitHub issue-comment side effect after validated
scalar arguments, durable approval binding, local durable ledger checks, remote
idempotency marker lookup/reconciliation, server-side token loading, and
durable audit recording.

Artifact 05 does not expand that capability. It defines how a future sprint may
collect manual smoke evidence without weakening the Artifact 04 boundaries.

Artifact 05 intentionally has no `src/app` package. The real application
runtime remains in Artifact 04. Artifact 05 docs, `tools/`, and `tests/`
provide the release-gate evidence layer without wiring into runtime execution.

## Artifact 04 Closeout Rule

The final Artifact 04 tag must point to `9ef8ab8`, unless a newer closeout
commit has been explicitly approved by the Design Supervisor.

Do not treat unreviewed later commits as the Artifact 04 final baseline.

## Thesis

```text
The LLM proposes.
The harness decides.
```

The model must never directly execute tools, provide credentials, enable real
mode, bypass policy, authorize side effects, or widen allowlists.

The harness owns:

- identity
- authorization
- validation
- policy
- approval
- durable state
- idempotency
- audit
- real-tool boundaries
- failure behavior

## Process Invariant

Every sprint must follow spec-driven and test-driven development. Before
implementation, the IDE/Codex agent must review the relevant specs, status
docs, and constitution/process rules. If the full spec set is too large, the
agent must target the specific relevant specs and state exactly which files
were reviewed. No sprint should proceed from implementation intuition alone.

Artifact 05 records those rules in:

- [development rules](../process/development-rules.md)
- [Artifact 05 constitution](constitution/README.md)

## A5.0 Scope

A5.0 is documentation/scaffold only:

- verify Artifact 04 closeout and tag state
- create Artifact 05 docs, demos, safety, and status scaffold
- define release-gate evidence requirements
- document redaction requirements
- document manual-only live smoke boundaries
- document block conditions and non-goals

A5.0 does not run live GitHub and does not require credentials.

## A5.x Direction

Sprints may proceed only if separately approved:

- **A5.0 - Artifact 04 Closeout Verification and Artifact 05 Scaffold:**
  completed documentation scaffold.
- **A5.1 - Redacted Evidence Bundle and Safety Checklist:** define concrete
  evidence collection checklists, redaction proof commands, safe placeholders,
  and threat-model evidence requirements.
- **A5.2 - Manual Preflight Gate:** prove the release gate with offline
  preflight validation, redacted output, and no network.
- **A5.3 - Manual Real-Mode Smoke:** completed one live smoke after the
  Product Owner explicitly approved the live step in that sprint.
- **A5.4 - Replay, Negative Evidence, and Closeout:** review replay,
  no-duplicate, negative allowlist, redaction, and final report evidence.
  Completed with offline/mocked/spy proof only.

No A5.x sprint may infer live-run approval from this scaffold.

## Safety Invariants

- fake client remains default
- real mode must be explicit
- manual smoke must be opt-in
- no CI live GitHub execution
- no token in source, docs, logs, evidence, audit rows, exception messages, or
  test snapshots
- `.env` remains ignored and untracked
- token loaded server-side only
- minimum-scope fine-grained PAT only
- one allowlisted repository
- one allowlisted issue
- one GitHub operation: post issue comment
- validated scalar arguments only
- repository allowlist before network
- durable approval binding before network
- durable side-effect ledger before and after execution
- remote marker lookup before posting
- marker found prevents duplicate post
- marker lookup failure fails closed
- durable audit events recorded
- evidence bundle redacted

## Manual Live Smoke Boundary

Manual live smoke is not part of A5.0. A future A5.3 sprint may not run live
GitHub unless the Product Owner explicitly approves the live smoke step in that
sprint.

No implicit live approval is allowed.

The only allowed live side effect remains:

```text
post one GitHub issue comment
```

Do not add PR creation, issue creation, branch writes, repository file writes,
workflow dispatch, labels, milestones, assignees, edit, delete, or arbitrary
repository support.

## Fresh Side-Effect Rule Before Live Smoke

Before A5.3 live smoke, one of the following must be true:

- fresh test issue with no previous marker
- new unique validated comment body producing a new `side_effect_id`
- explicit reconciliation path if marker already exists

If none is true, do not run the live smoke.

## Negative Allowlist Evidence Rule

The non-allowlisted repo/issue test must prove rejection happened before
network execution.

Preferred evidence:

```text
mocked/spy transport showing zero HTTP calls
```

The release gate must reject evidence that only proves an error occurred after a
network attempt.

## Evidence Bundle Requirements

A release-gate evidence bundle must include:

- Artifact 04 baseline and tag verification
- branch and workspace status
- explicit Product Owner live-run approval for the sprint that runs live smoke
- A5.1 checklist completion
- A5.2 preflight completion
- A5.2 redacted preflight output
- `.env` ignored/untracked proof without printing `.env`
- minimum-scope token checklist confirmation without token values
- token presence recorded only as a redacted placeholder
- repository and issue allowlist confirmation
- fresh side-effect rule evidence
- durable approval binding evidence
- durable side-effect ledger evidence
- remote marker lookup evidence before post
- marker-found duplicate-prevention evidence or marker-absent post evidence
- durable audit event evidence
- external comment id/url if a live comment is posted
- negative allowlist zero-network proof
- replay/no-duplicate evidence
- redaction proof
- block-condition review

The evidence bundle must include either:

```text
redaction test output
```

or:

```text
grep output proving no token-like values appear in docs/evidence/logs
```

Evidence must not include token values, Authorization header values, raw
unredacted transport exceptions, `.env` contents, or realistic-looking secrets.

Safety docs may intentionally mention token-detection strings. Redaction proof
for a live evidence packet must target generated evidence/log artifacts and
label documentation-only detection-pattern matches as intentional.

## A5.1 Acceptance Criteria

A5.1 is acceptable when:

- the evidence bundle template includes concrete sections for closeout
  verification, branch/commit status, live-run approval, preflight evidence,
  fresh side-effect rule evidence, allowlist evidence, token-presence
  redaction, remote marker lookup, comment URL placeholder, SQLite ledger
  evidence, audit evidence, replay/no-duplicate evidence, negative allowlist
  zero-network evidence, redaction proof, final conclusion, and known
  limitations
- the redacted evidence example uses safe placeholders only
- the token redaction checklist defines forbidden captures, safe captures,
  token-presence recording, command-output redaction, grep checks, expected
  results, and remediation if a possible secret is found
- the manual runbook makes A5.3 start gates explicit and marks future live
  commands as not runnable in A5.1
- the threat model covers secret leakage, false-positive proof, wrong scan
  paths, manual token copying, pre-existing markers, accidental network in
  negative allowlist tests, implicit live approval, CI live smoke, and evidence
  overclaiming
- A5.1 remains non-live and documentation-only
- no runtime execution behavior is added
- no live GitHub execution occurs
- no credentials are read or required
- `.env` remains ignored and untracked
- validation commands pass or any failure is reported plainly

## A5.2 Acceptance Criteria

A5.2 is acceptable when:

- an isolated Artifact 05 preflight helper exists
- tests prove fake mode passes without a token
- tests prove real-mode preflight requires explicit opt-in
- tests prove real-mode preflight fails closed in CI
- tests prove token presence is boolean-only and token values are redacted
- tests prove repository and issue allowlist failures attempt zero network calls
- tests prove fresh side-effect mode is required
- tests prove the marker format matches Artifact 04 source behavior
- serialized output omits token values, Authorization header text, and `.env`
  contents
- docs describe A5.2 as offline, non-live, preflight-only, and not proof of a
  real GitHub post
- validation commands pass or any failure is reported plainly

## A5.3 Acceptance Criteria

A5.3 is acceptable when:

- one Product Owner-approved live smoke posts exactly one GitHub issue comment
  to the allowlisted repository and issue
- A5.2 preflight output is redacted and shows `network_calls_attempted: 0`
- the fresh side-effect strategy is recorded as `new_unique_body`
- the remote marker lookup happens before the create call
- the marker is absent before posting
- durable side-effect status ends as `succeeded`
- external comment id and URL are captured
- durable audit events include the marker lookup and create-call lifecycle
- no replay/no-duplicate testing is run in A5.3
- no non-allowlisted live testing is run in A5.3
- no GitHub write operation besides the one issue comment occurs
- redaction checks against the evidence bundle show no token-like values
- validation commands pass or any failure is reported plainly

## A5.4 Acceptance Criteria

A5.4 is acceptable when:

- final release-gate report evidence exists under
  `docs/evidence/a5.4-final-release-gate-report/`
- replay/no-duplicate proof is evidence-backed by offline/mocked/spy tests
- real replay against GitHub is not run unless separately approved
- no second GitHub comment is posted
- negative allowlist proof shows non-allowlisted repo and issue rejection before
  network
- no non-allowlisted live test is run
- A5.3 comment id, comment URL, ledger success, and audit lifecycle evidence are
  preserved
- redaction checks against the evidence bundle show no token-like values
- validation commands pass or any failure is reported plainly

## Block Conditions

Stop before live smoke or release evidence acceptance if:

- Artifact 04 final tag does not point to `9ef8ab8`, unless a newer closeout
  commit was explicitly approved by the Design Supervisor
- Product Owner has not explicitly approved the live smoke step in that sprint
- `.env` is tracked, staged, or printed
- a token is missing, over-scoped, pasted into docs/logs/evidence, or accepted
  from request/model/tool input
- repository or issue is not allowlisted before network
- durable approval binding is missing or mismatched before network
- durable side-effect ledger state is missing, ambiguous, or unsafe
- remote marker lookup fails, is incomplete, or is ambiguous
- marker already exists and no explicit reconciliation path is approved
- non-allowlist evidence cannot prove zero HTTP calls
- redaction proof is missing
- the task requires CI live GitHub execution
- the scope expands beyond the one issue-comment operation

## Non-Goals

Artifact 05 does not implement:

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
- production-ready system
- Digital FTE behavior
- arbitrary repository support
- universal exactly-once guarantee

## Known Limitations

- This is a local/demo artifact sequence, not a production system.
- A5.0 is documentation/scaffold only.
- The future live smoke path remains manual and opt-in.
- Remote marker lookup reduces duplicate-post risk for the scoped path but is
  not a universal exactly-once guarantee.
- Human deletion or editing of marker text can undermine remote detection.
- GitHub availability, rate limits, pagination bounds, or malformed responses
  can block execution.
- Redacted evidence can prove the run shape, but it must not expose secrets.
