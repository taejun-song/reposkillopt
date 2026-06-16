"""Normalize chat-model output quirks (feature 013) — deterministic, model-free.

Open-source / chat-tuned models often wrap a Repository Specification in an outer code fence
(```` ```markdown … ``` ````) or pad it with conversational preamble/postamble. This strips those
wrappers WITHOUT touching the spec's own inner fences (e.g. ```` ```mermaid ````), so grounding,
section detection, and completeness see a clean document. Idempotent and a no-op on clean specs.
"""
from __future__ import annotations

import re

# reasoning models (Qwen3-style, DeepSeek-R1, etc.) emit a thinking block before the answer
_THINK = re.compile(r"(?is)<\s*(think|thinking|reason(?:ing)?)\s*>.*?<\s*/\s*\1\s*>\s*")
_FENCE_OPEN = re.compile(r"^(`{3,}|~{3,})\s*(markdown|md)?\s*$")
_FENCE_CLOSE = re.compile(r"^(`{3,}|~{3,})\s*$")
_HEAD = re.compile(r"^(#|---)")
_CITE = re.compile(r"\w+\.\w+:\d")
_CLOSER = re.compile(r"\b(let me know|hope this|feel free|if you (?:have|need|'d)|is there anything|"
                     r"happy to|i can also|would you like|let me|here'?s? (?:the|your)|enjoy)\b", re.I)


def _strip_outer_fence(text: str) -> str:
    lines = text.split("\n")
    i = 0
    while i < len(lines) and not lines[i].strip():
        i += 1
    if i >= len(lines):
        return text
    m = _FENCE_OPEN.match(lines[i].strip())
    if not m:
        return text
    j = len(lines) - 1
    while j >= 0 and not lines[j].strip():
        j -= 1
    if j <= i or not _FENCE_CLOSE.match(lines[j].strip()):
        return text
    inner = lines[i + 1:j]
    if not m.group(2):                       # bare fence — only strip if it really wraps a spec
        k = 0
        while k < len(inner) and not inner[k].strip():
            k += 1
        if k >= len(inner) or not _HEAD.match(inner[k].strip()):
            return text
    return "\n".join(inner)


def _trim_preamble(text: str) -> str:
    lines = text.split("\n")
    for idx, ln in enumerate(lines):
        if _HEAD.match(ln.strip()):
            if idx == 0:
                return text
            dropped = "\n".join(lines[:idx])
            if "[fact]" in dropped or _CITE.search(dropped):   # don't eat real content
                return text
            return "\n".join(lines[idx:])
    return text


def _trim_postamble(text: str) -> str:
    lines = text.split("\n")
    j = len(lines) - 1
    changed = False
    while j >= 0:
        s = lines[j].strip()
        if not s:
            j -= 1
            continue
        if _CLOSER.search(s) and "`" not in s and not s.startswith(("#", "|", "-", "*", ">")):
            j -= 1
            changed = True
            continue
        break
    return "\n".join(lines[:j + 1]) if changed else text


def sanitize_model_spec(text: str) -> str:
    """Strip a reasoning `<think>` block, an outer wrapping fence, and conversational pre/postamble;
    preserve inner fences. Idempotent and a no-op on clean specs."""
    return _trim_postamble(_trim_preamble(_strip_outer_fence(_THINK.sub("", text))))
