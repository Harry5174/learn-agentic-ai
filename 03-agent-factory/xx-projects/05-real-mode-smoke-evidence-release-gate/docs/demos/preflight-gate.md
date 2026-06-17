# Manual Preflight Gate

A5.2 adds an offline manual preflight gate for the future A5.3 live smoke
sprint. It does not run live GitHub, post a comment, read `.env`, load a real
token, or prove that remote freshness exists.

The helper lives at:

```text
tools/preflight_gate.py
```

It is dependency-free and isolated to Artifact 05. Tests run it through the
existing Artifact 04 Python environment without instantiating Artifact 04 real
clients.

## Repository-Backed Token Name

Artifact 04 source defines the server-side token environment name as:

```text
AGENT_FACTORY_GITHUB_TOKEN
```

A5.2 preflight reports only whether that token name is present in an injected
environment mapping. It never returns the token value.

## Repository-Backed Marker Format

Artifact 04 source and tests verify this marker format:

```html
<!-- agent_factory:v1 side_effect_id=<side_effect_id> args_hash=<validated_arguments_hash> -->
```

A5.2 verifies against that format. It does not invent a new marker.

## Behavior

The preflight gate checks:

- fake mode can pass without a token
- real mode requires explicit preflight opt-in
- real mode is blocked when `CI` is active
- token presence is boolean-only
- repository and issue allowlists are local checks
- fresh side-effect strategy is declared
- marker format is Artifact 04-backed
- network calls attempted remains `0`

Allowed fresh side-effect strategies:

```text
fresh_issue
new_unique_body
explicit_reconciliation
```

A5.2 does not prove remote freshness. A5.3 must prove freshness or
reconciliation through the live remote marker lookup after explicit live-run
approval.

## Redacted Result Shape

```text
preflight_status: passed/failed
mode: fake/real/docs
real_mode_explicit: true/false
ci_block_active: true/false
token_env_name: AGENT_FACTORY_GITHUB_TOKEN
token_present: true/false
token_value: REDACTED
allowlisted_repo: true/false
allowlisted_issue: true/false
fresh_side_effect_mode: fresh_issue/new_unique_body/explicit_reconciliation
marker_format_verified: true/false
network_calls_attempted: 0
failure_reason: safe string
```

`token_value` appears only as `REDACTED` when token presence is true.

## A5.3 Boundary

Passing A5.2 preflight is not approval to run live GitHub. A5.3 may begin only
after Design Supervisor approval of A5.2 and explicit Product Owner approval
for a live GitHub smoke run in A5.3.
