# Artifact 4 vs Artifact 5

## Summary

Artifact 4 is complete as a local/demo durable fake-client safety artifact.

Artifact 5 is initialized as a baseline/specification artifact for a future
approval-gated real GitHub issue-comment adapter.

A5.0 does not implement real GitHub execution.

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

## Artifact 5 A5.0

Artifact 5 A5.0 adds:

- Artifact 5 workspace identity
- real-mode safety boundary
- token guidance
- repository allowlist requirements
- GitHub/SQLite crash-window analysis
- remote idempotency marker format
- remote reconciliation behavior
- fail-closed ambiguity rules
- durable audit requirements for future real mode
- future real-mode testing strategy
- explicit non-goals and known limitations

Artifact 5 A5.0 does not add:

- real GitHub client implementation
- token provider implementation
- environment token loading
- HTTP/network code
- real GitHub API calls
- new runtime side-effect behavior
- remote marker runtime code
- live smoke test

## Why The New Design Is Needed

Artifact 4's local SQLite ledger can suppress duplicate fake-client execution
after durable success exists. A future real GitHub adapter needs an additional
remote reconciliation step because GitHub and SQLite cannot commit atomically.

The key crash window is:

```text
1. GitHub comment POST succeeds.
2. Process crashes before SQLite records succeeded.
3. Service restarts.
4. Local ledger is not succeeded.
5. Replay attempts execution.
6. Without remote marker lookup, duplicate real comment may be posted.
```

Artifact 5 addresses that design gap with a required future remote marker:

```html
<!-- agent_factory:v1 side_effect_id=<side_effect_id> args_hash=<validated_arguments_hash> -->
```

Future real mode must search for the exact marker before posting and must fail
closed if lookup fails or remote state is ambiguous.
