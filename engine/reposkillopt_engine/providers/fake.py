"""Deterministic, offline provider for tests and dry runs.

Routes by markers the engine puts in its prompts (REGENERATE_SPEC / SCORE_SPEC /
PROPOSE_EDIT) and returns scripted responses from per-phase queues. No network,
fully reproducible — this is what makes the gate and optimizer logic testable
without any real model or API key.
"""
from __future__ import annotations

import json
from collections import deque
from typing import Iterable

from .base import LLMProvider, ProviderError


class FakeProvider(LLMProvider):
    name = "fake"

    def __init__(
        self,
        *,
        spec_text: str = "# regenerated spec (fake)\n",
        scores: Iterable[dict] | None = None,
        proposals: Iterable[dict] | None = None,
    ):
        # spec_text: returned for every REGENERATE_SPEC call.
        self.spec_text = spec_text
        # scores: queue of {"scores": {dim:int}, "checks": {check:"pass"|"fail"}} dicts,
        #         popped once per SCORE_SPEC call (one per scorer).
        self._scores = deque(scores or [])
        # proposals: queue of proposal dicts popped per PROPOSE_EDIT call.
        self._proposals = deque(proposals or [])
        self.calls: list[str] = []

    def complete(self, prompt: str, *, system: str | None = None) -> str:
        if "REGENERATE_SPEC" in prompt:
            self.calls.append("regenerate")
            return self.spec_text
        if "SCORE_SPEC" in prompt:
            self.calls.append("score")
            if not self._scores:
                raise ProviderError("FakeProvider: no scripted scores left")
            return json.dumps(self._scores.popleft())
        if "PROPOSE_EDIT" in prompt:
            self.calls.append("propose")
            if not self._proposals:
                # signal "no further proposal" — engine treats this as convergence
                return json.dumps({"edit_kind": "NONE"})
            return json.dumps(self._proposals.popleft())
        raise ProviderError("FakeProvider: unrecognized prompt phase")
