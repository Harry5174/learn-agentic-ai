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
| 4 | [Durable Side-Effect Ledger and Approval Binding](xx-projects/03-durable-side-effect-ledger) | Complete as local/demo durable fake-client safety artifact |

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
└── xx-projects/                    # Numbered artifact sequence
    ├── 00-identity-aware-agent-harness
    ├── 01-llm-proposed-skill-runner
    ├── 02-approval-gated-github-tool-harness
    └── 03-durable-side-effect-ledger
```

---

## Current Leading Artifact

Artifact 4 is complete as a local/demo durable fake-client safety artifact. It implements SQLite persistence for side-effect records, approval bindings, and audit events, proving restart/replay duplicate suppression without executing a real GitHub client.

Artifact 4 does not implement real GitHub execution, GitHub token loading, OAuth/OIDC, MCP, frontend, deployment, or production hardening.

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

Review and approve A4.0 before starting any A4.1 implementation.

The next likely work is a narrow durable-state contract sprint, not real GitHub execution.
