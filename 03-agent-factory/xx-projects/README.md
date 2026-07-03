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
| 4 | [04-approval-gated-real-github-comment-adapter](04-approval-gated-real-github-comment-adapter) | Approval-Gated Real GitHub Comment Adapter | Complete as local/demo real-comment adapter (A4.5) |
| 5 | [05-real-mode-smoke-evidence-release-gate](05-real-mode-smoke-evidence-release-gate) | Real-Mode Smoke Evidence and Release Gate | Complete / published / tagged evidence artifact |
| 6 | [06-operator-approval-workbench](06-operator-approval-workbench) | Operator Approval Console / Workbench | Current local/demo workbench artifact (A6.5) |
| 7 | [07-github-repo-steward](07-github-repo-steward) | GitHub Repo Steward | Local fixture snapshot, normalizer, deterministic findings, fake proposal drafts, and local policy evaluation; fake/local/dry-run by default |

Numbering convention:

- `00` = Artifact 00
- `01` = Artifact 01
- `02` = Artifact 02
- `03` = Artifact 03
- `04` = Artifact 04
- `05` = Artifact 05
- `06` = Artifact 06
- `07` = Artifact 07

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

**A3.5 claim:** Artifact 3 demonstrates restart-safe local/demo side-effect execution for an approval-gated fake-client GitHub comment path using SQLite-backed side-effect records, durable approval bindings, restart/replay duplicate suppression, durable local/demo audit events, and adversarial persistence tests.

**Current limitation:** Fake-client only. It has not implemented real GitHub execution, token loading, or production-grade exactly-once claims.

**Read first:**

- [Artifact 3 README](03-durable-side-effect-ledger/README.md)
- [Artifact 3 durable-state spec](03-durable-side-effect-ledger/docs/specs/artifact-3-durable-side-effect-ledger.md)
- [Persistence boundary](03-durable-side-effect-ledger/docs/architecture/persistence-boundary.md)

---

## Artifact 4 - Approval-Gated Real GitHub Comment Adapter

**Path:** `04-approval-gated-real-github-comment-adapter`
**Status:** Complete as local/demo real-comment adapter (A4.5)

**A4.5 claim:** Artifact 4 demonstrates a local/demo approval-gated real GitHub issue-comment adapter. The fake client remains the default. An explicitly configured real mode can perform one repository-allowlisted GitHub issue-comment side effect after validated scalar arguments, durable approval binding, local durable ledger checks, remote idempotency marker lookup/reconciliation, server-side token loading, and durable audit recording. Automated tests use fake/mocked clients and include adversarial crash-window safety coverage.

**Current limitation:** Local/demo artifact. Not production-ready. One issue-comment operation only. No arbitrary repository support. No OAuth/OIDC, MCP, frontend, or deployment. Manual smoke test not run unless separately approved.

**Read first:**

- [Artifact 4 README](04-approval-gated-real-github-comment-adapter/README.md)
- [Artifact 4 real GitHub comment adapter spec](04-approval-gated-real-github-comment-adapter/docs/specs/artifact-4-real-github-comment-adapter.md)
- [Remote idempotency and reconciliation](04-approval-gated-real-github-comment-adapter/docs/architecture/remote-idempotency-reconciliation.md)
- [Known limitations](04-approval-gated-real-github-comment-adapter/docs/status/known-limitations.md)
- [Interview notes](04-approval-gated-real-github-comment-adapter/docs/status/interview-notes.md)

---

## Artifact 5 - Real-Mode Smoke Evidence and Release Gate

**Path:** `05-real-mode-smoke-evidence-release-gate`
**Status:** Complete / published / tagged evidence artifact

**Core claim:** Artifact 5 is the release-gate evidence layer for Artifact 4's
narrow approval-gated real GitHub issue-comment path. It preserves fake-client
default behavior, records one controlled manually approved live smoke result
with redacted evidence, and packages offline replay/no-duplicate and negative
zero-network proof.

**Current limitation:** Evidence and release-gate context only. It does not own
runtime code, add a GitHub adapter, broaden GitHub operations, implement an
operator console, or claim production readiness.

**Read first:**

- [Artifact 5 README](05-real-mode-smoke-evidence-release-gate/README.md)
- [Artifact 5 release-gate spec](05-real-mode-smoke-evidence-release-gate/docs/specs/artifact-5-real-mode-smoke-evidence-release-gate.md)
- [A5.4 final release-gate report](05-real-mode-smoke-evidence-release-gate/docs/evidence/a5.4-final-release-gate-report/README.md)

---

## Artifact 6 - Operator Approval Console / Workbench

