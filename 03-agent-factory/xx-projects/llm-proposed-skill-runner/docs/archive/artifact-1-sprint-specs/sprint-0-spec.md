# Sprint 0: Project Skeleton + Domain Contracts

## Objective
Create initial Python project structure and define core domain contracts before implementing graph orchestration, identity injection, tools, policy logic, persistence, FastAPI routes, rate limiting, or LLM calls.

## Scope
- project folder structure
- minimal Python package setup
- README
- .env.example
- typed Pydantic domain schema models/enums
- schema validation tests
- import smoke tests

## Non-Goals
- final LangGraph runtime state
- LangGraph graph
- reducers
- checkpointing
- FastAPI routes
- OAuth/OIDC
- JWT validation
- real API-key auth dependency
- tool registry
- dry-run tools
- policy guard logic
- audit persistence
- database
- rate limiting
- LLM calls
- GitHub API integration
- frontend

## Planned Package Structure
```text
src/app/
├── identity/
├── state/
├── tools/
├── policy/
├── approval/
└── audit/

tests/
├── test_imports.py
├── test_identity_schemas.py
├── test_state_schemas.py
├── test_tool_schemas.py
├── test_policy_schemas.py
├── test_approval_schemas.py
└── test_audit_schemas.py
```

## Domain Contracts to Implement Later in Sprint 0
- Role
- IdentityContext
- RiskLevel
- ToolCallRequest
- ToolSpec
- PolicyDecisionType
- PolicyDecision
- ApprovalStatus
- ApprovalRequest
- ApprovalDecision
- AuditEventType
- AuditEvent
- TaskStatus

## Acceptance Criteria
- project imports successfully
- all schema tests pass
- no final LangGraph runtime state is implemented
- no graph/API/tool execution logic is implemented
- mutable defaults use safe factories
- audit timestamps are timezone-aware
- schemas avoid unnecessary circular dependencies
- README clearly states the project is a harness, not a chatbot/RAG/OAuth project
