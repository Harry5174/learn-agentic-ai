from typing import Annotated

from fastapi import Header, HTTPException, status

from app.identity.errors import IdentityResolutionError
from app.identity.resolver import resolve_identity_from_api_key
from app.identity.schemas import IdentityContext


def get_current_identity(
    x_api_key: Annotated[str | None, Header(alias="X-API-Key")] = None,
) -> IdentityContext:
    """Resolve the current identity from the X-API-Key header."""

    if x_api_key is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-API-Key header.",
        )

    try:
        return resolve_identity_from_api_key(x_api_key)
    except IdentityResolutionError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key.",
        ) from exc