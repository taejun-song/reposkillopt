"""Provider registry + factory."""
from __future__ import annotations

import os

from .base import LLMProvider, ProviderError
from .fake import FakeProvider


def make_provider(spec: str, **kwargs) -> LLMProvider:
    """Build a provider from a short spec string.

    ``fake``                       -> FakeProvider (offline, default)
    ``anthropic`` / ``anthropic:<model>``
    ``openai`` / ``openai:<model>``  (OpenAI or any OpenAI-compatible / OSS endpoint)
    ``claude-cli``                 -> local Claude Code CLI (`claude -p`); no API key needed
    """
    name, _, model = spec.partition(":")
    name = name.strip().lower()
    if name == "fake":
        return FakeProvider(**kwargs)
    if name == "anthropic":
        from .anthropic import AnthropicProvider, DEFAULT_MODEL
        return AnthropicProvider(model=model or DEFAULT_MODEL, **kwargs)
    if name in ("openai", "openai-compatible", "oss"):
        if not model:
            model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
        from .openai_compatible import OpenAICompatibleProvider
        return OpenAICompatibleProvider(model=model, **kwargs)
    if name == "ollama":                 # local open-source models via Ollama's OpenAI shim
        from .openai_compatible import OpenAICompatibleProvider
        kwargs.setdefault("base_url", os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434/v1"))
        return OpenAICompatibleProvider(model=model or "qwen2.5-coder", **kwargs)
    if name in ("claude-cli", "claude_cli", "cli"):
        from .claude_cli import ClaudeCLIProvider
        return ClaudeCLIProvider(**kwargs)
    raise ProviderError(f"unknown provider: {spec!r}")


__all__ = ["LLMProvider", "ProviderError", "FakeProvider", "make_provider"]
