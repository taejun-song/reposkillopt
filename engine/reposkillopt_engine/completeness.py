"""Deterministic completeness guarantee (feature 010).

Feature 009 instructs the agent to account for every function/class, but a one-shot model
only manages ~10% on a large repo. This step closes that gap deterministically: given a spec +
repo, it appends/updates a "Symbols not yet analyzed" listing of every symbol the spec didn't
already account for — so `symbol_coverage` is guaranteed 100%, model-free and idempotent. It
guarantees *accounting*, not *analysis*: listed symbols don't count toward `analyzed_fraction`.
"""
from __future__ import annotations

import re

from .structure import extract_symbols

_SECTION = "Symbols not yet analyzed"
# matches the section heading (## or ###) through to the next heading of the same/higher level or EOF
_SECTION_RE = re.compile(
    r"(?ms)^\s*#{2,3}\s+Symbols not yet analyzed\b.*?(?=^\s*#{1,3}\s|\Z)")


def _split_existing(spec_text: str) -> tuple[str, str]:
    """Return (body_without_section, existing_section_text|'')."""
    m = _SECTION_RE.search(spec_text)
    if not m:
        return spec_text, ""
    return (spec_text[:m.start()] + spec_text[m.end():]), m.group(0)


def ensure_symbol_completeness(spec_text: str, repo_path: str, *, max_chars: int = 20_000) -> str:
    """Return the spec guaranteed to account for every defined function/class. Idempotent."""
    syms = extract_symbols(repo_path)
    if not syms:
        return spec_text

    body, existing = _split_existing(spec_text)

    # accounted = name appears anywhere in the spec, OR its file is already listed in the section.
    missing_by_file: dict[str, list[str]] = {}
    analyzed = 0
    for s in syms:
        named = re.search(rf"\b{re.escape(s.name)}\b", spec_text) is not None
        listed = bool(existing) and s.file in existing
        if named and re.search(rf"\b{re.escape(s.name)}\b", body):
            analyzed += 1
        if not (named or listed):
            missing_by_file.setdefault(s.file, []).append(s.name)

    if not missing_by_file:
        return spec_text   # already complete — idempotent no-op

    total = len(syms)
    n_listed = sum(len(v) for v in missing_by_file.values())
    lines = [f"\n## {_SECTION}\n",
             "_Generated deterministically — accounting only; see analysis above for depth._\n",
             f"**{total} defined, {analyzed} analyzed, {n_listed} listed.**\n"]
    used = sum(len(x) for x in lines)
    dropped = 0
    for f, names in sorted(missing_by_file.items()):
        full = f"- {f}: {', '.join(sorted(names))}"
        compact = f"- {f}: {len(names)} symbols"
        pick = full if used + len(full) + 1 <= max_chars else (
            compact if used + len(compact) + 1 <= max_chars else None)
        if pick is None:
            dropped += 1
            continue
        lines.append(pick)
        used += len(pick) + 1
    if dropped:
        lines.append(f"- … ({dropped} more files omitted for size; all still accounted-for above)")

    # If we had to drop files for size, fall back to per-file counts for ALL files so 100% holds.
    if dropped:
        lines = [f"\n## {_SECTION}\n",
                 "_Generated deterministically — accounting only._\n",
                 f"**{total} defined, {analyzed} analyzed, {n_listed} listed.**\n"]
        for f, names in sorted(missing_by_file.items()):
            lines.append(f"- {f}: {len(names)} symbols")

    section = "\n".join(lines) + "\n"
    return body.rstrip() + "\n" + section
