from fastapi.testclient import TestClient

from app.api.main import create_app


def test_get_tools_returns_registered_tool_metadata() -> None:
    client = TestClient(create_app())

    response = client.get("/tools")

    assert response.status_code == 200

    body = response.json()
    tools = body["tools"]

    assert len(tools) == 3

    tool_names = {tool["name"] for tool in tools}
    assert tool_names == {
        "inspect_sandbox_issues",
        "draft_issue_comment",
        "trigger_workflow_dry_run",
    }


def test_get_tools_does_not_expose_callables() -> None:
    client = TestClient(create_app())

    response = client.get("/tools")

    assert response.status_code == 200

    for tool in response.json()["tools"]:
        assert "function" not in tool
        assert "callable" not in tool
        assert "handler" not in tool


def test_get_tools_includes_risk_level_and_required_scopes() -> None:
    client = TestClient(create_app())

    response = client.get("/tools")

    assert response.status_code == 200

    for tool in response.json()["tools"]:
        assert tool["risk_level"] in {"low", "medium", "high"}
        assert isinstance(tool["required_scopes"], list)
        assert tool["required_scopes"]