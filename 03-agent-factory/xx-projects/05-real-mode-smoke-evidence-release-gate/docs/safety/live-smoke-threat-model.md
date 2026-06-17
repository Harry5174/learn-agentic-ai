# Live Smoke Threat Model

## Purpose

This page defines the threats that Artifact 05 release-gate evidence must
address before a future manual real-mode smoke run can be accepted.

A5.0 does not run live GitHub.

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

## Main Threats And Controls

| Threat | Required control |
|--------|------------------|
| Token leaks into docs, logs, evidence, audit, or exceptions | Server-side token only, redaction proof, no `.env` contents printed |
| Model or request enables real mode | Real mode controlled only by trusted server-side configuration |
| Repository allowlist bypass | Exact server-owned allowlist before token loading or network |
| Approval/hash mutation | Durable approval binding for exact `side_effect_id` and validated arguments hash |
| Duplicate post after crash | Remote marker lookup before posting and durable reconciliation |
| Marker ambiguity | Fail closed when lookup is ambiguous, incomplete, or failed |
| Non-allowlisted target reaches network | Mocked/spy transport proof showing zero HTTP calls |
| CI accidentally runs live GitHub | No CI live GitHub execution; automated tests fake/mocked only |
| Scope expands into GitHub automation | One operation only: post issue comment |

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

## Non-Goals

This threat model does not authorize production deployment, arbitrary
repository support, OAuth, MCP, operator UI, broad GitHub automation, or
universal exactly-once claims.

