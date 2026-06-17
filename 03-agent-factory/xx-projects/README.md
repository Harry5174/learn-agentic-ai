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
| 4 | [04-approval-gated-real-github-comment-adapter](04-approval-gated-real-github-comment-adapter) | Approval-Gated Real GitHub Comment Adapter | Complete as local/demo real-comment adapter (A5.5) |

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

## Artifact 3 - Durable Side-Effect Ledger and Approval Binding

**Path:** `03-durable-side-effect-ledger`
**Status:** Complete as local/demo durable fake-client safety artifact

**A4.5 claim:** Artifact 3 demonstrates restart-safe local/demo side-effect execution for an approval-gated fake-client GitHub comment path using SQLite-backed side-effect records, durable approval bindings, restart/replay duplicate suppression, durable local/demo audit events, and adversarial persistence tests.

**Current limitation:** Fake-client only. It has not implemented real GitHub execution, token loading, or production-grade exactly-once claims.

**Read first:**

- [Artifact 3 README](03-durable-side-effect-ledger/README.md)
- [Artifact 3 durable-state spec](03-durable-side-effect-ledger/docs/specs/artifact-3-durable-side-effect-ledger.md)
- [Persistence boundary](03-durable-side-effect-ledger/docs/architecture/persistence-boundary.md)

---

## Artifact 4 - Approval-Gated Real GitHub Comment Adapter

**Path:** `04-approval-gated-real-github-comment-adapter`
**Status:** Complete as local/demo real-comment adapter (A5.5)

**A5.5 claim:** Artifact 4 demonstrates a local/demo approval-gated real GitHub issue-comment adapter. The fake client remains the default. An explicitly configured real mode can perform one repository-allowlisted GitHub issue-comment side effect after validated scalar arguments, durable approval binding, local durable ledger checks, remote idempotency marker lookup/reconciliation, server-side token loading, and durable audit recording. Automated tests use fake/mocked clients and include adversarial crash-window safety coverage.

**Current limitation:** Local/demo artifact. Not production-ready. One issue-comment operation only. No arbitrary repository support. No OAuth/OIDC, MCP, frontend, or deployment. Manual smoke test not run unless separately approved.

**Read first:**

- [Artifact 4 README](04-approval-gated-real-github-comment-adapter/README.md)
- [Artifact 4 real GitHub comment adapter spec](04-approval-gated-real-github-comment-adapter/docs/specs/artifact-4-real-github-comment-adapter.md)
- [Remote idempotency and reconciliation](04-approval-gated-real-github-comment-adapter/docs/architecture/remote-idempotency-reconciliation.md)
- [Known limitations](04-approval-gated-real-github-comment-adapter/docs/status/known-limitations.md)
- [Interview notes](04-approval-gated-real-github-comment-adapter/docs/status/interview-notes.md)

## What Is Not Here Yet

All five artifacts are complete as local/demo safety artifacts. None claims production readiness, universal exactly-once execution, or arbitrary repository support.

Artifact 4 is the most recent. It extends the fake-client durable safety of Artifact 3 with one real GitHub issue-comment side effect behind explicit server-side configuration, remote idempotency marker reconciliation, and adversarial safety testing. It does not implement general GitHub automation, OAuth/OIDC, MCP, frontend, or deployment. The optional manual smoke test is documented but was not run.
