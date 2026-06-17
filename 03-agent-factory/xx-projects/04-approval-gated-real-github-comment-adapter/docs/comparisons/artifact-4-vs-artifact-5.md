# Artifact 4 vs Artifact 5

## Summary

Artifact 4 is complete as a local/demo durable fake-client safety artifact.

Artifact 5 is complete as a local/demo approval-gated real GitHub issue-comment
adapter built on the Artifact 4 baseline.

## Artifact 4

Artifact 4 implements:

- SQLite-backed side-effect records
- durable approval bindings
- durable audit events
- restart/replay duplicate suppression for the fake-client GitHub comment path
- fake-client-only execution
- local/demo safety evidence

Artifact 4 does not implement:

- real GitHub execution
- GitHub token loading
- remote marker lookup
- production-grade exactly-once semantics

## Artifact 5

Artifact 5 adds:

- server-side environment token-provider boundary (A5.1)
- real-mode configuration boundary, disabled by default (A5.1)
- GitHub client interface with fake and real implementations (A5.1)
- deterministic remote idempotency marker construction and parsing (A5.2)
- fake/mocked remote comment listing and marker lookup (A5.2)
- durable reconciliation for crash-window recovery (A5.2)
- one narrow real GitHub issue-comment client using standard-library HTTP (A5.3)
- bounded pagination for complete-enough marker lookup (A5.3)
- exact server-owned repository allowlist enforcement (A5.3)
- remote marker lookup before posting (A5.3)
- marker-found reconciliation without posting (A5.3)
- marker-absent posting with deterministic marker appended (A5.3)
- external comment id/url persistence (A5.3)
- durable audit events for real-mode safety decisions (A5.3)
- adversarial token leakage and redaction tests (A5.4)
- hostile transport exception redaction (A5.4)
- repository allowlist bypass tests (A5.4)
- approval/hash mutation tests (A5.4)
- marker spoofing, ambiguity, and fail-closed tests (A5.4)
- crash-window replay through executing durable records (A5.4)
- documentation, demo, and portfolio packaging (A5.5)

Artifact 5 does not implement:

- general GitHub automation
- arbitrary repository support
- OAuth/OIDC
- MCP
- frontend or operator console
- deployment
- production-ready guarantees
- universal exactly-once guarantees

## Why The Progression Is Needed

Artifact 4's local SQLite ledger can suppress duplicate fake-client execution
after durable success exists. A real GitHub adapter needs an additional remote
reconciliation step because GitHub and SQLite cannot commit atomically.

The critical crash window:

```text
1. GitHub comment POST succeeds.
2. Process crashes before SQLite records succeeded.
3. Service restarts.
4. Local ledger is not succeeded.
5. Replay attempts execution.
6. Without remote marker lookup, duplicate real comment may be posted.
```

Artifact 5 addresses that gap with a remote marker embedded in posted comments:

```html
<!-- agent_factory:v1 side_effect_id=<side_effect_id> args_hash=<validated_arguments_hash> -->
```

The harness searches for this exact marker before posting and fails closed if
lookup fails or remote state is ambiguous.

## Key Differences

| Aspect | Artifact 4 | Artifact 5 |
|--------|-----------|-----------|
| Default client | Fake | Fake (unchanged) |
| Real GitHub execution | Not implemented | Available via explicit server config |
| Token loading | Not implemented | Server-side environment only |
| Remote marker lookup | Not implemented | Before any real post |
| Crash-window reconciliation | Not applicable (fake only) | Marker-based remote reconciliation |
| Repository allowlist | Policy check only | Exact server-owned allowlist |
| Adversarial safety tests | Fake-client safety | Real-mode boundary safety |
| Durable audit | Local/demo events | Includes real-mode safety decisions |
