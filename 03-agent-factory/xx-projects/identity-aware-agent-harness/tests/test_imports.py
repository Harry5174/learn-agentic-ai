def test_app_imports() -> None:
    import app

    assert app is not None


def test_schema_modules_import() -> None:
    from app.approval import schemas as approval_schemas
    from app.audit import schemas as audit_schemas
    from app.identity import schemas as identity_schemas
    from app.policy import schemas as policy_schemas
    from app.state import schemas as state_schemas
    from app.tools import schemas as tool_schemas

    assert identity_schemas is not None
    assert tool_schemas is not None
    assert policy_schemas is not None
    assert approval_schemas is not None
    assert audit_schemas is not None
    assert state_schemas is not None