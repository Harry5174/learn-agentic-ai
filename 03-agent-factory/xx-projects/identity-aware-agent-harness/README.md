# Identity-Aware Stateful Agent Harness

This is a controlled LangGraph-based agent execution harness where an LLM may propose actions, but identity, authorization, approval, execution, and audit are controlled by deterministic application logic.

**Project Principle:** "The LLM proposes. The harness decides."

## What this is not
- not a chatbot
- not a generic RAG wrapper
- not an OAuth project
- not a multi-agent demo

## V1 Scope Summary
- API-key-derived identity later
- deterministic policy guard later
- dry-run tool registry later
- human approval gates later
- checkpointed graph state later
- audit trail later

## Sprint 0 Scope
- project skeleton
- domain contracts
- schema tests

## Current Status
Sprint 0 setup in progress

## Tech Stack
- Python 3.11+
- uv
- Pydantic v2
- Pytest
- Ruff
- LangGraph later, not yet added
- FastAPI later, not yet added

## Basic Commands
- `uv sync`
- `uv run pytest`
- `uv run ruff check .`
