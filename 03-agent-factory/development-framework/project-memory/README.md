# Project Memory

This directory contains the **living project memory** for Agent Factory and future projects managed by the Agent Factory Development Framework (AFDF).

---

## What is Living Memory?

Living memory is the source of truth for project state, decisions, limitations, and evidence. 
It differs from the templates in `docs/memory/` because it contains actual instantiated project data, rather than just the structure.

- `docs/memory/` contains **templates** for memory structures.
- `project-memory/` contains **instances** of those templates, filled with real history.

---

## Important Rules

1. **Not Automatically True:** Living memory is not automatically true just because it exists. It must be updated from repository evidence, completion reports, and green-gate reviews.
2. **Mark Unknowns:** Unknown publish/tag state must be marked unknown until verified.
3. **Avoid Overclaiming:** Never claim a feature is "released" or "published" without evidence of the release tag or merge.

---

## How to Add Another Project

Currently, this folder contains memory for the `agent-factory` project. 
If a new project is started under the AFDF, create a new subfolder (e.g., `project-memory/new-project/`) and copy the templates from `docs/memory/` to instantiate it.

---

## How to Update Memory

Memory must be updated **at the end of a sprint** after a GREEN gate review:
1. Review the completion report and gate outcome.
2. Update the `project-memory.md` with new status.
3. Record new decisions in `decision-log.md`.
4. Update `evidence-index.md` with new evidence artifacts.
5. Record any new limitations or technical debt in their respective registers.

---

## Where to Start

For the main Agent Factory project, start reading here:
- [Agent Factory Memory README](agent-factory/README.md)
