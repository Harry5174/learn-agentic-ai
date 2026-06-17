# Audit Trail Design

## Purpose

The audit trail records key harness decisions and actions.

In Artifact 1, audit is used to preserve evidence for:

- task/run creation
- skill proposal produced
- proposal validation result
- policy decision
- approval request
- approval grant or rejection
- dry-run tool execution
- final completion, denial, rejection, or failure

## Current Design

```python
create_audit_event(...)
append_audit_event(audit_trail, event)
```

`append_audit_event` returns a new list rather than mutating the original list in
place. This supports LangGraph-style state updates.

## Event Helpers

Common helpers include:

- `create_task_created_event`
- `create_tool_selected_event`
- `create_permission_checked_event`
- `create_approval_requested_event`
- `create_approval_granted_event`
- `create_approval_rejected_event`
- `create_tool_executed_event`

The skill execution graph also creates structured proposal and validation events
with metadata such as:

- skill ID
- skill version
- step IDs
- tool names
- proposal rationale
- validation status
- rejection reasons
- required scopes
- derived risk
- approval requirement

## Boundary

Audit does not:

- control routing
- perform authorization
- approve or reject actions
- execute tools
- persist to a database

Current audit events are in-memory only. They are carried in task/run
state/checkpoints while the process is alive.
