# Artifact 4 - Durable Side-Effect Ledger and Approval Binding

Artifact 4 is the Durable Side-Effect Ledger and Approval Binding project.

A4.0 is a baseline copy and durable-state specification sprint. This project was copied from the completed Artifact 3 project, `03-agent-factory/xx-projects/02-approval-gated-github-tool-harness`, and now identifies as the Artifact 4 workspace.

Artifact 4 exists to move from process-local side-effect safety toward restart-safe durable side-effect safety before any real GitHub write is enabled.

A4.1 implements the SQLite-backed side_effect_records ledger. A4.1 does not implement durable approval binding. A4.1 does not implement durable audit store. A4.1 does not integrate with graph/service execution. A4.1 does not provide restart-safe execution yet. A4.1 proves repository re-instantiation persistence only. Real GitHub execution remains absent.

A4.2 implements durable approval binding. A4.2 persists approval decisions against exact side_effect_id and validated_arguments_hash. A4.2 does not implement durable audit store. A4.2 does not integrate with graph/service execution. A4.2 does not provide full restart-safe execution yet. A4.2 does not execute fake client. A4.2 does not execute real GitHub calls.

A4.3 integrates the durable ledger and durable approval binding into the fake-client GitHub issue-comment execution path through explicit dependency injection. A4.3 demonstrates restart-replay duplicate suppression for the local/demo fake-client GitHub comment path using SQLite-backed side-effect and approval records. A4.3 does not add durable audit store, real GitHub execution, GitHub token loading, or production-grade exactly-once semantics.

A4.3.1 modularized the restart/replay implementation and graph/tool boundaries without adding runtime behavior.

## Mission

Make approval-gated side-effect execution durable, replay-safe, and auditable across process restarts before enabling any real GitHub write.

The core question for Artifact 4 is:

```text
If the same approved side effect is replayed after process restart, can the harness prove it will not execute twice?
```

A4.3 answers that question for the local/demo fake-client GitHub comment path after durable success has already been recorded.

## Current State

Current A4.3.1 state:

- copied baseline from completed Artifact 3
- Artifact 4 project identity and documentation baseline
- durable-state specification added
- persistence-boundary architecture added
- parent indexes updated to list Artifact 4 as in progress
- inherited Artifact 3 fake-client local/demo behavior remains unchanged
- SQLite-backed side_effect_records ledger implemented in A4.1
- SQLite-backed approval_bindings store implemented in A4.2
- approval binding persists against exact side_effect_id + validated_arguments_hash
- approval-to-side-effect matching enforced at domain level
- one approval binding per side_effect_id enforced for V1
- approve/reject update both approval binding and side-effect status in a single transaction
- expired approval does not mutate side-effect status
- durable ledger and approval binding are integrated into the fake-client GitHub comment execution path through explicit runtime injection
- approved execution marks the side effect executing, calls `FakeGitHubIssueCommentClient` once, and persists succeeded or failed
- replay after durable success returns already_succeeded / duplicate-suppressed evidence without calling the fake client again
- replay after durable success preserves `side_effect_records.status = succeeded`
- persisted `executing` and failed terminal records are not automatically retried
- A4.3.1 splits restart/replay tests and extracts graph/tool helper modules without changing execution semantics

Not implemented yet:

- durable audit store runtime code
- default API startup requiring a SQLite file
- real GitHub client
- GitHub token loading
- real GitHub network execution
- production persistence or production audit guarantees
- production-grade exactly-once side-effect execution

## Source Baseline

Artifact 4 was copied from completed Artifact 3:

```text
03-agent-factory/xx-projects/02-approval-gated-github-tool-harness
```

Inherited behavior remains local/demo only:

```text
model-shaped proposal
-> proposal validation
-> scalar argument validation
-> repository policy
-> approval gate
-> side_effect_id computation
-> in-memory ledger check
-> fake GitHub client
-> audit evidence
```

Artifact 3 demonstrated that path with an in-memory ledger and `FakeGitHubIssueCommentClient`. Artifact 4 keeps default app startup compatible with that behavior while allowing A4.3 tests to inject durable stores into the same GitHub comment tool path. A4.1 implements the SQLite side-effect ledger. A4.2 implements the durable approval binding store. A4.3 integrates those stores for the fake-client restart-replay proof.

## Durable-State Design

Read the A4.0 durable-state spec first:

- [Artifact 4 durable side-effect ledger spec](docs/specs/artifact-4-durable-side-effect-ledger.md)
- [Persistence boundary architecture](docs/architecture/persistence-boundary.md)
- [Artifact 3 vs Artifact 4 comparison](docs/comparisons/artifact-3-vs-artifact-4.md)

The A4.3 durable execution proof uses:

```text
SkillGraphService
-> DurableApprovalBindingStore
-> DurableSideEffectLedger
-> SQLite
-> FakeGitHubIssueCommentClient
```

A4.3 keeps `DurableApprovalBindingStore` and `DurableSideEffectLedger` backed by SQLite. The durable audit store is not yet implemented. SQLite is the persistence boundary for the local/demo proof. The fake GitHub client remains the execution boundary. Real GitHub execution remains out of scope.

## Quickstart

Install dependencies:

```bash
uv sync
```

Run tests and lint:

```bash
uv run pytest
uv run ruff check .
```

Run the inherited local API with the repo-supported console script:

```bash
uv run app
```

Equivalent direct uvicorn form:

```bash
uv run uvicorn app.api.main:app --reload
```

Base URL:

```text
http://127.0.0.1:8000
```

Demo API keys:

- `viewer-dev-key`
- `operator-dev-key`
- `admin-dev-key`

These are static local/demo credentials, not production identity.

## Documentation

Use [docs/README.md](docs/README.md) as the documentation index.

High-value entry points:

- [Artifact 4 durable side-effect ledger spec](docs/specs/artifact-4-durable-side-effect-ledger.md)
- [Persistence boundary architecture](docs/architecture/persistence-boundary.md)
- [Project status](docs/status/project-status.md)
- [Roadmap](docs/status/roadmap.md)
- [Known limitations](docs/status/known-limitations.md)
- [Interview notes](docs/status/interview-notes.md)
- [Artifact 3 vs Artifact 4](docs/comparisons/artifact-3-vs-artifact-4.md)
- [Inherited GitHub comment demo](docs/demos/github-comment-tool-demo.md)
- [Restart replay demo](docs/demos/restart-replay-demo.md)
- [Inherited adversarial GitHub side-effect safety](docs/adversarial-github-side-effect-safety.md)

## Current Boundaries

Artifact 4 A4.3 implements the `DurableApprovalBindingStore` and `DurableSideEffectLedger` backed by SQLite and integrates them into the fake-client GitHub comment execution path through explicit runtime injection. A4.3 proves that an approved side effect that has already been marked succeeded is not executed again after fresh service/store/fake-client objects are created against the same SQLite file.

The default copied runtime still inherits Artifact 3 local/demo behavior:

- one approval-gated GitHub issue-comment skill path
- validated scalar `repository`, `issue_number`, and `comment_body` arguments
- trusted repository allowlist policy
- explicit approval
- process-local `InMemorySideEffectLedger`
- `FakeGitHubIssueCommentClient` simulated execution
- in-memory audit evidence

The project remains local/demo and fake-client-only. No real GitHub API call. No token required. No network call.

A4.3 does not prove production-grade exactly-once execution across every crash window. If the fake client succeeds but the process dies before `side_effect_records` is marked `succeeded`, A4.3 does not prove universal duplicate suppression for that interrupted attempt.
