# Agent Factory

The Agent Factory is the main portfolio and system-building track in the Learning Agentic AI repository. It combines coursework, design thinking, and a progressive artifact sequence that demonstrates controlled AI tool execution harnesses.

---

## Thesis

> Agents are useful only when the application harness controls identity, validation, policy, approval, execution, and audit.

The Agent Factory track explores this thesis through:

- Coursework on AI-native thinking, prompting, and agentic coding
- A numbered artifact sequence (`xx-projects/`) where each artifact adds a new layer of harness control
- Strict separation between what the model proposes and what the harness permits

---

## Artifact Sequence

The `xx-projects/` directory contains the core artifact sequence:

| Artifact | Name | Status |
|----------|------|--------|
| 1 | [Identity-Aware Stateful Agent Harness](xx-projects/00-identity-aware-agent-harness) | Complete / preserved |
| 2 / 2.2 | [LLM-Proposed, Harness-Controlled Skill Runner](xx-projects/01-llm-proposed-skill-runner) | Complete / tagged `artifact-2.2` |
| 3 | [Approval-Gated GitHub Tool Harness](xx-projects/02-approval-gated-github-tool-harness) | Complete as local/demo fake-client artifact |

Each artifact builds on the previous:

- **Artifact 1** established server-derived identity, role/scope policy, stateful task lifecycle, approval gates, audit trail, and LangGraph checkpoint/resume.
- **Artifact 2 / 2.2** added model-shaped skill proposals (SkillSpec / SkillStep / SkillProposal), proposal validation, policy and approval lifecycle, a Skill Runner API, and safe rejection of unsafe arguments.
- **Artifact 3** added one approval-gated GitHub issue-comment skill path with validated scalar arguments, trusted repository policy, explicit approval, side-effect idempotency (in-memory ledger), FakeGitHubIssueCommentClient execution, audit evidence, and adversarial safety tests.

See [xx-projects/README.md](xx-projects/README.md) for the detailed artifact index.

---

## Current Folders

```
03-agent-factory/
├── 00-about-and-thesis/            # Foundations: four-channel ecosystem, role guide, invariants
├── 01-ai-prompting-2026/           # Prompt engineering, context control, experiments
├── 02-how-to-think-ai-era/         # Thinking checklists and methodologies
├── 03-agentic-coding-crash-course/ # Core workflows, persistent sandboxes, routines
├── 04-build-ai-agents/             # Architecture patterns, MCP, orchestration SDKs
└── xx-projects/                    # ★ Numbered artifact sequence
    ├── 00-identity-aware-agent-harness
    ├── 01-llm-proposed-skill-runner
    └── 02-approval-gated-github-tool-harness
```

---

## What Artifact 3 Adds

Artifact 3 is the current leading artifact. It demonstrates a local/demo approval-gated GitHub issue-comment harness path where:

- Model-proposed scalar arguments are validated
- Repository policy is checked against a trusted-repository allowlist
- Explicit approval is required before execution
- Side-effect idempotency is checked with an in-memory ledger
- Fake-client execution is used (no real GitHub network calls)
- Audit evidence is recorded for every decision
- Adversarial safety tests verify rejection of unsafe inputs

---

## What Is Not Implemented Yet

Current Artifact 3 is a local/demo fake-client artifact. It does not implement:

- Real GitHub API / network execution
- GitHub token loading or credential management
- Durable side-effect ledger (replay protection is in-memory only)
- Durable audit store
- OAuth/OIDC production identity provider
- Frontend / operator console
- MCP integration
- Production deployment

---

## Recommended Next Work

**Next likely artifact:**
Artifact 4 — Approval-Gated Real GitHub Comment Adapter

**Purpose:** Move from fake-client local/demo execution to one carefully guarded real GitHub issue-comment adapter.

This should be separately designed and approved before implementation.
