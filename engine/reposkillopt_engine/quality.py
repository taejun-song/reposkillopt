"""Deterministic spec-quality metrics for the benchmark (feature 008).

The grounding benchmark's headline is the citation-resolution rate. But on a repo that's
already fully grounded (e.g. the objectiv TS monorepo: 100% → 100%), an optimized skill can
still improve the spec along *quality* axes the resolution rate can't see — evidence
discipline, completeness, no malformed citations. These metrics surface that, and they are
**model-free and reproducible** (same spec + repo ⇒ identical numbers), reusing feature-005's
citation parsing/resolution. `grounding.py` is left unchanged.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from .grounding import REQUIRED_SECTIONS, GroundingResult, ground_spec
from .grounding import _CIT_RE as _CIT  # reuse the exact citation pattern grounding uses

_FACT_RE = re.compile(r"\*\*\[fact\]\*\*")
# A citation locator containing a comma (comma-disjoint line list, e.g. `core.py:39-40,147`) —
# exactly the malformed form the optimizer learns to remove.
_MALFORMED_RE = re.compile(r"[A-Za-z0-9_][A-Za-z0-9_./\-]*\.[A-Za-z][A-Za-z0-9_]*:\d[\d\-]*,[\d,\-]*")


@dataclass
class QualityMetrics:
    fact_count: int
    citation_density: float | None
    labeled_claim_rate: float
    malformed_citation_rate: float
    section_completeness: float
    trace_presence: float
    quality_score: float


def _section_text(spec_text: str, name: str) -> str | None:
    """Body under `## <name>` up to the next `## ` heading, or None if the section is absent."""
    out: list[str] = []
    capturing = False
    low = name.lower()
    for ln in spec_text.splitlines():
        s = ln.strip()
        if s.startswith("## "):
            if capturing:
                break
            if s[3:].strip().lower().startswith(low):
                capturing = True
            continue
        if capturing:
            out.append(ln)
    return "\n".join(out) if capturing else None


def _non_empty(body: str | None) -> bool:
    if body is None:
        return False
    return any(ln.strip() and not ln.lstrip().startswith("#") for ln in body.splitlines())


def compute_quality(spec_text: str, ground: GroundingResult, repo_path: str) -> QualityMetrics:
    """Deterministic quality metrics from (spec, grounding result, repo). No LLM, no randomness."""
    facts = len(_FACT_RE.findall(spec_text))

    labeled = 0
    for m in _FACT_RE.finditer(spec_text):
        tail = spec_text[m.end():m.end() + 90]
        if "`" in tail or _CIT.search(tail) or "cmd:" in tail:
            labeled += 1
    labeled_rate = (labeled / facts) if facts else 1.0

    citation_density = (ground.resolvable_total / facts) if facts else None

    total_cits = len(ground.citations)
    malformed = len(_MALFORMED_RE.findall(spec_text))
    malformed_rate = min(malformed / total_cits, 1.0) if total_cits else 0.0

    present = sum(1 for s in REQUIRED_SECTIONS if _non_empty(_section_text(spec_text, s)))
    section_completeness = present / len(REQUIRED_SECTIONS)

    trace_presence = 0.0
    for sec in ("Control-flow traces", "Data-flow traces"):
        body = _section_text(spec_text, sec)
        if body and ground_spec(repo_path, body).resolved > 0:
            trace_presence += 0.5

    comps = [labeled_rate, 1.0 - malformed_rate, section_completeness, trace_presence]
    if citation_density is not None:
        comps.append(min(citation_density, 1.0))
    quality_score = sum(comps) / len(comps)

    return QualityMetrics(
        fact_count=facts, citation_density=citation_density, labeled_claim_rate=labeled_rate,
        malformed_citation_rate=malformed_rate, section_completeness=section_completeness,
        trace_presence=trace_presence, quality_score=quality_score)


@dataclass
class StructureMetrics:
    symbol_total: int
    symbol_accounted: int
    symbol_coverage: float
    analyzed_fraction: float
    schema_entities: int
    diagram_entities: int
    diagram_grounding: float | None


def compute_structure(spec_text: str, symbols, schema) -> "StructureMetrics":
    """Deterministic structural coverage: every function/class accounted for + ER grounded.

    `symbols` = list of structure.Symbol; `schema` = list of structure.SchemaEntity.
    No LLM, reproducible. A symbol is "accounted for" if its name appears anywhere in the spec;
    "analyzed" if it appears outside the 'Symbols not yet analyzed' subsection.
    """
    from .structure import parse_er_entities

    total = len(symbols)
    # split the spec into "analyzed" body vs the explicit not-yet-analyzed listing
    not_analyzed = _section_text(spec_text, "Symbols not yet analyzed") or ""
    analyzed_body = spec_text.replace(not_analyzed, "") if not_analyzed else spec_text

    accounted = analyzed = 0
    for sym in symbols:
        tok = re.compile(rf"\b{re.escape(sym.name)}\b")
        named = bool(tok.search(spec_text))
        # accounted = the symbol's name appears anywhere, OR its file is listed under
        # "Symbols not yet analyzed" (per-file accounting is allowed on large repos).
        if named or (not_analyzed and sym.file in not_analyzed):
            accounted += 1
        if named and tok.search(analyzed_body):
            analyzed += 1
    symbol_coverage = (accounted / total) if total else 1.0
    analyzed_fraction = (analyzed / total) if total else 1.0

    schema_names = {e.name.lower() for e in schema}
    er = parse_er_entities(spec_text)
    if not schema_names or not er:
        diagram_grounding = None     # n/a: no DB or no diagram
    else:
        grounded = sum(1 for e in er if e.lower() in schema_names)
        diagram_grounding = grounded / len(er)

    return StructureMetrics(
        symbol_total=total, symbol_accounted=accounted, symbol_coverage=symbol_coverage,
        analyzed_fraction=analyzed_fraction, schema_entities=len(schema),
        diagram_entities=len(er), diagram_grounding=diagram_grounding)
