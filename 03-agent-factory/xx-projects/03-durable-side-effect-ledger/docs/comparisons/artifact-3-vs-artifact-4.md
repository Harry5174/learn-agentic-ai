# Artifact 3 vs Artifact 4

Artifact 4 is copied from completed Artifact 3, but it has a different mission.

## Artifact 3 Source Baseline

Artifact 3 - Approval-Gated GitHub Tool Harness demonstrates a local/demo approval-gated GitHub issue-comment harness path where model-proposed scalar arguments are validated, repository policy is checked, approval is required, side-effect idempotency is checked with an in-memory ledger, fake-client execution is used, and audit evidence is recorded.

Artifact 3 limitations remain important:

- fake-client-only execution
- no real GitHub API/network call
- no GitHub token loading
- no durable ledger
- no durable audit store
- `ApprovalDecision` does not persist `validated_arguments_hash`
- `ApprovalDecision` does not persist `side_effect_id`
- not production-ready

## Artifact 4 Mission

Artifact 4 - Durable Side-Effect Ledger and Approval Binding moves the design target from in-memory side-effect safety to restart-safe durable side-effect safety.

Mission:

```text
Make approval-gated side-effect execution durable, replay-safe, and auditable across process restarts before enabling any real GitHub write.
```

## A4.0 Difference

A4.0 is not an implementation sprint. It defines the future durable-state design.

A4.0 adds:

- durable side-effect record schema
- durable approval binding schema
- durable audit event schema
- V1 lifecycle statuses and transitions
- terminal failure decision
- blocked/rejected distinction
- planned record behavior
- restart-replay proof sequence
- standalone SQLite persistence proof requirement

A4.0 does not add SQLite runtime code or real GitHub execution.

## Boundary Comparison

| Concern | Artifact 3 | Artifact 4 A4.0 |
|---------|------------|-----------------|
| Execution client | Fake GitHub client | Fake GitHub client remains |
| Replay guard | In-memory ledger | Future SQLite-backed durable ledger design |
| Approval binding | Checkpointed graph state | Future persisted binding to `side_effect_id` and `validated_arguments_hash` |
| Audit evidence | In-memory/local demo | Future durable local/demo audit event design |
| Restart safety | Not durable | Defined as future acceptance requirement |
| Real GitHub writes | Not implemented | Still out of scope |
| Token loading | Not implemented | Still out of scope |
| Production readiness | Not production-ready | Not production-ready |
