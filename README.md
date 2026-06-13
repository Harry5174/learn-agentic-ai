# Learning Agentic AI

A long-running learning and portfolio repository focused on **applied AI systems**, **agentic AI**, **backend AI engineering**, and **controlled tool-use harnesses**.

Each module is an isolated, runnable project managed with [uv](https://docs.astral.sh/uv/). The repository has evolved from early framework explorations into a structured portfolio track — **Agent Factory** — that demonstrates production-oriented harness design for AI tool execution.

**Project thesis:**
> Agents are useful only when the application harness controls identity, validation, policy, approval, execution, and audit.

---

## Repository Structure

```
learn-agentic-ai/
├── 00-uv/                          # uv package manager fundamentals
├── 01-lite-llm/uv-proj/            # LiteLLM unified LLM API gateway
├── 02-crewai/00-hello-crewai/      # CrewAI multi-agent framework
├── 03-agent-factory/               # ★ Main portfolio / system-building track
│   ├── 00-about-and-thesis/
│   ├── 01-ai-prompting-2026/
│   ├── 02-how-to-think-ai-era/
│   ├── 03-agentic-coding-crash-course/
│   ├── 04-build-ai-agents/
│   └── xx-projects/                # Numbered artifact sequence
│       ├── 00-identity-aware-agent-harness
│       ├── 01-llm-proposed-skill-runner
│       └── 02-approval-gated-github-tool-harness
```

**`03-agent-factory`** is the main portfolio and system-building track. It contains coursework, thesis notes, and the `xx-projects/` artifact sequence — a series of progressively more capable controlled-agent harnesses.

---

## Agent Factory — Artifact Sequence

The Agent Factory track builds a series of numbered artifacts, each adding a new layer of controlled AI tool execution.

| # | Artifact | Path | Status | Core Claim |
|---|---------|------|--------|------------|
| 1 | Identity-Aware Stateful Agent Harness | [00-identity-aware-agent-harness](03-agent-factory/xx-projects/00-identity-aware-agent-harness) | Complete / preserved | Server-derived identity, role/scope policy, stateful task lifecycle, approval gates, audit trail, LangGraph checkpoint/resume |
| 2 / 2.2 | LLM-Proposed, Harness-Controlled Skill Runner | [01-llm-proposed-skill-runner](03-agent-factory/xx-projects/01-llm-proposed-skill-runner) | Complete / tagged `artifact-2.2` | Model-shaped skill proposals (SkillSpec / SkillStep / SkillProposal), proposal validation, policy and approval lifecycle, Skill Runner API, validated scalar arguments, safe rejection of unsafe/control-plane/malformed args |
| 3 | Approval-Gated GitHub Tool Harness | [02-approval-gated-github-tool-harness](03-agent-factory/xx-projects/02-approval-gated-github-tool-harness) | Complete as local/demo fake-client artifact | One approval-gated GitHub issue-comment skill path, validated scalar arguments, trusted repository policy, explicit approval, side-effect idempotency (in-memory ledger), FakeGitHubIssueCommentClient execution, audit evidence, adversarial safety tests |

### Key Design Boundaries

- **Artifact 1:** Request bodies cannot claim identity, role, or scopes. Identity is server-derived.
- **Artifact 2 / 2.2:** The proposer proposes. The harness validates, authorizes, approval-gates, executes, and audits. Dry-run only; scalar args only; no real GitHub writes; no live LLM HTTP mode.
- **Artifact 3:** Local/demo fake-client only. No real GitHub API calls. Not production-ready.

---

## What Artifact 3 Demonstrates

Artifact 3 demonstrates a local/demo approval-gated GitHub issue-comment harness path where:

- Model-proposed scalar arguments are validated
- Repository policy is checked against a trusted-repository allowlist
- Explicit approval is required before execution
- Side-effect idempotency is checked with an in-memory ledger
- Fake-client execution is used (no real GitHub network calls)
- Audit evidence is recorded for every decision
- Adversarial safety tests verify rejection of unsafe inputs

### What Artifact 3 Does Not Claim

Artifact 3 does **not** claim or implement:

- Real GitHub comments are posted
- Production readiness
- Durable replay protection
- OAuth-secured identity
- Arbitrary repository support
- General GitHub automation platform capabilities
- Autonomous repository modification

---

## Recommended Review Path

1. Start with this root README.
2. Open [03-agent-factory/README.md](03-agent-factory/README.md).
3. Open [03-agent-factory/xx-projects/README.md](03-agent-factory/xx-projects/README.md).
4. Review [Artifact 3 README](03-agent-factory/xx-projects/02-approval-gated-github-tool-harness/docs/README.md).
5. Review [Artifact 3 demo](03-agent-factory/xx-projects/02-approval-gated-github-tool-harness/docs/demos/github-comment-tool-demo.md).
6. Review [Artifact 3 adversarial evidence](03-agent-factory/xx-projects/02-approval-gated-github-tool-harness/docs/adversarial-github-side-effect-safety.md).

---

## Current Limitations

This repository contains learning and portfolio artifacts, not a deployed production service.

**Current Artifact 3 limitations:**

- Local/demo only
- Fake GitHub client only
- No real GitHub API / network execution
- No GitHub token loading
- No durable side-effect ledger
- No durable audit store
- No OAuth/OIDC production identity provider
- No frontend / operator console
- No MCP integration
- Not production-ready

---

## Early Learning Modules

The early modules remain as reference material from the initial learning phase.

### `00-uv` — uv Package Manager

| Project | Description |
|---------|-------------|
| `00_hello_world` | Minimal uv project — `pyproject.toml`, virtual environments, script entry points |
| `01_blog_flow_uv` | Blog generation pipeline built with CrewAI Flows, managed via uv |

### `01-lite-llm` — LiteLLM

| Project | Description |
|---------|-------------|
| `uv-proj` | Calls Google Gemini 2.0 using LiteLLM's `completion()` API |

### `02-crewai` — CrewAI

| Project | Description |
|---------|-------------|
| `00_hello_crewai` | First multi-agent crew — agents with roles, goals, tasks |


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

**Harry5174** — [harisjaved010@gmail.com](mailto:harisjaved010@gmail.com)
