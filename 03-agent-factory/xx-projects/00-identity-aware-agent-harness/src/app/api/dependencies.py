from typing import Annotated

from fastapi import Depends, Header, HTTPException, Request, status

from app.api.rate_limiter import InMemoryRateLimiter, RateLimitExceeded
from app.identity.errors import IdentityResolutionError
from app.identity.resolver import resolve_identity_from_api_key
from app.identity.schemas import IdentityContext

DEFAULT_RATE_LIMIT_WINDOW_SECONDS = 60
TASK_CREATE_RATE_LIMIT = 5
APPROVAL_ACTION_RATE_LIMIT = 10
TASK_CREATE_ROUTE_GROUP = "task_create"
APPROVAL_ACTION_ROUTE_GROUP = "approval_action"
RATE_LIMIT_EXCEEDED_DETAIL = "Rate limit exceeded."


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


def get_rate_limiter(request: Request) -> InMemoryRateLimiter:
    """Return the app-local in-memory rate limiter."""

    limiter = getattr(request.app.state, "rate_limiter", None)

    if limiter is None:
        limiter = InMemoryRateLimiter()
        request.app.state.rate_limiter = limiter

    return limiter


def enforce_rate_limit(
    *,
    identity: IdentityContext,
    limiter: InMemoryRateLimiter,
    route_group: str,
    limit: int,
    window_seconds: int = DEFAULT_RATE_LIMIT_WINDOW_SECONDS,
) -> None:
    """Enforce a route-group limit keyed from server-derived identity."""

    try:
        limiter.check(
            key=f"{identity.api_key_id}:{route_group}",
            limit=limit,
            window_seconds=window_seconds,
        )
    except RateLimitExceeded as exc:
        retry_after = str(max(1, int(exc.retry_after_seconds)))
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=RATE_LIMIT_EXCEEDED_DETAIL,
            headers={"Retry-After": retry_after},
        ) from exc


def enforce_task_create_rate_limit(
    identity: Annotated[IdentityContext, Depends(get_current_identity)],
    limiter: Annotated[InMemoryRateLimiter, Depends(get_rate_limiter)],
) -> IdentityContext:
    """Resolve identity and enforce task creation rate limits."""

    enforce_rate_limit(
        identity=identity,
        limiter=limiter,
        route_group=TASK_CREATE_ROUTE_GROUP,
        limit=TASK_CREATE_RATE_LIMIT,
    )
    return identity


def enforce_approval_action_rate_limit(
    identity: Annotated[IdentityContext, Depends(get_current_identity)],
    limiter: Annotated[InMemoryRateLimiter, Depends(get_rate_limiter)],
) -> IdentityContext:
    """Resolve identity and enforce approval/rejection rate limits."""

    enforce_rate_limit(
        identity=identity,
        limiter=limiter,
        route_group=APPROVAL_ACTION_ROUTE_GROUP,
        limit=APPROVAL_ACTION_RATE_LIMIT,
    )
    return identity
