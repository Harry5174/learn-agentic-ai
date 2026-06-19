import re
from pathlib import Path

from fastapi.testclient import TestClient

from app.api.main import create_app

ARTIFACT_ROOT = Path(__file__).resolve().parents[1]
STATIC_ROOT = ARTIFACT_ROOT / "src" / "app" / "operator" / "static"
WORKBENCH_HTML = STATIC_ROOT / "workbench.html"
WORKBENCH_CSS = STATIC_ROOT / "workbench.css"
WORKBENCH_JS = STATIC_ROOT / "workbench.js"
SAFETY_NOTICE = (
    "Local demo workbench. Fake/default execution only. No live GitHub "
    "execution. No GitHub token or .env required."
)


def _asset_text() -> str:
    return "\n".join(
        [
            WORKBENCH_HTML.read_text(encoding="utf-8"),
            WORKBENCH_CSS.read_text(encoding="utf-8"),
            WORKBENCH_JS.read_text(encoding="utf-8"),
        ]
    )


def test_operator_workbench_route_returns_static_html() -> None:
    client = TestClient(create_app())

    response = client.get("/operator/workbench")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert SAFETY_NOTICE in response.text


def test_operator_workbench_local_assets_are_served() -> None:
    client = TestClient(create_app())

    css_response = client.get("/operator/workbench.css")
    js_response = client.get("/operator/workbench.js")

    assert css_response.status_code == 200
    assert "text/css" in css_response.headers["content-type"]
    assert js_response.status_code == 200
    assert "application/javascript" in js_response.headers["content-type"]


def test_operator_workbench_references_only_a6_operator_api_routes() -> None:
    asset_text = _asset_text()

    assert '"/operator/approvals"' in asset_text
    assert '"/operator/approvals/{approval_id}"' in asset_text
    assert '"/operator/approvals/{approval_id}/approve"' in asset_text
    assert '"/operator/approvals/{approval_id}/reject"' in asset_text

    inherited_fragments = [
        "/" + "skill" + "-runs" + "/",
        "/" + "tasks" + "/",
        "approve-run",
        "reject-run",
    ]
    for fragment in inherited_fragments:
        assert fragment not in asset_text


def test_operator_workbench_has_no_frontend_package_or_nextjs_files() -> None:
    forbidden_names = {
        "package" + ".json",
        "node" + "_modules",
    }
    forbidden_prefixes = ("next" + ".config",)

    matches = [
        path
        for path in ARTIFACT_ROOT.rglob("*")
        if path.name in forbidden_names
        or path.name.startswith(forbidden_prefixes)
    ]

    assert matches == []


def test_operator_workbench_uses_no_external_assets_or_urls() -> None:
    asset_text = _asset_text()

    assert "http://" not in asset_text
    assert "https://" not in asset_text
    assert "cdn." not in asset_text.lower()
    assert "unpkg" not in asset_text.lower()


def test_operator_workbench_assets_do_not_embed_key_or_token_values() -> None:
    asset_text = _asset_text()
    token_prefixes = ["g" + "hp_", "github" + "_pat_", "gho_", "ghu_", "ghs_", "ghr_"]
    env_names = ["GITHUB_ACCESS" + "_TOKEN=", "AGENT_FACTORY_GITHUB" + "_TOKEN="]
    token_pattern = re.compile(
        "|".join(re.escape(value) for value in [*token_prefixes, "Bearer ", *env_names])
    )

    assert token_pattern.search(asset_text) is None
    assert "viewer-dev-key" not in asset_text
    assert "operator-dev-key" not in asset_text
    assert "admin-dev-key" not in asset_text


def test_operator_workbench_keeps_api_key_in_memory_only() -> None:
    asset_text = _asset_text()
    browser_storage_names = ["local" + "Storage", "session" + "Storage"]

    for storage_name in browser_storage_names:
        assert storage_name not in asset_text
    assert '"X-API-Key": apiKey' in asset_text


def test_operator_workbench_uses_safe_dom_rendering_patterns() -> None:
    js_text = WORKBENCH_JS.read_text(encoding="utf-8")
    unsafe_html_property = "inner" + "HTML"
    unsafe_react_property = "dangerously" + "SetInnerHTML"
    dangerous_img = "<img src=x onerror=alert(1)>"
    dangerous_script = "<script>alert(1)</script>"

    assert unsafe_html_property not in js_text
    assert unsafe_react_property not in js_text
    assert "createElement" in js_text
    assert "textContent" in js_text
    assert dangerous_img not in js_text
    assert dangerous_script not in js_text


def test_operator_workbench_decision_flows_target_a6_operator_routes() -> None:
    js_text = WORKBENCH_JS.read_text(encoding="utf-8")

    assert '"/operator/approvals/{approval_id}/approve"' in js_text
    assert '"/operator/approvals/{approval_id}/reject"' in js_text
    assert "APPROVE_ROUTE_TEMPLATE" in js_text
    assert "REJECT_ROUTE_TEMPLATE" in js_text


def test_operator_workbench_requires_no_github_token_or_env(monkeypatch) -> None:
    monkeypatch.delenv("AGENT_FACTORY_GITHUB_TOKEN", raising=False)
    client = TestClient(create_app())

    response = client.get("/operator/workbench")

    assert response.status_code == 200
    assert "No GitHub token or .env required." in response.text


def test_operator_workbench_does_not_call_live_github_client() -> None:
    asset_text = _asset_text()

    assert "real_client" not in asset_text
    assert "RealGitHub" not in asset_text
    assert "api." + "github.com" not in asset_text
