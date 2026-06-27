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
│       ├── 03-durable-side-effect-ledger
│       ├── 04-approval-gated-real-github-comment-adapter
│       ├── 05-real-mode-smoke-evidence-release-gate
│       └── 06-operator-approval-workbench
```

**`03-agent-factory`** is the main portfolio and system-building track. It contains coursework, thesis notes, and the `xx-projects/` artifact sequence - a series of progressively more capable controlled-agent harnesses.

---

## Agent Factory - Artifact Sequence

The Agent Factory track builds a series of numbered artifacts, each adding a new layer of controlled AI tool execution.

| # | Artifact | Path | Status | Core Claim |
|---|---------|------|--------|------------|
| 00 | Identity-Aware Stateful Agent Harness | [00-identity-aware-agent-harness](03-agent-factory/xx-projects/00-identity-aware-agent-harness) | Complete / preserved | Server-derived identity, role/scope policy, stateful task lifecycle, approval gates, audit trail, LangGraph checkpoint/resume |
| 01 | LLM-Proposed, Harness-Controlled Skill Runner | [01-llm-proposed-skill-runner](03-agent-factory/xx-projects/01-llm-proposed-skill-runner) | Complete / tagged `artifact-2.2` | Model-shaped skill proposals, proposal validation, policy and approval lifecycle, Skill Runner API, validated scalar arguments, safe rejection of unsafe/control-plane/malformed args |
| 02 | Approval-Gated GitHub Tool Harness | [02-approval-gated-github-tool-harness](03-agent-factory/xx-projects/02-approval-gated-github-tool-harness) | Complete as local/demo fake-client artifact | One approval-gated GitHub issue-comment skill path, validated scalar arguments, trusted repository policy, explicit approval, side-effect idempotency through an in-memory ledger, fake-client execution, audit evidence, adversarial safety tests |
| 03 | Durable Side-Effect Ledger and Approval Binding | [03-durable-side-effect-ledger](03-agent-factory/xx-projects/03-durable-side-effect-ledger) | Complete as local/demo durable fake-client safety artifact | SQLite-backed side-effect records, durable approval binding, restart/replay duplicate suppression, durable audit evidence, fake-client execution |
| 04 | Approval-Gated Real GitHub Comment Adapter | [04-approval-gated-real-github-comment-adapter](03-agent-factory/xx-projects/04-approval-gated-real-github-comment-adapter) | Complete as local/demo real-comment adapter | Fake-client default plus explicitly configured allowlisted real GitHub issue-comment path with durable approval binding, token boundary, remote marker lookup/reconciliation, and audit evidence |
| 05 | Real-Mode Smoke Evidence and Release Gate | [05-real-mode-smoke-evidence-release-gate](03-agent-factory/xx-projects/05-real-mode-smoke-evidence-release-gate) | Complete / published / tagged evidence artifact | Release-gate evidence context for Artifact 04, with redacted manual smoke evidence, offline replay/no-duplicate proof, and zero-network negative proof |
| 06 | Operator Approval Console / Workbench | [06-operator-approval-workbench](03-agent-factory/xx-projects/06-operator-approval-workbench) | Current local/demo workbench artifact (A6.5) | Operator-facing approval inbox, explicit operator approve/reject routes, local static workbench, status/audit/ledger visibility, and demo packaging |

### Key Design Boundaries

- **Artifact 00:** Request bodies cannot claim identity, role, or scopes. Identity is server-derived.
- **Artifact 01 / 2.2:** The proposer proposes. The harness validates, authorizes, approval-gates, executes, and audits. Dry-run only; scalar args only; no real GitHub writes; no live LLM HTTP mode.
- **Artifact 02:** Local/demo fake-client only. No real GitHub API calls. Not production-ready.
- **Artifact 03:** Durable local/demo fake-client safety artifact with SQLite side-effect records, approval bindings, restart/replay duplicate suppression, and durable audit events.
- **Artifact 04:** Local/demo real GitHub comment adapter. Fake client remains default; real mode is explicit, allowlisted, token-boundary-controlled, and narrow to one issue-comment operation.
- **Artifact 05:** Evidence and release-gate context only. It does not own runtime code or broaden GitHub operations.
- **Artifact 06:** Current local/demo operator workbench. Fake/default execution only for the demo; no live GitHub, token, `.env`, Next.js, package-managed frontend, deployment, OAuth/OIDC, or production console claim.

---

## Current Leading Artifact

Artifact 06 is the current leading artifact. It turns the approval-gated harness
lineage into a local/demo operator workbench: a proposed action appears in an
approval inbox, the operator reviews risk/scopes/context/execution mode,
approves or rejects through server-controlled A6 routes, and then inspects
status, decision history, local/demo audit timeline, side-effect/ledger
visibility, and execution-result evidence.

Artifact 06 derives its runtime baseline from Artifact 04. Artifact 05 is
referenced as release-gate evidence context only.

Artifact 06 remains local/demo and fake/default by default. It does not claim
production readiness, production authentication, deployment, arbitrary GitHub
automation, or live GitHub execution for the demo.

---

## Recommended Review Path

1. Start with this root README.
2. Open [03-agent-factory/README.md](03-agent-factory/README.md).
3. Open [03-agent-factory/xx-projects/README.md](03-agent-factory/xx-projects/README.md).
4. Review [Artifact 6 README](03-agent-factory/xx-projects/06-operator-approval-workbench/README.md).
5. Review [Artifact 6 project status](03-agent-factory/xx-projects/06-operator-approval-workbench/docs/status/project-status.md).
6. Review [Artifact 6 operator workbench demo](03-agent-factory/xx-projects/06-operator-approval-workbench/docs/demos/operator-workbench-demo.md).
7. Review [A6.5 demo evidence](03-agent-factory/xx-projects/06-operator-approval-workbench/docs/evidence/a6.5-operator-workbench-demo/README.md).

---

## Current Limitations

This repository contains learning and portfolio artifacts, not a deployed
production service.

**Current Artifact 06 limitations:**

- Local/demo operator workbench only
- Fake/default execution for the demo
- No live GitHub execution required or performed by the demo
- No GitHub token or `.env` required for the demo
- No OAuth/OIDC production identity provider
- No deployment or production authentication
- No Next.js frontend, `package.json`, or `node_modules`
- No MCP integration
- No arbitrary GitHub automation claim
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