**Path:** `06-operator-approval-workbench`
**Status:** Current local/demo workbench artifact (A6.5)

**A6.5 claim:** Artifact 6 turns the approval-gated harness lineage into a
local operator workbench. A proposed action appears in the approval inbox, the
operator inspects risk/scopes/context/execution mode, the operator approves or
rejects through server-controlled A6 routes, and the operator can then inspect
status, decision history, local/demo audit timeline, side-effect/ledger
visibility, and execution result evidence.

**Baseline rule:** Artifact 6 derives its runtime baseline from Artifact 4.
Artifact 5 is referenced as release-gate evidence context only.

**Current boundary:** Local/demo and fake/default execution only. No live
GitHub execution, GitHub token, `.env`, OAuth/OIDC, sessions, deployment,
Next.js frontend, `package.json`, or `node_modules` are required or included
for the Artifact 6 demo.

**Read first:**

- [Artifact 6 README](06-operator-approval-workbench/README.md)
- [Operator workbench demo](06-operator-approval-workbench/docs/demos/operator-workbench-demo.md)
- [A6.5 demo evidence](06-operator-approval-workbench/docs/evidence/a6.5-operator-workbench-demo/README.md)

---

## Artifact 7 - GitHub Repo Steward

**Path:** `07-github-repo-steward`
**Status:** Local fixture snapshot, normalizer, deterministic findings, and
non-executing fake proposal drafts with local policy evaluation;
fake/local/dry-run by default

**Sprint 7.0 claim:** Artifact 07 is a GitHub Repo Steward vertical agent
scaffold. Sprint 7.0 defines the design scaffold, safety contract, evidence
expectations, and future test plan for a repository stewardship agent without
adding runtime GitHub clients, real GitHub writes, real LLM routing, or
mandatory provider credentials.

**Sprint 7.1 claim:** Artifact 07 can load a committed local fake GitHub-like
fixture snapshot and normalize repository identity, labels, issues, pull
requests, comments, and CI/status summaries into typed internal records.

**Sprint 7.2 claim:** Artifact 07 can convert normalized local fixture data into
structured deterministic repository stewardship findings.

**Sprint 7.3 claim:** Artifact 07 can convert deterministic analyzer findings
into non-executing fake proposal drafts.

**Sprint 7.4 claim:** Artifact 07 can evaluate non-executing fake proposal
drafts with deterministic local policy rules and produce structured
`ProposalPolicyEvaluation` records. `allowed_for_operator_review` is not
approval, and every evaluation still requires future operator approval.

**Current boundary:** Local fixture intake, normalization, deterministic
findings, non-executing fake proposal drafts, and local policy evaluation only.
No real GitHub reads or writes, GitHub API calls, GitHub API adapter, GitHub
SDKs, real GitHub issue comments, label mutation, issue closing, PR mutation,
branch or commit creation, workflow dispatch, required real LLM calls, real LLM
proposal generation, approval decisions, approval inbox runtime, ledger
runtime, executor runtime, `.env` reads, token reads, background automation, or
autonomous external side effects are included.

**Read first:**

- [Artifact 7 README](07-github-repo-steward/README.md)
- [Artifact 7 design scaffold](07-github-repo-steward/docs/design.md)
- [Artifact 7 safety boundaries](07-github-repo-steward/docs/safety-boundaries.md)
- [Artifact 7.0 validation summary](07-github-repo-steward/docs/evidence/artifact-7.0-validation-summary.md)
- [Artifact 7.1 validation summary](07-github-repo-steward/docs/evidence/artifact-7.1-validation-summary.md)
- [Artifact 7.2 validation summary](07-github-repo-steward/docs/evidence/artifact-7.2-validation-summary.md)
- [Artifact 7.3 validation summary](07-github-repo-steward/docs/evidence/artifact-7.3-validation-summary.md)
- [Artifact 7.4 validation summary](07-github-repo-steward/docs/evidence/artifact-7.4-validation-summary.md)

## What Is Not Here Yet

Artifacts 00 through 05 are complete as local/demo safety and evidence
artifacts. None claims production readiness, universal exactly-once execution,
or arbitrary repository support.

Artifact 06 is the current local/demo operator workbench artifact. It does not
implement general GitHub automation, OAuth/OIDC, MCP, deployment, production
authentication, live GitHub execution, or production-grade operator console
claims.

Artifact 07 currently implements only local fixture snapshot loading,
normalization, deterministic findings, non-executing fake proposal drafts, and
local policy evaluation for a future approval-gated repository stewardship
vertical agent. It does not yet implement approval runtime, ledger runtime,
executor runtime, real GitHub access, a GitHub API adapter, or a real LLM
provider requirement.
