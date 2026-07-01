# Artifact 07 — GitHub Repo Steward Bootstrap Package

## Purpose
This package prepares future sessions to design and implement Artifact 07 (GitHub Repo Steward Agent).

**Artifact 07 has not yet started.** This package exists to ensure that when it does start, the session is fully grounded in the Agent Factory Development Framework (AFDF).

## Package Contents
- `context-load-order.md`: The exact reading sequence for loading context.
- `design-supervisor-kickoff.md`: The prompt to start the design session.
- `implementation-supervisor-kickoff.md`: The prompt to plan implementation after design approval.
- `ide-agent-kickoff.md`: The prompt for the IDE Agent to begin execution.
- `pre-design-repository-inspection.md`: Safe inspection commands.
- `open-decisions-for-design.md`: Key architectural questions that must be resolved.
- `safety-and-scope-boundaries.md`: The strict limits placed on Artifact 07.

## How the Design Supervisor should use it
The Design Supervisor should be provided with `design-supervisor-kickoff.md`, which instructs them to read the context load order, run the inspection, and propose a design that resolves the open decisions while respecting the safety boundaries.

## How the Implementation Supervisor should use it
The Implementation Supervisor should be provided with `implementation-supervisor-kickoff.md` *after* the Design Supervisor's plan is green-gated. They will translate the design into actionable IDE agent tasks.

## How the IDE Agent should use it
The IDE Agent should be provided with `ide-agent-kickoff.md` *after* the implementation plan is approved. They will execute the work, respecting the boundaries, and produce a Completion Report.

## What remains open
All decisions listed in `open-decisions-for-design.md` remain unresolved. The Design Supervisor is responsible for settling them.
