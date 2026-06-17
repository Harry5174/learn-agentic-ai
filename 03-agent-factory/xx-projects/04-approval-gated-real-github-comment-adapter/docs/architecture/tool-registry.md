# Tool Registry Design

## Purpose

The tool registry provides the controlled execution boundary for dry-run tools.
It prevents arbitrary tool execution by allowing only registered tool names.

Artifact 1 adds a separate `SkillRegistry` above this layer. The skill registry
defines which skills and steps may reference which tools. The tool registry
executes only registered dry-run tools after validation, policy, and approval
requirements are satisfied.

## Current Tool Registry Design

```text
build_default_tool_registry()
-> ToolRegistry
-> list_tools()
-> get_tool(tool_name)
-> execute(tool_name, arguments)
```

## Registered Tools

- `inspect_sandbox_issues`
  - risk: `low`
  - required scope: `tools:inspect`
- `draft_issue_comment`
  - risk: `medium`
  - required scope: `tools:draft`
- `trigger_workflow_dry_run`
  - risk: `high`
  - required scope: `tools:trigger_workflow`

## Dry-Run Guarantee

- no external calls
- no GitHub API calls
- no real workflow triggers
- no live issue comments
- high-risk workflow tool returns dry-run output only

## Skill Runner Boundary

Artifact 1 validates model-shaped proposals before reaching the tool registry.

The sequence is:

```text
SkillProposal
-> ProposalValidator
-> SkillRegistry metadata
-> policy guard
-> approval gate when required
-> ToolRegistry.execute(...)
```

## Tool Argument Limitation

Skill specs include argument-schema metadata, but the current skill execution
graph uses harness-owned default arguments for registered dry-run tools.

The tool registry accepts arguments from the harness. It does not yet receive or
validate arbitrary model-proposed runtime arguments.

## Boundary

The tool registry does not:

- know identity
- perform policy checks
- approve actions
- decide whether high-risk execution may proceed
- call external APIs
