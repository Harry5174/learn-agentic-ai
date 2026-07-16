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
| 7 | [GitHub Repo Steward](xx-projects/07-github-repo-steward) | Closed as a local/fake-first GitHub Repo Steward prototype. Production development is deferred to the dedicated `github-steward` repository after AFEF v0.2.0 is released and adoption is authorized. |

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
├── development-framework/          # Frozen historical AFDF snapshot
└── xx-projects/                    # Numbered artifact sequence
    ├── 00-identity-aware-agent-harness
    ├── 01-llm-proposed-skill-runner
    ├── 02-approval-gated-github-tool-harness
    ├── 03-durable-side-effect-ledger
    ├── 04-approval-gated-real-github-comment-adapter
    ├── 05-real-mode-smoke-evidence-release-gate
    ├── 06-operator-approval-workbench
    └── 07-github-repo-steward
```

---

## Current Leading Artifact

Artifact 07 completed through Sprint 7.12 and is closed as a local/fake-first prototype. It demonstrated fixture intake, deterministic analysis, proposals, policy evaluation, approval records, audit records, dry-run results, and readiness gates, but did not implement the production GitHub Steward.

The production successor belongs in the dedicated `github-steward` repository, which remains reserved and Git-empty. Implementation begins only after the AFEF v0.2.0 release and Product Owner adoption authorization. See [xx-projects/README.md](xx-projects/README.md) for the detailed historical record.

---

## Development Framework

The in-repository [Agent Factory Development Framework](development-framework/) (AFDF) is a frozen historical snapshot. It was the valid framework location for earlier Agent Factory work and remains preserved for provenance and earlier Artifact context.

Its canonical successor is the [Agent Factory Engineering Framework](https://github.com/Harry5174/agent-factory-engineering-framework) (AFEF). AFEF v0.1.0 established the first canonical public baseline; current framework use should begin from the dedicated AFEF repository, and the [AFEF Releases page](https://github.com/Harry5174/agent-factory-engineering-framework/releases) determines the current released version.

See the [legacy transition record](development-framework/LEGACY.md) for the freeze rules and historical ownership boundary.

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

The legacy AFDF-to-AFEF transition is complete in this revision. The next work is:

1. Build and release the minimum AFEF v0.2.0 adoption baseline.
2. Initialize and adopt AFEF in the dedicated `github-steward` repository.
3. Begin the production Vertical GitHub Steward Agent through bounded sprints.
