from enum import StrEnum
from pydantic import BaseModel


class Role(StrEnum):
    """Identity roles."""

    VIEWER = "viewer"
    OPERATOR = "operator"
    ADMIN = "admin"

class IdentityContext(BaseModel):
    """Server-derived identity context.

    API-key mapping is intentionally not implemented in Sprint 0.
    """
    user_id: str
    api_key_id: str
    role: Role
    scopes: list[str]
    tenant_id: str | None = None