"""LLM provider adapters for the threat modeler pipeline."""

__all__ = ["LlmAdapter", "FixtureAdapter", "OpenAiCompatibleAdapter", "XaiAdapter"]


def __getattr__(name: str):
    """Lazy import to avoid circular import issues."""
    if name == "LlmAdapter":
        from .base import LlmAdapter
        return LlmAdapter
    elif name == "FixtureAdapter":
        from .base import FixtureAdapter
        return FixtureAdapter
    elif name == "OpenAiCompatibleAdapter":
        from .openai_compatible_adapter import OpenAiCompatibleAdapter
        return OpenAiCompatibleAdapter
    elif name == "XaiAdapter":
        from .xai_adapter import XaiAdapter
        return XaiAdapter
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
