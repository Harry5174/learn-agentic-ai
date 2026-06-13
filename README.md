# Learning Agentic AI

A long-running learning and portfolio repository focused on **applied AI systems**, **agentic AI**, **backend AI engineering**, and **controlled tool-use harnesses**.

Each module is an isolated, runnable project managed with [uv](https://docs.astral.sh/uv/). The repository has evolved from early framework explorations into a structured portfolio track - **Agent Factory** - that demonstrates production-oriented harness design for AI tool execution.

**Project thesis:**
> Agents are useful only when the application harness controls identity, validation, policy, approval, execution, and audit.

---

## Repository Structure

```text
learn-agentic-ai/
├── 00-uv/                          # uv package manager fundamentals
├── 01-lite-llm/uv-proj/             # LiteLLM unified LLM API gateway
├── 02-crewai/00-hello-crewai/      # CrewAI multi-agent framework
├── 03-agent-factory/               # Main portfolio / system-building track
│   ├── 00-about-and-thesis/
│   ├── 01-ai-prompting-2026/
│   ├── 02-how-to-think-ai-era/
│   ├── 03-agentic-coding-crash-course/
│   ├── 04-build-ai-agents/
│   └── xx-projects/                # Numbered artifact sequence
│       ├── 00-identity-aware-agent-harness
│       ├── 01-llm-proposed-skill-runner
│       ├── 02-approval-gated-github-tool-harness
│       └── 03-durable-side-effect-ledger
```

**`03-agent-factory`** is the main portfolio and system-building track. It contains coursework, thesis notes, and the `xx-projects/` artifact sequence - a series of progressively more capable controlled-agent harnesses.

---

## Agent Factory - Artifact Sequence

The Agent Factory track builds a series of numbered artifacts, each adding a new layer of controlled AI tool execution.

| # | Artifact | Path | Status | Core Claim |
|---|---------|------|--------|------------|
| 1 | Identity-Aware Stateful Agent Harness | [00-identity-aware-agent-harness](03-agent-factory/xx-projects/00-identity-aware-agent-harness) | Complete / preserved | Server-derived identity, role/scope policy, stateful task lifecycle, approval gates, audit trail, LangGraph checkpoint/resume |
| 2 / 2.2 | LLM-Proposed, Harness-Controlled Skill Runner | [01-llm-proposed-skill-runner](03-agent-factory/xx-projects/01-llm-proposed-skill-runner) | Complete / tagged `artifact-2.2` | Model-shaped skill proposals, proposal validation, policy and approval lifecycle, Skill Runner API, validated scalar arguments, safe rejection of unsafe/control-plane/malformed args |
| 3 | Approval-Gated GitHub Tool Harness | [02-approval-gated-github-tool-harness](03-agent-factory/xx-projects/02-approval-gated-github-tool-harness) | Complete as local/demo fake-client artifact | One approval-gated GitHub issue-comment skill path, validated scalar arguments, trusted repository policy, explicit approval, side-effect idempotency through an in-memory ledger, fake-client execution, audit evidence, adversarial safety tests |
| 4 | Durable Side-Effect Ledger and Approval Binding | [03-durable-side-effect-ledger](03-agent-factory/xx-projects/03-durable-side-effect-ledger) | Complete as local/demo durable fake-client safety artifact | SQLite-backed side-effect records, durable approval binding, restart/replay duplicate suppression, durable audit evidence, fake-client execution |

### Key Design Boundaries

- **Artifact 1:** Request bodies cannot claim identity, role, or scopes. Identity is server-derived.
- **Artifact 2 / 2.2:** The proposer proposes. The harness validates, authorizes, approval-gates, executes, and audits. Dry-run only; scalar args only; no real GitHub writes; no live LLM HTTP mode.
- **Artifact 3:** Local/demo fake-client only. No real GitHub API calls. Not production-ready.
- **Artifact 4:** Complete as a local/demo fake-client artifact. SQLite persistence, durable approval binding, restart/replay duplicate suppression, and durable audit events are implemented. No real network execution.

---

## Current Leading Artifact

Artifact 4 is complete as a local/demo durable fake-client safety artifact. It implements SQLite persistence semantics for durable side-effect records, approval bindings, and audit events.

Artifact 4 does not implement real GitHub execution, GitHub token loading, OAuth/OIDC, MCP, frontend, deployment, or production hardening.

---

## Recommended Review Path

1. Start with this root README.
2. Open [03-agent-factory/README.md](03-agent-factory/README.md).
3. Open [03-agent-factory/xx-projects/README.md](03-agent-factory/xx-projects/README.md).
4. Review [Artifact 4 README](03-agent-factory/xx-projects/03-durable-side-effect-ledger/README.md).
5. Review [Artifact 4 durable-state spec](03-agent-factory/xx-projects/03-durable-side-effect-ledger/docs/specs/artifact-4-durable-side-effect-ledger.md).
6. Review [Artifact 4 persistence boundary](03-agent-factory/xx-projects/03-durable-side-effect-ledger/docs/architecture/persistence-boundary.md).

---

## Current Limitations

This repository contains learning and portfolio artifacts, not a deployed production service.

**Current Artifact 4 limitations:**

- Fake-client only
- Local/demo SQLite database only
- No real GitHub API / network execution
- No GitHub token loading
- No OAuth/OIDC production identity provider
- No frontend / operator console
- No MCP integration
- Not production-ready

---

## Early Learning Modules

The early modules remain as reference material from the initial learning phase.

### `00-uv` - uv Package Manager

| Project | Description |
|---------|-------------|
| `00_hello_world` | Minimal uv project - `pyproject.toml`, virtual environments, script entry points |
| `01_blog_flow_uv` | Blog generation pipeline built with CrewAI Flows, managed via uv |

### `01-lite-llm` - LiteLLM

| Project | Description |
|---------|-------------|
| `uv-proj` | Calls Google Gemini 2.0 using LiteLLM's `completion()` API |

### `02-crewai` - CrewAI

| Project | Description |
|---------|-------------|
| `00_hello_crewai` | First multi-agent crew - agents with roles, goals, tasks |

---

## Technologies Used

| Technology | Purpose |
|-----------|---------|
| [uv](https://docs.astral.sh/uv/) | Fast Python package and project manager |
| [FastAPI](https://fastapi.tiangolo.com/) | API framework for agent harness endpoints |
| [LangGraph](https://langchain-ai.github.io/langgraph/) | Stateful graph execution with checkpoint/resume |
| [Pydantic](https://docs.pydantic.dev/) | Strict domain model validation |
| [pytest](https://docs.pytest.org/) | Test framework for all artifacts |
| [Ruff](https://docs.astral.sh/ruff/) | Python linter and formatter |
| [CrewAI](https://www.crewai.com/) | Multi-agent orchestration (early modules) |
| [LiteLLM](https://github.com/BerriAI/litellm) | Unified, provider-agnostic LLM API (early modules) |
| Python >= 3.12 | Language runtime |

---

## Prerequisites

- **Python >= 3.12**
- **uv** installed:
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```

---

## Author

**Harry5174** - [harisjaved010@gmail.com](mailto:harisjaved010@gmail.com)
