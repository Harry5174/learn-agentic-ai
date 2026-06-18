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

    def has_valid_exact_repository_allowlist(self) -> bool:
        return bool(self.allowed_repositories) and all(
            _is_exact_repository_name(repository)
            for repository in self.allowed_repositories
        )

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


def _is_exact_repository_name(repository: str) -> bool:
    parts = repository.split("/")
    return (
        len(parts) == 2
        and all(part.strip() == part and part for part in parts)
        and "*" not in repository
    )
