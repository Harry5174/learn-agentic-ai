import pytest
from pydantic import ValidationError

from app.identity.schemas import IdentityContext, Role


def test_valid_identity_context_creates_successfully() -> None:
    identity = IdentityContext(
        user_id="user-123",
        api_key_id="key-123",
        role=Role.OPERATOR,
        scopes=["tasks:read", "tools:dry_run"],
    )

    assert identity.user_id == "user-123"
    assert identity.api_key_id == "key-123"
    assert identity.role == Role.OPERATOR
    assert identity.scopes == ["tasks:read", "tools:dry_run"]
    assert identity.tenant_id is None


def test_missing_user_id_fails() -> None:
    with pytest.raises(ValidationError):
        IdentityContext(
            api_key_id="key-123",
            role=Role.VIEWER,
            scopes=["tasks:read"],
        )


def test_invalid_role_fails() -> None:
    with pytest.raises(ValidationError):
        IdentityContext(
            user_id="user-123",
            api_key_id="key-123",
            role="super_admin",
            scopes=["tasks:read"],
        )


def test_scopes_must_be_list_of_strings() -> None:
    with pytest.raises(ValidationError):
        IdentityContext(
            user_id="user-123",
            api_key_id="key-123",
            role=Role.VIEWER,
            scopes="tasks:read",
        )

    with pytest.raises(ValidationError):
        IdentityContext(
            user_id="user-123",
            api_key_id="key-123",
            role=Role.VIEWER,
            scopes=["tasks:read", 123],
        )


def test_scopes_are_required_explicitly() -> None:
    with pytest.raises(ValidationError):
        IdentityContext(
            user_id="user-123",
            api_key_id="key-123",
            role=Role.VIEWER,
        )