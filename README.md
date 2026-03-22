# Learning Agentic AI

A hands-on learning repository for exploring and implementing **Agentic AI** concepts, frameworks, and tooling. Each module is an isolated, runnable project managed with [uv](https://docs.astral.sh/uv/) — a fast Python package manager — and focuses on a specific technology or framework in the agentic AI ecosystem.

---

## Repository Structure

```
05_learn_agentic_ai/
├── 00_uv/                          # uv package manager fundamentals
│   ├── 00_hello_world/             # Minimal uv project setup and structure
│   └── 01_blog_flow_uv/            # Blog generation using CrewAI Flows
│
├── 01_lite_llm/                    # LiteLLM unified LLM API gateway
│   └── uv-proj/                    # Calling Gemini 2.0 via LiteLLM
│
└── 02_crewai/                      # CrewAI multi-agent framework
    └── 00_hello_crewai/            # First CrewAI crew with agents and tasks
```

---

## Modules Overview

### `00_uv` — uv Package Manager

Explores [uv](https://docs.astral.sh/uv/), an extremely fast Python package and project manager written in Rust. Covers project initialization, virtual environment management, dependency handling, and running scripts.

| Project | Description |
|---|---|
| `00_hello_world` | Minimal uv project — covers `pyproject.toml`, virtual environments, and script entry points |
| `01_blog_flow_uv` | Blog content generation pipeline built with [CrewAI Flows](https://docs.crewai.com/concepts/flows) and managed via uv |

---

### `01_lite_llm` — LiteLLM

Explores [LiteLLM](https://github.com/BerriAI/litellm), a unified Python SDK that provides a consistent OpenAI-compatible interface across 100+ LLM providers (OpenAI, Anthropic, Gemini, etc.).

| Project | Description |
|---|---|
| `uv-proj` | Calls **Google Gemini 2.0** using LiteLLM's `completion()` API; demonstrates provider-agnostic LLM integration |

---

### `02_crewai` — CrewAI

Explores [CrewAI](https://www.crewai.com/), a framework for orchestrating autonomous AI agents that collaborate to accomplish complex, multi-step tasks.

| Project | Description |
|---|---|
| `00_hello_crewai` | First multi-agent crew — defines agents with roles and goals, assigns tasks, and runs the crew using `crewai run` |

---

## Technologies Used

| Technology | Purpose |
|---|---|
| [uv](https://docs.astral.sh/uv/) | Fast Python package and project manager |
| [CrewAI](https://www.crewai.com/) | Multi-agent orchestration framework |
| [LiteLLM](https://github.com/BerriAI/litellm) | Unified, provider-agnostic LLM API |
| [Google Gemini 2.0](https://deepmind.google/technologies/gemini/) | Large Language Model used for inference |
| [Hatchling](https://hatch.pypa.io/latest/) | Python build backend |
| Python >= 3.12 | Language runtime for all projects |

---

## Prerequisites

- **Python >= 3.12**
- **uv** installed globally:
  ```bash
  pip install uv
  # or (recommended)
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```

---

## Getting Started

Each module is a self-contained uv project. To run any project:

```bash
# 1. Navigate to the project directory
cd 00_uv/00_hello_world

# 2. Install dependencies (creates a virtual environment automatically)
uv sync

# 3. Run the project using its defined script entry point
uv run 00-hello-world
```

For CrewAI projects, you can alternatively use:
```bash
cd 02_crewai/00_hello_crewai
crewai install   # installs dependencies
crewai run       # kicks off the crew
```

---

## Environment Variables

Some projects require API keys. Create a `.env` file inside the relevant project directory:

```env
# For LiteLLM / Gemini projects
GEMINI_API_KEY=your_gemini_api_key_here

# For CrewAI projects (if using OpenAI models)
OPENAI_API_KEY=your_openai_api_key_here
```

> **Note:** `.env` files are excluded from version control via `.gitignore`.

---

## Author

**Harry5174** — [harisjaved010@gmail.com](mailto:harisjaved010@gmail.com)
