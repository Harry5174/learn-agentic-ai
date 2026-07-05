# Project Memory: Agent Factory

---

## Project Purpose
Agent Factory is a foundational platform for building, controlling, and reviewing AI agents with strong safety, approval, and evidence guarantees. It focuses on separating the LLM reasoning from tool execution, ensuring a human-in-the-loop (Product Owner/Operator) remains in control of any external side effects.

---

## Current Phase and Status
**Phase 02** is complete or ready to close, subject to Artifact 06 final publish/tag verification.
**Phase 02.5** is ongoing: Agent Factory Development Framework standardization (AFDF).
**Phase 03** has started with Artifact 07, which is closed as a local/fake-first GitHub Repo Steward prototype.

---

## Artifact Map Summary
- **Artifacts 00–03:** Established identity, policy, approval, and fake side-effect safety.
- **Artifact 04:** Approval-gated real GitHub comment adapter (local/demo).
- **Artifact 05:** Real-mode smoke evidence and release gate.
- **Artifact 06:** Operator approval console/workbench (local/demo).
- **Artifact 07:** GitHub Repo Steward local/fake-first prototype with deterministic local pipeline, adapter boundary, real-read gate, and real-write readiness gate.
- **AFDF (Phase 02.5):** Framework scaffold, template hardening, living memory creation.

See [Artifact Map](artifact-map.md) for detailed artifact ownership and status.

---

## Architecture Principles
- **LLM as a Service:** LLMs propose actions; they do not execute tools directly.
- **Harness Controls Execution:** The local harness controls the flow, enforces policies, and executes approved side effects.
- **Idempotency:** Remote actions (like GitHub comments) must use idempotency markers to prevent duplicate side effects.

---

## Safety Principles
- **Fake/Default First:** Fake clients are the default for all tests and demos.
- **Real Mode Explicit Only:** Real execution requires explicit approval and is release-gated.
- **Approval Before Side Effects:** No external side effect occurs without a recorded approval decision.
- **No Secrets Exposed:** Never print tokens or read `.env` files into logs or AI prompts.

See [Safety Invariants](safety-invariants.md) for the full list.

---

## Reusable Runtime Summary
The platform provides a reusable, safe runtime where actions can be proposed by an AI, placed into a durable SQLite ledger, reviewed by a human operator, and then executed (or rejected) safely. Identity is server-derived, not client-supplied.

---

## Operator Workflow Summary
Operators use a local workbench (Artifact 06) to view proposed actions, inspect the arguments, and issue cryptographic or durable approval decisions. These decisions are bound to the exact side-effect intent.

---

## Real-Mode Evidence Summary
Real-mode execution (e.g., GitHub comments) is proven through the Artifact 05 release gate, which contains the exact audit trails, API responses, and idempotency markers from live execution in an allowlisted test repository. 

---

## AFDF Summary
AFDF (Phase 02.5) provides the Markdown-first workflow for designing, implementing, and reviewing these artifacts. It uses templates and living memory to prevent context drift across AI sessions. It is a process framework, not a code runtime.

---

## Next Direction
**Phase 03 target is vertical agents.**
Artifact 07 is closed as a local/fake-first GitHub Repo Steward prototype. It
does not prove live GitHub reads, real GitHub writes, real executor runtime,
real LLM integration, durable persistence, or production readiness.

Next artifact requires Product Owner selection.

---

## Interview Framing
> Agent Factory is a platform I built to demonstrate how to safely control AI agents. Instead of letting LLMs run tools directly, the LLM proposes an action, a local harness intercepts it, durably logs it, and waits for explicit human approval via an operator workbench. I also built a reusable Markdown-based development framework (AFDF) to manage the AI-assisted engineering lifecycle without losing context across sessions.
