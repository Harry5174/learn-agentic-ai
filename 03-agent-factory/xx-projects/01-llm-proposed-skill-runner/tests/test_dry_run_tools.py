from app.tools.dry_run_tools import (
    draft_issue_comment,
    inspect_sandbox_issues,
    trigger_workflow_dry_run,
)


def test_inspect_sandbox_issues_returns_predictable_issue_data() -> None:
    result = inspect_sandbox_issues({})

    assert result.tool_name == "inspect_sandbox_issues"
    assert result.success is True
    assert result.dry_run is True
    assert result.result["repository"] == "sandbox/demo-repo"
    assert result.result["issues"] == [
        {"id": 1, "title": "CI workflow failing", "status": "open"},
        {"id": 2, "title": "Dependency update needed", "status": "open"},
    ]


def test_draft_issue_comment_returns_dry_run_payload() -> None:
    result = draft_issue_comment(
        {
            "issue_id": 1,
            "comment_body": "Proposed investigation summary.",
        }
    )

    assert result.tool_name == "draft_issue_comment"
    assert result.success is True
    assert result.dry_run is True
    assert result.result == {
        "issue_id": 1,
        "comment_body": "Proposed investigation summary.",
        "would_post": False,
    }


def test_trigger_workflow_dry_run_returns_simulated_trigger_payload() -> None:
    result = trigger_workflow_dry_run(
        {
            "workflow_name": "ci.yml",
            "ref": "main",
        }
    )

    assert result.tool_name == "trigger_workflow_dry_run"
    assert result.success is True
    assert result.dry_run is True
    assert result.result == {
        "workflow_name": "ci.yml",
        "ref": "main",
        "would_trigger": False,
        "simulated_status": "queued",
    }


def test_all_dry_run_tools_indicate_dry_run_true() -> None:
    results = [
        inspect_sandbox_issues({}),
        draft_issue_comment({"issue_id": 1, "comment_body": "test"}),
        trigger_workflow_dry_run({"workflow_name": "ci.yml", "ref": "main"}),
    ]

    assert all(result.dry_run is True for result in results)


def test_dry_run_tools_do_not_report_external_execution() -> None:
    comment_result = draft_issue_comment(
        {"issue_id": 1, "comment_body": "Do not post."}
    )
    workflow_result = trigger_workflow_dry_run(
        {"workflow_name": "ci.yml", "ref": "main"}
    )

    assert comment_result.result["would_post"] is False
    assert workflow_result.result["would_trigger"] is False