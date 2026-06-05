from enum import StrEnum

from pydantic import BaseModel


class Role(StrEnum):
    """Identity roles"""
    VIEWER = "viewer"
    OPERATOR = "operator"
    ADMIN = "admin"


class IdentityContext(BaseModel):
    """Identity context"""
    user_id: str
    api_key_id: str
    role: Role
    scopes: list[str]
    tenant_id: str | None = None