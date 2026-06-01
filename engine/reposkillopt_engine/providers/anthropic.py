"""Anthropic Messages API provider (stdlib urllib; no SDK dependency).

Reads ANTHROPIC_API_KEY from the environment. Model defaults to a current Claude
model and can be overridden. Network is only touched when this provider is used —
the engine ships with the FakeProvider as the dependency-free default.
"""
from __future__ import annotations

import json
import os
import urllib.request

from .base import LLMProvider, ProviderError

DEFAULT_MODEL = "claude-sonnet-4-6"
API_URL = "https://api.anthropic.com/v1/messages"


class AnthropicProvider(LLMProvider):
    name = "anthropic"

    def __init__(self, *, model: str = DEFAULT_MODEL, api_key: str | None = None,
                 max_tokens: int = 4096, timeout: float = 120.0):
        self.model = model
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        self.max_tokens = max_tokens
        self.timeout = timeout
        if not self.api_key:
            raise ProviderError("ANTHROPIC_API_KEY not set")

    def complete(self, prompt: str, *, system: str | None = None) -> str:
        body = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "messages": [{"role": "user", "content": prompt}],
        }
        if system:
            body["system"] = system
        req = urllib.request.Request(
            API_URL,
            data=json.dumps(body).encode("utf-8"),
            headers={
                "content-type": "application/json",
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
        except Exception as exc:  # noqa: BLE001 - surface any transport/parse error uniformly
            raise ProviderError(f"Anthropic request failed: {exc}") from exc
        try:
            return "".join(b.get("text", "") for b in payload["content"])
        except (KeyError, TypeError) as exc:
            raise ProviderError(f"Unexpected Anthropic response: {payload}") from exc
