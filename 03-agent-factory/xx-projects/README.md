# Agent Factory — Project Artifacts

This directory contains the numbered artifact sequence for the Agent Factory track. Each artifact builds on the previous one, adding a new layer of controlled AI tool execution.

---

## Artifact Index

| # | Folder | Title | Status |
|---|--------|-------|--------|
| 0 | [00-identity-aware-agent-harness](00-identity-aware-agent-harness) | Identity-Aware Stateful Agent Harness | Complete / preserved |
| 1 | [01-llm-proposed-skill-runner](01-llm-proposed-skill-runner) | LLM-Proposed, Harness-Controlled Skill Runner | Complete / tagged `artifact-2.2` |
| 2 | [02-approval-gated-github-tool-harness](02-approval-gated-github-tool-harness) | Approval-Gated GitHub Tool Harness | Complete as local/demo fake-client artifact |

---

## Artifact 0 — Identity-Aware Stateful Agent Harness

**Path:** `00-identity-aware-agent-harness`
**Status:** Complete / preserved

**Core claim:** Server-derived identity, role/scope-aware policy checks, stateful task lifecycle, approval gates, audit trail, dry-run tools, LangGraph checkpoint/resume, FastAPI task API.

**Key boundary:** Request bodies cannot claim identity, role, or scopes. Identity is always server-derived.

**Read first:**
- The artifact's root README
- `docs/` for architecture and sprint documentation

**Limitations:**
- Dry-run tools only
- No real external tool execution
- Identity is simulated (no production OIDC/OAuth provider)

---

## Artifact 1 — LLM-Proposed, Harness-Controlled Skill Runner

**Path:** `01-llm-proposed-skill-runner`
**Status:** Complete / tagged `artifact-2.2`

**Core claim:** Model-shaped skill proposals (SkillSpec / SkillStep / SkillProposal), proposal validation, policy and approval lifecycle, Skill Runner API, validated model-proposed scalar arguments, safe rejection of unsafe/control-plane/malformed args.

**Key boundary:** The proposer proposes. The harness validates, authorizes, approval-gates, executes, and audits.

**Read first:**
- The artifact's root README
- `docs/demos/skill-runner-api-demo.md`

**Limitations:**
- Dry-run only
- Scalar args only (no object/list/nested args)
- No real GitHub writes
- No live LLM HTTP mode
- Not production-ready

---

## Artifact 2 — Approval-Gated GitHub Tool Harness

**Path:** `02-approval-gated-github-tool-harness`
**Status:** Complete as local/demo fake-client artifact

**Core claim:** One approval-gated GitHub issue-comment skill path with validated scalar arguments, trusted repository policy, explicit approval, side-effect idempotency (in-memory ledger), FakeGitHubIssueCommentClient execution, audit evidence, and adversarial safety tests.

**Final statement:** Artifact 3 demonstrates a local/demo approval-gated GitHub issue-comment harness path where model-proposed scalar arguments are validated, repository policy is checked, approval is required, side-effect idempotency is checked with an in-memory ledger, fake-client execution is used, and audit evidence is recorded.

**Read first:**
- [Artifact 3 docs README](02-approval-gated-github-tool-harness/docs/README.md)
- [GitHub comment tool demo](02-approval-gated-github-tool-harness/docs/demos/github-comment-tool-demo.md)
- [Adversarial safety evidence](02-approval-gated-github-tool-harness/docs/adversarial-github-side-effect-safety.md)

**Limitations:**
- Local/demo only
- Fake GitHub client only (no real GitHub API / network execution)
- No GitHub token loading
- No durable side-effect ledger
- No durable audit store
- No OAuth/OIDC production identity provider
- No frontend / operator console
- Not production-ready

---

## What Is Not Here Yet

The next likely artifact is **Artifact 4 — Approval-Gated Real GitHub Comment Adapter**, which would move from fake-client local/demo execution to one carefully guarded real GitHub issue-comment adapter. This should be separately designed and approved before implementation.
