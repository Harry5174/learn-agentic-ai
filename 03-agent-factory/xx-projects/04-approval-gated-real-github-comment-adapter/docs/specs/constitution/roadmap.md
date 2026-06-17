# Constitution Roadmap

This roadmap records sequencing discipline for future coding agents.

## Completed Baseline

Artifact 4 starts from completed Artifact 3.

Artifact 3 proved local/demo durable fake-client safety for the GitHub
issue-comment path:

- SQLite-backed side-effect records
- durable approval bindings
- durable audit events
- restart/replay duplicate suppression after durable success
- fake-client-only execution

Artifact 3 did not implement real GitHub execution, GitHub token loading, or
production-grade exactly-once semantics.

## Current Step: A5.0

A5.0 initializes Artifact 4 as a baseline/specification artifact for a future
approval-gated real GitHub issue-comment adapter.

A5.0 defines:

- real-mode safety boundary
- fake-client default behavior
- server-side token handling requirements
- minimum-privilege token guidance
- repository allowlist requirements
- GitHub/SQLite crash window
- remote idempotency marker format
- remote reconciliation behavior
- fail-closed ambiguity behavior
- durable audit requirements
- future testing strategy
- explicit non-goals

A5.0 does not implement real GitHub execution.

## Next Recommended Steps

Prepare explicit A5.1/A5.2 proposals before adding runtime real-mode behavior.

Good next slices:

- marker construction/parsing contract
- mocked remote marker lookup tests
- fail-closed reconciliation tests
- remote client interface design
- token provider interface design without loading real tokens
- server-owned repository allowlist design
- durable audit extension design

## Sequencing Rule

Do not add these as incidental cleanup:

- real GitHub API calls
- token loading
- OAuth/OIDC
- MCP
- frontend/demo UI
- deployment
- PR creation
- branch creation
- issue creation
- repo file writes
- workflow dispatch
- multiple real tools
- manual live smoke test

Any future infrastructure expansion must preserve validation, approval, audit,
redaction, repository allowlist, remote idempotency, and fail-closed boundaries.

## Future Real-Mode Requirements

Before any future real GitHub post, the harness must:

- validate scalar arguments
- enforce repository allowlist policy
- require explicit approval
- check local durable side-effect and approval records
- list existing issue comments
- search for the exact remote idempotency marker
- reconcile local state if the marker already exists
- fail closed on marker lookup failure or ambiguity
- record durable audit evidence

Future real comments must include:

```html
<!-- agent_factory:v1 side_effect_id=<side_effect_id> args_hash=<validated_arguments_hash> -->
```

The marker must be harness-generated, deterministic, machine-readable, and not
model-controlled or user-controlled.

## Token Rule

Future real mode should use server-side token loading only, with a fine-grained
GitHub token scoped to one allowlisted test repository, Issues read/write
permission, short expiration, no Contents permission, no Actions/workflows
permission, and no broad repo scope.

Tokens must not come from request bodies, model output, tool arguments, logs,
audit rows, exception messages, or test snapshots.
