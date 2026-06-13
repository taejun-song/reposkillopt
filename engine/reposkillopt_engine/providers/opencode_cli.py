"""Provider that shells out to the local OpenCode CLI in non-interactive mode (`opencode run`).

The OpenCode counterpart to `claude_cli` (`claude -p`): lets the engine make real LLM calls
**without an API key of its own** when run in an environment that has `opencode` installed and
authenticated (`opencode auth login`). Each `complete()` is one headless `opencode run`
invocation, using whatever model OpenCode is configured with (including local/open-source models
behind Ollama/LM Studio). Output is ANSI-stripped; the generation path still sanitizes chat
wrappers via `sanitize.sanitize_model_spec`.
"""
from __future__ import annotations

import re
import subprocess

from .base import LLMProvider, ProviderError

_ANSI = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")


class OpenCodeCLIProvider(LLMProvider):
    name = "opencode-cli"

    def __init__(self, *, model: str | None = None, binary: str = "opencode",
                 extra_args: list[str] | None = None, timeout: float = 300.0):
        self.model = model
        self.binary = binary
        self.extra_args = extra_args or []
        self.timeout = timeout

    def complete(self, prompt: str, *, system: str | None = None) -> str:
        text = prompt if not system else f"{system}\n\n{prompt}"
        cmd = [self.binary, "run"]
        if self.model:
            cmd += ["--model", self.model]   # else OpenCode's configured default model
        cmd += [*self.extra_args, text]
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=self.timeout)
        except FileNotFoundError as exc:
            raise ProviderError(f"opencode CLI not found ({self.binary!r})") from exc
        except subprocess.TimeoutExpired as exc:
            raise ProviderError(f"opencode CLI timed out after {self.timeout}s") from exc
        if proc.returncode != 0:
            raise ProviderError(f"opencode CLI exit {proc.returncode}: {proc.stderr.strip()[:200]}")
        return _ANSI.sub("", proc.stdout).strip()
