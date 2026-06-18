import os
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Protocol


GITHUB_TOKEN_ENV_VAR = "AGENT_FACTORY_GITHUB_TOKEN"
GITHUB_TOKEN_NOT_CONFIGURED_MESSAGE = "GitHub token is not configured."
GITHUB_TOKEN_UNAVAILABLE_MESSAGE = "GitHub token is unavailable."
GITHUB_CREDENTIALS_UNAVAILABLE_MESSAGE = "GitHub credentials are unavailable."


class MissingGitHubTokenError(RuntimeError):
    """Raised when trusted server-side GitHub credentials are unavailable."""

    def __init__(self, message: str = GITHUB_TOKEN_NOT_CONFIGURED_MESSAGE) -> None:
        super().__init__(message)


class GitHubTokenProvider(Protocol):
    """Server-side boundary for obtaining a GitHub token."""

    def get_token(self) -> str:
        """Return a token from trusted server-side configuration."""


@dataclass(frozen=True)
class EnvironmentGitHubTokenProvider:
    """Read a GitHub token from server-side environment only."""

    env_var: str = GITHUB_TOKEN_ENV_VAR
    environ: Mapping[str, str] | None = field(default=None, repr=False)

    def get_token(self) -> str:
        source = os.environ if self.environ is None else self.environ
        token = source.get(self.env_var)

        if token is None or token.strip() == "":
            raise MissingGitHubTokenError()

        return token
