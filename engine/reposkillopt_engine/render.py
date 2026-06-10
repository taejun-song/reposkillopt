"""Deterministic audience-specific projections of a Repository Specification.

The canonical spec is one evidence-grounded Markdown document — the single source of truth.
These are **pure functions of that text** (no model, no repo access, no drift), so a
human-facing and an agent-facing rendering never diverge from the same spec:

- `to_agent_view`  → lean Markdown: drops visual-only diagrams (`mermaid`) and authoring
  comments that an agent consuming the spec doesn't need, keeping every labeled, cited
  claim and table. Cheaper context for feeding the spec into a coding agent.
- `to_structured`  → JSON: sections, each with its labeled claims and the citations that
  ground them, plus the de-duplicated evidence index — for programmatic upgrade tooling.

Neither invents content; both are derivations. The Markdown spec remains canonical.
"""
from __future__ import annotations

import json
import re

from .grounding import parse_citations

# A fenced ```mermaid … ``` block (visual aid; agents read code directly).
_MERMAID_RE = re.compile(r"(?ms)^[ \t]*```mermaid\b.*?^[ \t]*```[ \t]*\n?")
# An HTML authoring comment (template guidance; not part of the analysis).
_COMMENT_RE = re.compile(r"(?s)<!--.*?-->\n?")
_BLANKS_RE = re.compile(r"\n{3,}")
_LABEL_RE = re.compile(r"\*\*\[(fact|inference|unknown|human)\]\*\*")
_HEAD_RE = re.compile(r"^#{1,3}\s+(.*\S)\s*$")
# leading enumerator / emphasis on a heading ("1. ", "**") — mirrors quality._ENUM_RE
_ENUM_RE = re.compile(r"^\s*(?:\d+\s*[.):\-]\s+)?[*_`\s]*")
_FRONT_RE = re.compile(r"(?s)\A---\n(.*?)\n---\n")


def to_agent_view(spec_text: str) -> str:
    """Lean Markdown for agent consumption: drop mermaid diagrams + authoring comments."""
    t = _MERMAID_RE.sub("", spec_text)
    t = _COMMENT_RE.sub("", t)
    t = _BLANKS_RE.sub("\n\n", t)
    return t.strip() + "\n"


def _norm_heading(h: str) -> str:
    return _ENUM_RE.sub("", h.strip()).strip()


def _front_matter(spec_text: str) -> dict[str, str]:
    m = _FRONT_RE.match(spec_text)
    if not m:
        return {}
    fm: dict[str, str] = {}
    for ln in m.group(1).splitlines():
        if ":" in ln and not ln.lstrip().startswith("#"):
            k, _, v = ln.partition(":")
            fm[k.strip()] = v.strip()
    return fm


def to_structured(spec_text: str) -> dict:
    """Parse the spec into {meta, sections:[{section, claims:[{label,text,citations}]}], evidence_index}.

    Deterministic and model-free: claims are lines carrying an R10 label; citations are the
    grounding parser's `path:line` forms found on that line.
    """
    body = _FRONT_RE.sub("", spec_text, count=1)
    sections: list[dict] = []
    current = {"section": "(preamble)", "claims": []}
    sections.append(current)
    for ln in body.splitlines():
        hm = _HEAD_RE.match(ln.strip())
        if hm and ln.strip().startswith("## "):   # top-level section heading only
            current = {"section": _norm_heading(hm.group(1)), "claims": []}
            sections.append(current)
            continue
        lab = _LABEL_RE.search(ln)
        if lab:
            cites = [c.raw for c in parse_citations(ln)]
            text = _LABEL_RE.sub("", ln).strip(" -\t").strip()
            current["claims"].append({"label": lab.group(1), "text": text, "citations": cites})
    # drop an empty preamble bucket
    sections = [s for s in sections if s["claims"] or s["section"] != "(preamble)"]
    evidence = sorted({c.raw for c in parse_citations(body)})
    return {
        "meta": _front_matter(spec_text),
        "sections": sections,
        "evidence_index": evidence,
        "counts": {
            "sections": sum(1 for s in sections if s["section"] != "(preamble)"),
            "claims": sum(len(s["claims"]) for s in sections),
            "distinct_citations": len(evidence),
        },
    }


def render(spec_text: str, view: str) -> str:
    """Return the requested projection as a string (Markdown for `agent`, JSON for `structured`)."""
    if view == "agent":
        return to_agent_view(spec_text)
    if view == "structured":
        return json.dumps(to_structured(spec_text), indent=2, ensure_ascii=False) + "\n"
    raise ValueError(f"unknown view: {view!r} (expected 'agent' or 'structured')")
