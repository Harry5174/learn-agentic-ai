# Interview Notes

How to describe the Agent Factory Development Framework in professional contexts.

---

## Framing

> I noticed that the agent-development workflow itself was becoming reusable, so I extracted the process into a lightweight framework of bootstraps, templates, decision logs, evidence protocols, and memory files. This reduces context drift and makes future artifacts easier to start, review, and hand off.

---

## Key Points

### What It Is

- A Markdown-first process framework for managing the lifecycle of AI agent development artifacts
- Provides session bootstraps, sprint protocols, evidence standards, safety boundary inheritance, and living project memory
- Designed to prevent context drift when work spans multiple sessions with LLM-based IDE agents

### Why It Exists

- Each new LLM session starts with no reliable memory of prior work
- Without structured bootstraps and living memory, context must be recreated from scratch
- The framework captures the reusable workflow pattern: design → implement → evidence → review → handoff
- Safety boundaries from earlier artifacts must be carried forward consistently

### What It Demonstrates

- Process thinking applied to AI-assisted development
- Understanding of LLM context limitations and how to mitigate them
- Structured approach to evidence-based software delivery
- Safety-first design philosophy (fake-default, approval-gated, evidence-required)

### What It Is Not

- Not an automation tool or CLI
- Not a runtime that executes agents
- Not a replacement for human judgment or review
- Not a production deployment system

---

## Sample Interview Question and Answer

**Q:** How do you manage context across multiple AI-assisted development sessions?

**A:** I built a lightweight Markdown framework that provides session bootstraps, sprint lifecycle protocols, and living project memory. Each new session receives a bootstrap document that carries forward project state, approved decisions, and safety invariants. At the end of each sprint, a completion report with evidence feeds into a green-gate review, and the project memory is updated. This means the next session starts from current truth rather than recreating context from scratch.

---

## Honest Boundaries

- The framework is advisory, not enforced by automation
- Templates are manually filled, not auto-generated
- It has been used within a single project (Agent Factory) so far
- It is Markdown-only with no database, CLI, or validation tooling
