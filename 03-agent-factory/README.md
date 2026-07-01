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
| 0 | [Identity-Aware Stateful Agent Harness](xx-projects/00-identity-aware-agent-harness) | Complete / preserved |
| 1 | [LLM-Proposed, Harness-Controlled Skill Runner](xx-projects/01-llm-proposed-skill-runner) | Complete / tagged `artifact-2.2` |
| 2 | [Approval-Gated GitHub Tool Harness](xx-projects/02-approval-gated-github-tool-harness) | Complete as local/demo fake-client artifact |
| 3 | [Durable Side-Effect Ledger and Approval Binding](xx-projects/03-durable-side-effect-ledger) | Complete as local/demo durable fake-client safety artifact |
| 4 | [Approval-Gated Real GitHub Comment Adapter](xx-projects/04-approval-gated-real-github-comment-adapter) | Complete as local/demo real-comment adapter (A4.5) |
| 5 | [Real-Mode Smoke Evidence and Release Gate](xx-projects/05-real-mode-smoke-evidence-release-gate) | Complete / published / tagged evidence artifact |
| 6 | [Operator Approval Console / Workbench](xx-projects/06-operator-approval-workbench) | Current local/demo workbench artifact (A6.5) |

Each artifact builds on the previous:

- **Artifact 1** established server-derived identity, role/scope policy, stateful task lifecycle, approval gates, audit trail, and LangGraph checkpoint/resume.
- **Artifact 2 / 2.2** added model-shaped skill proposals, proposal validation, policy and approval lifecycle, a Skill Runner API, and safe rejection of unsafe arguments.
- **Artifact 3** added one approval-gated GitHub issue-comment skill path with validated scalar arguments, trusted repository policy, explicit approval, side-effect idempotency through an in-memory ledger, fake-client execution, audit evidence, and adversarial safety tests.
- **Artifact 4** defines the durable-state design for future restart-safe side-effect records, approval bindings, and audit evidence before any real GitHub write is enabled.

See [xx-projects/README.md](xx-projects/README.md) for the detailed artifact index.

---

## Current Folders

```text
03-agent-factory/
├── 00-about-and-thesis/            # Foundations: four-channel ecosystem, role guide, invariants
├── 01-ai-prompting-2026/           # Prompt engineering, context control, experiments
├── 02-how-to-think-ai-era/         # Thinking checklists and methodologies
├── 03-agentic-coding-crash-course/ # Core workflows, persistent sandboxes, routines
├── 04-build-ai-agents/             # Architecture patterns, MCP, orchestration SDKs
├── development-framework/          # Reusable development framework (AFDF)
└── xx-projects/                    # Numbered artifact sequence
    ├── 00-identity-aware-agent-harness
    ├── 01-llm-proposed-skill-runner
    ├── 02-approval-gated-github-tool-harness
    ├── 03-durable-side-effect-ledger
    ├── 04-approval-gated-real-github-comment-adapter
    ├── 05-real-mode-smoke-evidence-release-gate
    └── 06-operator-approval-workbench
```

---

## Current Leading Artifact

Artifact 06 (Operator Approval Console / Workbench) is the current leading artifact at sprint A6.5. It turns the approval-gated harness lineage into a local operator workbench where proposed actions appear in an approval inbox, the operator inspects risk/scopes/context, and approves or rejects through server-controlled routes.

Artifact 06 does not implement live GitHub execution, OAuth/OIDC, MCP, deployment, or production hardening.

---

## Development Framework

The [Agent Factory Development Framework](development-framework/) (AFDF) provides reusable session bootstraps, sprint lifecycle protocols, evidence review standards, safety boundary inheritance, and living project memory templates. It supports all future artifacts and sessions.

AFDF is advisory/process infrastructure only. It does not run agents or modify artifact runtime behavior.

---

## Current Limitations

The current artifact sequence remains local/demo. It does not implement:

- Real GitHub API / network execution
- GitHub token loading or credential management
- Durable side-effect ledger runtime integration
- Durable approval binding runtime integration
- Durable audit store runtime integration
- OAuth/OIDC production identity provider
- Frontend / operator console
- MCP integration
- Production deployment

---

## Recommended Next Work

The next step is the design kickoff for **Artifact 07 — GitHub Repo Steward Agent**, using the newly created `artifact-07-github-repo-steward` AFDF bootstrap package. Artifact 07 will be the first vertical agent leveraging the full harness safety stack.
