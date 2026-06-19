from app.identity.schemas import IdentityContext, Role

VIEWER_API_KEY = "viewer-dev-key"
OPERATOR_API_KEY = "operator-dev-key"
ADMIN_API_KEY = "admin-dev-key"


DEMO_API_KEY_IDENTITIES: dict[str, IdentityContext] = {
    VIEWER_API_KEY: IdentityContext(
        user_id="demo_viewer",
        api_key_id="demo-viewer-key",
        role=Role.VIEWER,
        scopes=[
            "tasks:read",
            "tasks:create",
            "tools:inspect",
        ],
    ),
    OPERATOR_API_KEY: IdentityContext(
        user_id="demo_operator",
        api_key_id="demo-operator-key",
        role=Role.OPERATOR,
        scopes=[
            "tasks:read",
            "tasks:create",
            "tools:inspect",
            "tools:draft",
            "approval:request",
            "approval:approve",
            "approval:reject",
        ],
    ),
    ADMIN_API_KEY: IdentityContext(
        user_id="demo_admin",
        api_key_id="demo-admin-key",
        role=Role.ADMIN,
        scopes=[
            "tasks:read",
            "tasks:create",
            "tools:inspect",
            "tools:draft",
            "tools:trigger_workflow",
            "tools:post_github_comment",
            "approval:approve",
            "approval:reject",
        ],
    ),
}
