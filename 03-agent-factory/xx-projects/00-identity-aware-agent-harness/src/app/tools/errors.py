class ToolRegistryError(Exception):
    """Base error for tool registry failures."""


class UnknownToolError(ToolRegistryError):
    """Raised when a requested tool is not registered."""