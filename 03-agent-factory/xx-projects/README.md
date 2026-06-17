# Agent Factory - Project Artifacts

This directory contains the numbered artifact sequence for the Agent Factory track. Each artifact builds on the previous one, adding a new layer of controlled AI tool execution.

---

## Artifact Index

| # | Folder | Title | Status |
|---|--------|-------|--------|
| 0 | [00-identity-aware-agent-harness](00-identity-aware-agent-harness) | Identity-Aware Stateful Agent Harness | Complete / preserved |
| 1 | [01-llm-proposed-skill-runner](01-llm-proposed-skill-runner) | LLM-Proposed, Harness-Controlled Skill Runner | Complete / tagged `artifact-2.2` |
| 2 | [02-approval-gated-github-tool-harness](02-approval-gated-github-tool-harness) | Approval-Gated GitHub Tool Harness | Complete as local/demo fake-client artifact |
| 3 | [03-durable-side-effect-ledger](03-durable-side-effect-ledger) | Durable Side-Effect Ledger and Approval Binding | Complete as local/demo durable fake-client safety artifact |
| 4 | [04-approval-gated-real-github-comment-adapter](04-approval-gated-real-github-comment-adapter) | Approval-Gated Real GitHub Comment Adapter | Initialized as A5.0 baseline/specification artifact |

---

## Artifact 0 - Identity-Aware Stateful Agent Harness

**Path:** `00-identity-aware-agent-harness`
**Status:** Complete / preserved

**Core claim:** Server-derived identity, role/scope-aware policy checks, stateful task lifecycle, approval gates, audit trail, dry-run tools, LangGraph checkpoint/resume, FastAPI task API.

**Key boundary:** Request bodies cannot claim identity, role, or scopes. Identity is always server-derived.

---

## Artifact 1 - LLM-Proposed, Harness-Controlled Skill Runner

**Path:** `01-llm-proposed-skill-runner`
**Status:** Complete / tagged `artifact-2.2`

**Core claim:** Model-shaped skill proposals, proposal validation, policy and approval lifecycle, Skill Runner API, validated model-proposed scalar arguments, safe rejection of unsafe/control-plane/malformed args.

**Key boundary:** The proposer proposes. The harness validates, authorizes, approval-gates, executes, and audits.

---

## Artifact 2 - Approval-Gated GitHub Tool Harness

**Path:** `02-approval-gated-github-tool-harness`
**Status:** Complete as local/demo fake-client artifact

**Core claim:** One approval-gated GitHub issue-comment skill path with validated scalar arguments, trusted repository policy, explicit approval, side-effect idempotency through an in-memory ledger, `FakeGitHubIssueCommentClient` execution, audit evidence, and adversarial safety tests.

**Final statement:** Artifact 3 demonstrates a local/demo approval-gated GitHub issue-comment harness path where model-proposed scalar arguments are validated, repository policy is checked, approval is required, side-effect idempotency is checked with an in-memory ledger, fake-client execution is used, and audit evidence is recorded.

**Read first:**

- [Artifact 3 docs README](02-approval-gated-github-tool-harness/docs/README.md)
- [GitHub comment tool demo](02-approval-gated-github-tool-harness/docs/demos/github-comment-tool-demo.md)
- [Adversarial safety evidence](02-approval-gated-github-tool-harness/docs/adversarial-github-side-effect-safety.md)

---

## Artifact 4 - Durable Side-Effect Ledger and Approval Binding

**Path:** `03-durable-side-effect-ledger`
**Status:** Complete as local/demo durable fake-client safety artifact

**A4.5 claim:** Artifact 4 demonstrates restart-safe local/demo side-effect execution for an approval-gated fake-client GitHub comment path using SQLite-backed side-effect records, durable approval bindings, restart/replay duplicate suppression, durable local/demo audit events, and adversarial persistence tests.

**Current limitation:** Fake-client only. It has not implemented real GitHub execution, token loading, or production-grade exactly-once claims.

**Read first:**

- [Artifact 4 README](03-durable-side-effect-ledger/README.md)
- [Artifact 4 durable-state spec](03-durable-side-effect-ledger/docs/specs/artifact-4-durable-side-effect-ledger.md)
- [Persistence boundary](03-durable-side-effect-ledger/docs/architecture/persistence-boundary.md)

---

## Artifact 5 - Approval-Gated Real GitHub Comment Adapter

**Path:** `04-approval-gated-real-github-comment-adapter`
**Status:** Initialized as A5.0 baseline/specification artifact

**A5.0 claim:** Artifact 5 defines the safety design for a future approval-gated real GitHub issue-comment adapter, including the real-mode boundary, fake-client default, server-side token handling requirements, repository allowlist requirements, GitHub/SQLite crash-window analysis, remote idempotency marker format, reconciliation behavior, fail-closed ambiguity handling, durable audit requirements, future test strategy, explicit non-goals, known limitations, and A5.1 onward roadmap.

**Current limitation:** No real GitHub client, token loading, network code, real GitHub API call, or runtime remote marker implementation exists yet.

**Read first:**

- [Artifact 5 README](04-approval-gated-real-github-comment-adapter/README.md)
- [Artifact 5 real GitHub comment adapter spec](04-approval-gated-real-github-comment-adapter/docs/specs/artifact-5-real-github-comment-adapter.md)
- [Remote idempotency and reconciliation](04-approval-gated-real-github-comment-adapter/docs/architecture/remote-idempotency-reconciliation.md)

## What Is Not Here Yet

Artifact 4 is complete as a local/demo durable fake-client safety artifact. It implements SQLite-backed side-effect records, durable approval bindings, durable audit events, and restart/replay duplicate suppression for the fake-client GitHub comment path. It does not implement real GitHub execution, GitHub token loading, or production-grade exactly-once semantics.

Artifact 5 is initialized as a baseline/specification artifact for a future approval-gated real GitHub issue-comment adapter. A5.0 defines the real-mode safety boundary, token guidance, remote idempotency marker, reconciliation behavior, audit requirements, and non-goals. No real GitHub client, token loading, network code, or runtime remote marker implementation exists yet.
