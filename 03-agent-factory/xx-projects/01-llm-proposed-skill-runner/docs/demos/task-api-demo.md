# Task API Demo Flow

This guide demonstrates the inherited Artifact 1-style `/tasks` API that remains
available in Artifact 2.

The primary Artifact 2.1 demo is the skill-runner API guide:
[skill-runner-api-demo.md](skill-runner-api-demo.md).

This guide assumes the local API is running:

```bash
uv run uvicorn app.api.main:app --reload
```

Base URL:

```bash
BASE_URL=http://127.0.0.1:8000
```

Demo API keys:

```bash
VIEWER_KEY=viewer-dev-key
OPERATOR_KEY=operator-dev-key
ADMIN_KEY=admin-dev-key
```

## Flow 1: Viewer Inspects Issues -> Completed

Viewer identity has the scope needed for low-risk issue inspection.

```bash
curl -s -X POST "$BASE_URL/tasks" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $VIEWER_KEY" \
  -d '{"user_query": "inspect sandbox issues"}'
```

Expected result:

```json
{
  "status": "completed",
  "selected_tool_name": "inspect_sandbox_issues",
  "requires_approval": false
}
```

## Flow 2: Viewer Drafts Issue Comment -> Denied

Viewer identity does not have the scope needed for the medium-risk draft tool.

```bash
curl -s -X POST "$BASE_URL/tasks" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $VIEWER_KEY" \
  -d '{"user_query": "draft issue comment"}'
```

Expected result:

```json
{
  "status": "denied",
  "selected_tool_name": "draft_issue_comment",
  "requires_approval": false
}
```

## Flow 3: Operator Triggers Workflow -> Paused for Approval

High-risk workflow triggering cannot execute immediately. It pauses before tool execution.

```bash
curl -s -X POST "$BASE_URL/tasks" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $OPERATOR_KEY" \
  -d '{"user_query": "trigger workflow"}'
```

Expected result:

```json
{
  "status": "paused_for_approval",
  "selected_tool_name": "trigger_workflow_dry_run",
  "requires_approval": true,
  "approval_request": {
    "tool_name": "trigger_workflow_dry_run",
    "requested_by": "demo_operator"
  }
}
```

Copy the returned `task_id` for the approval or rejection flows:

```bash
TASK_ID=replace-with-task-id
```

## Flow 4: Admin Approves -> Completed

Admin approval resumes the checkpointed graph and executes the dry-run tool.

```bash
curl -s -X POST "$BASE_URL/tasks/$TASK_ID/approve" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $ADMIN_KEY" \
  -d '{"reason": "Approved for dry-run execution."}'
```

Expected result:

```json
{
  "status": "completed",
  "selected_tool_name": "trigger_workflow_dry_run",
  "requires_approval": false
}
```

Check audit events:

```bash
curl -s "$BASE_URL/tasks/$TASK_ID/audit"
```

Expected approved path includes:

- `approval_requested`
- `approval_granted`
- `tool_executed`
- `task_completed`

## Flow 5: Admin Rejects -> Rejected

Create a fresh paused task first:

```bash
curl -s -X POST "$BASE_URL/tasks" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $OPERATOR_KEY" \
  -d '{"user_query": "trigger workflow"}'
```

Copy the new `task_id`:

```bash
TASK_ID=replace-with-new-task-id
```

Reject the paused task:

```bash
curl -s -X POST "$BASE_URL/tasks/$TASK_ID/reject" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $ADMIN_KEY" \
  -d '{"reason": "Rejected during review."}'
```

Expected result:

```json
{
  "status": "rejected",
  "requires_approval": false
}
```

Check audit events:

```bash
curl -s "$BASE_URL/tasks/$TASK_ID/audit"
```

Expected rejected path includes:

- `approval_requested`
- `approval_rejected`

Expected rejected path excludes:

- `tool_executed`

## Flow 6: Repeated Task Creation -> 429

`POST /tasks` is limited to 5 requests per 60 seconds per API key.

```bash
for i in 1 2 3 4 5 6; do
  curl -s -o /dev/null -w "%{http_code}\n" -X POST "$BASE_URL/tasks" \
    -H "Content-Type: application/json" \
    -H "X-API-Key: $VIEWER_KEY" \
    -d '{"user_query": "inspect sandbox issues"}'
done
```

Expected result:

```text
202
202
202
202
202
429
```

The rate limit is in-memory and process-local. Restarting the API resets the limit windows.
