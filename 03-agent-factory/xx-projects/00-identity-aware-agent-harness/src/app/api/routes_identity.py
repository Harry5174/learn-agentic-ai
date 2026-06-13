from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.api.dependencies import get_current_identity
from app.identity.schemas import IdentityContext, Role

router = APIRouter(prefix="/identity", tags=["identity"])


class IdentityResponse(BaseModel):
    user_id: str
    role: Role
    scopes: list[str]


@router.get("/me", response_model=IdentityResponse)
def get_me(
    identity: Annotated[IdentityContext, Depends(get_current_identity)],
) -> IdentityResponse:
    """Return the resolved server-derived identity."""

    return IdentityResponse(
        user_id=identity.user_id,
        role=identity.role,
        scopes=list(identity.scopes),
    )