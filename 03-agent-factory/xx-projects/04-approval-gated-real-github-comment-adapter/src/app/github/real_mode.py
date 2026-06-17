from dataclasses import dataclass

from app.github.token_provider import GITHUB_TOKEN_ENV_VAR


@dataclass(frozen=True, repr=False)
class GitHubRealModeConfig:
    """Trusted server-side real-mode settings boundary."""

    enabled: bool = False
    allowed_repositories: tuple[str, ...] = ()
    token_env_var: str = GITHUB_TOKEN_ENV_VAR
    client_mode: str = "disabled"

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "allowed_repositories",
            tuple(self.allowed_repositories),
        )

    def repository_is_allowed(self, repository: str) -> bool:
        return repository in self.allowed_repositories

    def __repr__(self) -> str:
        return (
            "GitHubRealModeConfig("
            f"enabled={self.enabled!r}, "
            f"allowed_repositories={self.allowed_repositories!r}, "
            "token_env_var='<server-side-env-var>', "
            f"client_mode={self.client_mode!r}"
            ")"
        )

    __str__ = __repr__
