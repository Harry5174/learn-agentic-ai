import time
from collections.abc import Callable
from dataclasses import dataclass


class RateLimitExceeded(Exception):
    """Raised when a fixed-window rate limit has been exceeded."""

    def __init__(self, retry_after_seconds: float) -> None:
        self.retry_after_seconds = retry_after_seconds
        super().__init__("Rate limit exceeded.")


@dataclass
class _RateLimitWindow:
    started_at: float
    count: int = 0


class InMemoryRateLimiter:
    """Simple in-memory fixed-window rate limiter."""

    def __init__(
        self,
        time_provider: Callable[[], float] = time.monotonic,
    ) -> None:
        self._time_provider = time_provider
        self._windows: dict[str, _RateLimitWindow] = {}

    def check(
        self,
        *,
        key: str,
        limit: int,
        window_seconds: int,
    ) -> None:
        """Allow a request or raise when the key is over its fixed-window limit."""

        now = self._time_provider()
        window = self._windows.get(key)

        if window is None or now - window.started_at >= window_seconds:
            self._windows[key] = _RateLimitWindow(started_at=now, count=1)
            return

        if window.count >= limit:
            retry_after = window_seconds - (now - window.started_at)
            raise RateLimitExceeded(retry_after_seconds=max(retry_after, 0.0))

        window.count += 1
