"""OpenAI-compatible chat-completions provider (stdlib urllib; no SDK dependency).

Works with the OpenAI API and any compatible endpoint — including local / open-source
model servers (vLLM, Ollama's OpenAI shim, llama.cpp server, LM Studio, etc.). Point
``base_url`` (or OPENAI_BASE_URL) at the endpoint and set the model.

Env: OPENAI_API_KEY (may be a dummy value for local servers), OPENAI_BASE_URL.
"""
from __future__ import annotations

import json
import os
import urllib.request

from .base import LLMProvider, ProviderError

DEFAULT_BASE_URL = "https://api.openai.com/v1"


class OpenAICompatibleProvider(LLMProvider):
    name = "openai-compatible"

    def __init__(self, *, model: str, base_url: str | None = None,
                 api_key: str | None = None, max_tokens: int = 4096, timeout: float = 120.0):
        self.model = model
        self.base_url = (base_url or os.environ.get("OPENAI_BASE_URL") or DEFAULT_BASE_URL).rstrip("/")
        # Local/OSS servers often ignore the key; default to a placeholder so requests still send.
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY") or "sk-local"
        self.max_tokens = max_tokens
        self.timeout = timeout

    def complete(self, prompt: str, *, system: str | None = None) -> str:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        body = {"model": self.model, "messages": messages, "max_tokens": self.max_tokens}
        req = urllib.request.Request(
            f"{self.base_url}/chat/completions",
            data=json.dumps(body).encode("utf-8"),
            headers={
                "content-type": "application/json",
                "authorization": f"Bearer {self.api_key}",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
        except Exception as exc:  # noqa: BLE001
            raise ProviderError(f"OpenAI-compatible request failed: {exc}") from exc
        try:
            return payload["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise ProviderError(f"Unexpected response: {payload}") from exc
