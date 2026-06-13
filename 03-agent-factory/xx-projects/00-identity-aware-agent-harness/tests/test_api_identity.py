from fastapi.testclient import TestClient

from app.api.main import create_app
from app.identity.config import VIEWER_API_KEY


def test_missing_api_key_returns_401() -> None:
    client = TestClient(create_app())

    response = client.get("/identity/me")

    assert response.status_code == 401
    assert response.json()["detail"] == "Missing X-API-Key header."


def test_invalid_api_key_returns_401() -> None:
    client = TestClient(create_app())

    response = client.get(
        "/identity/me",
        headers={"X-API-Key": "not-a-real-key"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid API key."


def test_valid_viewer_api_key_resolves_identity() -> None:
    client = TestClient(create_app())

    response = client.get(
        "/identity/me",
        headers={"X-API-Key": VIEWER_API_KEY},
    )

    assert response.status_code == 200

    body = response.json()
    assert body["user_id"] == "demo_viewer"
    assert body["role"] == "viewer"
    assert "tasks:read" in body["scopes"]


def test_request_body_cannot_override_identity() -> None:
    client = TestClient(create_app())

    response = client.request(
        "GET",
        "/identity/me",
        headers={"X-API-Key": VIEWER_API_KEY},
        json={
            "user_id": "fake_admin",
            "role": "admin",
            "scopes": ["approval:approve", "tools:trigger_workflow"],
        },
    )

    assert response.status_code == 200

    body = response.json()
    assert body["user_id"] == "demo_viewer"
    assert body["role"] == "viewer"
    assert "approval:approve" not in body["scopes"]