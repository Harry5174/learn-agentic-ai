# Live Smoke Threat Model

## Purpose

This page defines the threats that Artifact 05 release-gate evidence must
address before a future manual real-mode smoke run can be accepted.

A5.2 does not run live GitHub.

## Assets

- GitHub token
- allowlisted repository and issue
- validated scalar arguments
- durable approval binding
- durable side-effect ledger
- durable audit events
- remote idempotency marker
- redacted evidence bundle

## Trust Boundary

The model, request body, tool arguments, and approval payload are untrusted for
security decisions. They must not define identity, role, scopes, policy,
approval authority, token values, repository allowlists, real-mode enablement,
idempotency markers, or execution authority.

The harness decides.

## Main Threats, Mitigations, And Evidence

| Threat | Required mitigation | Evidence requirement |
|--------|---------------------|----------------------|
| Secret leakage in evidence | Server-side token only, no `.env` contents, no copied headers, redaction before evidence review | Redaction proof or grep output against generated evidence/log directories |
| False-positive safety proof | Require proof that checks scanned the intended generated evidence/log path | Evidence bundle records scan path and expected no-match result |
| Grep scans the wrong directory | Keep safety checklist pattern references separate from generated evidence proof | Evidence labels documentation matches as intentional and scans generated evidence/log artifacts separately when present |
| Manual operator copies token into report | Use `[TOKEN VALUE: REDACTED]` only and reject prefixes, suffixes, hashes, screenshots, or lengths | Completed token redaction checklist |
| Marker already exists before first run | Apply fresh side-effect rule before A5.3 | Evidence of fresh issue, new unique body, or approved reconciliation path |
| Negative allowlist test accidentally hits network | Reject before network with mocked/spy transport | Zero HTTP calls proof |
| Live approval assumed implicitly | Require Product Owner explicit approval in the live sprint | Approval record in evidence bundle |
| CI accidentally runs live smoke | Keep live smoke manual only and automated tests fake/mocked | CI/test command evidence requires no credentials and no network |
| Evidence overclaims production readiness | Preserve local/demo, one-operation, non-production wording | Final conclusion states limitations and avoids production/universal claims |
| Preflight mistaken for live proof | Keep A5.2 output explicitly offline/non-live | Evidence states `network_calls_attempted: 0` and no real comment URL |
| Model or request enables real mode | Real mode controlled only by trusted server-side configuration | Evidence that request/model/tool did not enable real mode |
| Repository allowlist bypass | Exact server-owned allowlist before token loading or network | Allowlist evidence and zero-network rejection proof |
| Approval/hash mutation | Durable approval binding for exact `side_effect_id` and validated arguments hash | Approval binding evidence before network |
| Duplicate post after crash | Remote marker lookup before posting and durable reconciliation | Remote marker and replay/no-duplicate evidence |
| Marker ambiguity | Fail closed when lookup is ambiguous, incomplete, or failed | Audit event and ledger status evidence |
| Scope expands into GitHub automation | One operation only: post issue comment | Evidence bundle non-goal review |

## Required Fail-Closed Cases

- repository or issue not allowlisted
- missing, blank, or unsafe token source
- approval binding missing or mismatched
- durable ledger state unsafe or ambiguous
- marker lookup failure
- multiple matching markers unless explicitly reconciled
- same `side_effect_id` with different validated arguments hash
- incomplete remote listing
- GitHub HTTP, timeout, transport, or malformed-response failure
- redaction proof missing
- live-run approval missing
- generated evidence path missing when a generated evidence packet is claimed
- token-like value found in generated evidence/log artifacts
- negative allowlist proof cannot show zero HTTP calls
- evidence claims production readiness or universal exactly-once execution

## Evidence Expectations

The release gate must show:

- local gates completed before network
- repository allowlist rejection made zero HTTP calls
- durable approval binding existed before network
- durable ledger state was checked before and after execution
- remote marker lookup occurred before any post
- marker-found state prevented duplicate posting or marker-absent state allowed
  exactly one post
- durable audit events were recorded
- evidence is redacted
- Product Owner live-run approval was explicit for the sprint that runs live
  smoke
- generated evidence/log artifacts contain no token-like values
- intentional safety-documentation pattern matches are not mistaken for secrets
- A5.2 preflight output is not treated as A5.3 live evidence
- final conclusions remain local/demo and non-production

## Non-Goals

This threat model does not authorize production deployment, arbitrary
repository support, OAuth, MCP, operator UI, broad GitHub automation, or
universal exactly-once claims.
