# Tool Registry Design

## Purpose
Explain controlled registry and dry-run execution. The registry provides a controlled boundary of approved tools that the system can execute, preventing arbitrary code execution.

## Current Design
```text
build_default_tool_registry()
→ ToolRegistry
→ list_tools()
→ get_tool(tool_name)
→ execute(tool_name, arguments)
```

## Registered Tools
- `inspect_sandbox_issues`
- `draft_issue_comment`
- `trigger_workflow_dry_run`

## Dry-Run Guarantee
- no external calls
- no GitHub API calls
- no real workflow triggers
- no live issue comments
- high-risk tool returns `would_trigger=False`

## Boundary
- Registry does not know identity.
- Registry does not perform policy checks.
- Registry does not approve actions.
