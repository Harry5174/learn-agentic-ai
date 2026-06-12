import pytest

from app.identity.config import ADMIN_API_KEY, OPERATOR_API_KEY, VIEWER_API_KEY
from app.identity.errors import IdentityResolutionError
from app.identity.resolver import resolve_identity_from_api_key
from app.identity.schemas import Role


def test_viewer_key_resolves_correctly() -> None:
    identity = resolve_identity_from_api_key(VIEWER_API_KEY)

    assert identity.user_id == "demo_viewer"
    assert identity.api_key_id == "demo-viewer-key"
    assert identity.role == Role.VIEWER
    assert identity.scopes == [
        "tasks:read",
        "tasks:create",
        "tools:inspect",
    ]


def test_operator_key_resolves_correctly() -> None:
    identity = resolve_identity_from_api_key(OPERATOR_API_KEY)

    assert identity.user_id == "demo_operator"
    assert identity.api_key_id == "demo-operator-key"
    assert identity.role == Role.OPERATOR
    assert identity.scopes == [
        "tasks:read",
        "tasks:create",
        "tools:inspect",
        "tools:draft",
        "approval:request",
    ]


def test_admin_key_resolves_correctly() -> None:
    identity = resolve_identity_from_api_key(ADMIN_API_KEY)

    assert identity.user_id == "demo_admin"
    assert identity.api_key_id == "demo-admin-key"
    assert identity.role == Role.ADMIN
    assert identity.scopes == [
        "tasks:read",
        "tasks:create",
        "tools:inspect",
        "tools:draft",
        "tools:trigger_workflow",
        "approval:approve",
        "approval:reject",
    ]


def test_invalid_key_raises_identity_resolution_error() -> None:
    with pytest.raises(IdentityResolutionError, match="Invalid API key"):
        resolve_identity_from_api_key("not-a-real-key")


def test_empty_key_raises_identity_resolution_error() -> None:
    with pytest.raises(IdentityResolutionError, match="Missing API key"):
        resolve_identity_from_api_key("")


def test_whitespace_key_raises_identity_resolution_error() -> None:
    with pytest.raises(IdentityResolutionError, match="Missing API key"):
        resolve_identity_from_api_key("   ")


def test_resolver_accepts_only_api_key_not_user_claimed_identity() -> None:
    identity = resolve_identity_from_api_key(VIEWER_API_KEY)

    assert identity.role == Role.VIEWER
    assert "approval:approve" not in identity.scopes


def test_resolver_returns_fresh_identity_objects() -> None:
    first = resolve_identity_from_api_key(VIEWER_API_KEY)
    second = resolve_identity_from_api_key(VIEWER_API_KEY)

    first.scopes.append("malicious:scope")

    assert "malicious:scope" in first.scopes
    assert "malicious:scope" not in second.scopes
    assert second.scopes == [
        "tasks:read",
        "tasks:create",
        "tools:inspect",
    ]