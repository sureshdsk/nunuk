class AgentError(Exception):
    """Base exception for all agent errors."""


class ConfigurationError(AgentError):
    """Missing or invalid configuration (env vars, etc.)."""


class MaxRetriesExceeded(AgentError):
    """LLM call retry limit exhausted."""


class IterationCapReached(AgentError):
    """Agent loop iteration limit exceeded."""
