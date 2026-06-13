# Artifact 4 - Durable Side-Effect Ledger and Approval Binding

Artifact 4 is the Durable Side-Effect Ledger and Approval Binding project.

A4.0 is a baseline copy and durable-state specification sprint. This project was copied from the completed Artifact 3 project, `03-agent-factory/xx-projects/02-approval-gated-github-tool-harness`, and now identifies as the Artifact 4 workspace.

Artifact 4 exists to move from process-local side-effect safety toward restart-safe durable side-effect safety before any real GitHub write is enabled.

A4.1 implements the SQLite-backed side_effect_records ledger. A4.1 does not implement durable approval binding. A4.1 does not implement durable audit store. A4.1 does not integrate with graph/service execution. A4.1 does not provide restart-safe execution yet. A4.1 proves repository re-instantiation persistence only. Real GitHub execution remains absent.

A4.2 implements durable approval binding. A4.2 persists approval decisions against exact side_effect_id and validated_arguments_hash. A4.2 does not implement durable audit store. A4.2 does not integrate with graph/service execution. A4.2 does not provide full restart-safe execution yet. A4.2 does not execute fake client. A4.2 does not execute real GitHub calls.

## Mission

Make approval-gated side-effect execution durable, replay-safe, and auditable across process restarts before enabling any real GitHub write.

The core question for Artifact 4 is:

```text
If the same approved side effect is replayed after process restart, can the harness prove it will not execute twice?
```

A4.0 answers that question as a design and acceptance contract only. Implementation is reserved for later A4.x sprints after review.

## Current State

Current A4.2 state:

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

Not implemented yet:

- durable audit store runtime code
- graph or service integration with durable persistence
- API behavior changes
- real GitHub client
- GitHub token loading
- real GitHub network execution
- production persistence or production audit guarantees

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

Artifact 3 demonstrated that path with an in-memory ledger and `FakeGitHubIssueCommentClient`. Artifact 4 keeps that runtime behavior unchanged at the graph/service level while defining the future durable-state boundary. A4.1 implements the SQLite side-effect ledger. A4.2 implements the durable approval binding store.

## Durable-State Design

Read the A4.0 durable-state spec first:

- [Artifact 4 durable side-effect ledger spec](docs/specs/artifact-4-durable-side-effect-ledger.md)
- [Persistence boundary architecture](docs/architecture/persistence-boundary.md)
- [Artifact 3 vs Artifact 4 comparison](docs/comparisons/artifact-3-vs-artifact-4.md)

The future target architecture is:

```text
SkillGraphService
-> DurableApprovalBindingStore
-> DurableSideEffectLedger
-> DurableAuditStore
-> SQLite
-> FakeGitHubIssueCommentClient
```

A4.2 implements `DurableApprovalBindingStore` and `DurableSideEffectLedger` backed by SQLite. The durable audit store is not yet implemented. The graph/service integration is not yet implemented. SQLite is the planned persistence boundary for Artifact 4. The fake GitHub client remains the execution boundary. Real GitHub execution remains out of scope.

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
- [Inherited adversarial GitHub side-effect safety](docs/adversarial-github-side-effect-safety.md)

## Current Boundaries

Artifact 4 A4.2 implements the `DurableApprovalBindingStore` and `DurableSideEffectLedger` backed by SQLite. A4.2 proves that approval bindings can persist in SQLite and authorize only the exact side_effect_id and validated_arguments_hash after store re-instantiation. However, A4.2 does not integrate these stores into the graph/service execution path, does not implement durable audit store, and does not provide full restart-safe side-effect execution.

The copied runtime still inherits Artifact 3 local/demo behavior:

- one approval-gated GitHub issue-comment skill path
- validated scalar `repository`, `issue_number`, and `comment_body` arguments
- trusted repository allowlist policy
- explicit approval
- process-local `InMemorySideEffectLedger`
- `FakeGitHubIssueCommentClient` simulated execution
- in-memory audit evidence

The project remains local/demo, process-local, fake-client-only, and real-network disabled. No real GitHub API call. No token required. No network call.
