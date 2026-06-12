from typing import Protocol

from app.identity.schemas import IdentityContext
from app.skills.schemas import SkillProposal


class SkillProposer(Protocol):
    """Minimal interface for a source that proposes skill plans."""

    def propose(self, task: str, identity: IdentityContext) -> SkillProposal:
        """Return an untrusted skill proposal for the harness to validate."""
