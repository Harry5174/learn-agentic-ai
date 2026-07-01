# Phase Map

---

## Phase 00 / Foundation
- **Purpose:** Establish the fundamental local test harness and stateful agent loop.
- **Included Artifacts:** Artifact 00.
- **Status:** Complete.
- **Proves:** We can run an agent loop locally with state.
- **Does Not Prove:** Safety, real execution, or approvals.

## Phase 01 / Safety and Approval Building Blocks
- **Purpose:** Build the core primitives for identity, policy, approval, and fake side-effect safety.
- **Included Artifacts:** Artifact 01, Artifact 02, Artifact 03.
- **Status:** Complete.
- **Proves:** The harness can pause on tools, require approval, and use a durable SQLite ledger for fake side effects.
- **Does Not Prove:** Real external execution.

## Phase 02 / Reusable Safe Agent Runtime
- **Purpose:** Prove that the safety building blocks can securely manage real external side effects (like GitHub comments) and provide a usable operator console.
- **Included Artifacts:** Artifact 04, Artifact 05, Artifact 06.
- **Status:** Complete or ready to close, subject to final publish/tag verification for Artifact 06.
- **Proves:** We can safely execute real GitHub comments through an allowlist, prove it with a release gate, and approve it via a local workbench.
- **Does Not Prove:** Value-add AI reasoning (it only proves the plumbing).

## Phase 02.5 / Agent Factory Development Framework
- **Purpose:** Standardize the development, implementation, and review lifecycle for future AI agent artifacts to prevent context drift.
- **Included Work:** AFDF.0, AFDF.1, AFDF.2 (Current).
- **Status:** In Progress.
- **Proves:** We can manage AI-assisted sessions using a Markdown-first process framework.
- **Does Not Prove:** Automated validation or orchestration.

## Phase 03 / Vertical Agent Platform
- **Purpose:** Build vertical agents that utilize the Phase 02 safe runtime to solve actual problems.
- **Included Artifacts:** Artifact 07 (Candidate: GitHub Repo Steward Agent) and beyond.
- **Status:** Not Started.
- **Proves:** The safe runtime provides value in real-world scenarios.
- **Does Not Prove:** Multi-agent orchestration or SaaS deployment.

## Phase 04 / Digital FTE Platform
- **Purpose:** Orchestrate multiple vertical agents into long-running, autonomous "Digital FTEs."
- **Status:** Not Started.
