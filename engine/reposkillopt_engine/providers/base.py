"""LLM provider abstraction.

The engine is provider-agnostic: it builds prompts and parses responses, while a
provider only needs to turn a prompt into text. Concrete providers live alongside
this module (fake, anthropic, openai_compatible). Open-source models are reachable
through the OpenAI-compatible provider (point base_url at a local/OSS endpoint).
"""
from __future__ import annotations

import abc


class LLMProvider(abc.ABC):
    """Minimal interface: turn a prompt (+ optional system) into text."""

    name: str = "base"

    @abc.abstractmethod
    def complete(self, prompt: str, *, system: str | None = None) -> str:
        """Return the model's text completion for ``prompt``."""
        raise NotImplementedError


class ProviderError(RuntimeError):
    """Raised when a provider cannot produce a usable response."""
