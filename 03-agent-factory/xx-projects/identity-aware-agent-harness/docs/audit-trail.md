# Audit Trail Design

## Purpose
The audit trail records key harness decisions and actions.

## Current Design
```python
create_audit_event(...)
append_audit_event(audit_trail, event)
```

## Immutable Append
`append_audit_event` returns a new list rather than mutating the original list in place. This supports future LangGraph-style state updates which rely on immutable state progression and reducers.

## Event Helpers
- `create_task_created_event`
- `create_tool_selected_event`
- `create_permission_checked_event`
- `create_approval_requested_event`
- `create_tool_executed_event`

## Boundary
- Audit does not control routing.
- Audit does not perform authorization.
- Audit does not execute tools.
- Audit does not persist to database yet.
