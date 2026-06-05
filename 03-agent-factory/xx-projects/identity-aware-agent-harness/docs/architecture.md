# Architecture

## Project Principle
The LLM proposes. The harness decides.

## Core Safety Invariant
Identity is server-derived, policy is deterministic, and high-risk execution cannot happen before approval.

## High-Level Layers
1. FastAPI API Layer (not implemented yet)
2. Identity Layer (not implemented yet)
3. Rate Limit Layer (not implemented yet)
4. LangGraph Orchestration Layer (not implemented yet)
5. Policy Guard Layer (not implemented yet)
6. Tool Registry Layer (not implemented yet)
7. Dry-Run Tool Layer (not implemented yet)
8. Audit Layer (not implemented yet)
9. Persistence Layer (not implemented yet)

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
