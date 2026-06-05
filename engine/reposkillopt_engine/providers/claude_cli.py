"""Provider that shells out to the local Claude Code CLI in print mode (`claude -p`).

Lets the engine make real LLM calls **without an API key** when run inside an environment
that has the `claude` CLI installed and authenticated. Each `complete()` is one headless
`claude -p` invocation. Useful for genuinely exercising the gate/optimizer end-to-end
(regenerate + score) using the local agent as the model.
"""
from __future__ import annotations

import subprocess

from .base import LLMProvider, ProviderError


class ClaudeCLIProvider(LLMProvider):
    name = "claude-cli"

    def __init__(self, *, binary: str = "claude", extra_args: list[str] | None = None,
                 timeout: float = 300.0):
        self.binary = binary
        self.extra_args = extra_args or []
        self.timeout = timeout

    def complete(self, prompt: str, *, system: str | None = None) -> str:
        text = prompt if not system else f"{system}\n\n{prompt}"
        try:
            proc = subprocess.run(
                [self.binary, "-p", *self.extra_args, text],
                capture_output=True, text=True, timeout=self.timeout,
            )
        except FileNotFoundError as exc:
            raise ProviderError(f"claude CLI not found ({self.binary!r})") from exc
        except subprocess.TimeoutExpired as exc:
            raise ProviderError(f"claude CLI timed out after {self.timeout}s") from exc
        if proc.returncode != 0:
            raise ProviderError(f"claude CLI exit {proc.returncode}: {proc.stderr.strip()[:200]}")
        return proc.stdout.strip()
