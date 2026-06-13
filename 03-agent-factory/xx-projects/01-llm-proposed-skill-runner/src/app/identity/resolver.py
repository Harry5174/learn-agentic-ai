from app.identity.config import DEMO_API_KEY_IDENTITIES
from app.identity.errors import IdentityResolutionError
from app.identity.schemas import IdentityContext


def resolve_identity_from_api_key(api_key: str) -> IdentityContext:
    """Resolve a server-derived identity from a known API key.

    This resolver intentionally accepts only the API key string.
    It does not accept user_id, role, scopes, or request-body identity data.
    """

    if not api_key or not api_key.strip():
        raise IdentityResolutionError("Missing API key.")

    identity = DEMO_API_KEY_IDENTITIES.get(api_key)

    if identity is None:
        raise IdentityResolutionError("Invalid API key.")

    return identity.model_copy(deep=True)