class SkillRegistryError(Exception):
    """Base error for skill registry failures."""


class UnknownSkillError(SkillRegistryError):
    """Raised when a requested skill is not registered."""
