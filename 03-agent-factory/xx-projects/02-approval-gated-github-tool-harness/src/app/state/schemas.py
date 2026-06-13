from enum import StrEnum


class TaskStatus(StrEnum):
    """Task lifecycle status.

    This is a domain-level task status enum only.
    It is not the final LangGraph runtime state.
    """

    CREATED = "created"
    RUNNING = "running"
    PAUSED_FOR_APPROVAL = "paused_for_approval"
    COMPLETED = "completed"
    FAILED = "failed"
    DENIED = "denied"
    REJECTED = "rejected"