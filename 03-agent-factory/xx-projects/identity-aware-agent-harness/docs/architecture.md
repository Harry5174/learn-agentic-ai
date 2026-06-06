# Architecture

## Project Principle
The LLM proposes. The harness decides.

## Core Safety Invariant
Identity is server-derived, policy is deterministic, and high-risk execution cannot happen before approval.

## High-Level Layers
1. FastAPI API Layer (not implemented yet)
2. Identity Layer: pure resolver implemented
3. Rate Limit Layer: not implemented
4. Local LangGraph Orchestration Layer: implemented locally
5. Policy Guard Layer: implemented
6. Tool Registry Layer: implemented
7. Dry-Run Tool Layer: implemented
8. Audit Layer: implemented
9. Persistence/checkpointing: not implemented

> **Warning:** PAUSED_FOR_APPROVAL is currently represented locally, but full checkpointed interrupt/resume is Sprint 6.

## Intended Graph Flow
*(Architecture only, not implemented yet)*

```text
receive_task
→ interpret_task
→ select_tool
→ policy_guard
    ├── ALLOW → execute_tool → generate_report → END
    ├── DENY → finalize_denial → END
    └── REQUIRE_APPROVAL → pause_for_approval / interrupt
```

On approval:

```text
approve endpoint
→ validate approver identity
→ inject ApprovalDecision
→ resume graph
→ execute_tool
→ generate_report
→ END
```

On rejection:

```text
reject endpoint
→ validate approver identity
→ inject ApprovalDecision
→ resume graph
→ finalize_rejection
→ END
```

> **Note:** PAUSED_FOR_APPROVAL is not completion. It is a resumable suspended state.

## V1 Non-Goals
- OAuth/OIDC
- JWT validation
- real identity provider
- frontend dashboard
- complex RAG
- fine-tuning
- real GitHub writes by default
- multi-agent system
- OPA/Casbin
- Kubernetes
- production deployment hardening
