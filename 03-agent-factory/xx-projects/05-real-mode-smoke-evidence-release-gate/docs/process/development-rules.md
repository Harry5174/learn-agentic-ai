# Development Rules

Artifact 05 follows the Agent Factory process inherited from Artifact 04 while
remaining an evidence and release-gate artifact.

## Core Process

- Work one sprint at a time.
- Review relevant specs, docs, and code before implementation.
- Keep changes small, reviewable, and tied to the current sprint goal.
- Prefer test-backed behavior when helper code is added.
- Preserve fake/default behavior before any real execution.
- Do not run live GitHub unless the current sprint explicitly approves it.

## Safety Rules

- Do not read or print `.env` contents.
- Do not require or load the user's real GitHub token.
- Do not print token values, Authorization headers, or raw secret-bearing
  transport output.
- Do not push or tag during implementation sprints unless explicitly approved.
- Keep live GitHub execution out of CI.
- Keep any future live smoke manual and explicitly approved by the Product
  Owner in that sprint.

## Scope Rules

Artifact 05 may add documentation, evidence templates, safety checklists, and
small isolated helper code for preflight or redaction validation.

Artifact 05 must not add:

- a new GitHub adapter
- broad GitHub automation
- PR creation
- issue creation
- branch creation
- repository file writes
- workflow dispatch
- labels or milestones
- OAuth/OIDC
- MCP
- deployment
- operator UI
- Digital FTE behavior
- production-readiness claims
- universal exactly-once claims

## Runtime Boundary

No `src/app` package is intentional in Artifact 05. Runtime behavior remains in
Artifact 04. Artifact 05 is the release-gate and evidence layer around that
runtime boundary, so its helper code stays isolated under `tools/` and is not
wired into the Artifact 04 application path.

This keeps A5.x work inspectable as offline evidence preparation until a later
Product Owner-approved live smoke sprint.
