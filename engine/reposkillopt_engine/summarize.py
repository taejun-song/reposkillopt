"""Summarize-then-analyze: a map-reduce evidence pipeline (feature 020).

MAP: deterministically enumerate EVERY source file and write one grounded summary each (the file's
symbols+lines from `structure` are the deterministic, always-present skeleton; the model adds prose).
REDUCE: assemble the complete summary set as the generation evidence and produce the Repository
Specification from it — bounded peak context, complete coverage. Citations are normalized
**repo-relative** so the output grounds by construction (the two pitfalls the demo's gates caught are
fixed here: no file silently skipped; no absolute-path citations). Opt-in; reuses
structure/evidence/grounding/completeness/judge/providers; stdlib only; frozen metrics unchanged.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from .completeness import ensure_symbol_completeness
from .evidence import _list_code_files
from .structure import _read, extract_symbols


@dataclass
class FileSummary:
    file: str                       # repo-relative
    role: str = ""
    key_symbols: list = field(default_factory=list)   # [(name, line)]
    notes: str = ""
    skeleton_only: bool = False


@dataclass
class SummarizeReport:
    files_total: int = 0
    files_summarized: int = 0
    skeleton_fallbacks: int = 0
    peak_chars: int = 0
    total_chars: int = 0
    summaries_dir: str = ""


@dataclass
class FromSummariesEvidence:
    text: str = ""
    included: list = field(default_factory=list)
    omitted: list = field(default_factory=list)
    missing: list = field(default_factory=list)


def enumerate_source_files(repo_path: str) -> list[str]:
    """Deterministic, reproducible source-file set (== evidence._list_code_files), sorted."""
    return sorted(_list_code_files(Path(repo_path)))


def normalize_repo_relative(text: str, repo_path: str) -> str:
    """Strip an absolute repo prefix from any citation so paths are repo-relative. Idempotent."""
    ab = os.path.abspath(repo_path)
    return text.replace(ab + "/", "").replace(ab + os.sep, "").replace(ab, "")


def _skeleton(repo_path: str, rel: str) -> FileSummary:
    syms = [(s.name, s.line) for s in extract_symbols(repo_path) if s.file == rel]
    return FileSummary(file=rel, key_symbols=syms, skeleton_only=True)


def summarize_file(provider, repo_path: str, rel: str, *, char_budget: int = 4000) -> FileSummary:
    """Deterministic skeleton (symbols+lines) + best-effort model prose. Never empty (FR-002/004)."""
    fs = _skeleton(repo_path, rel)
    body = "\n".join(_read(Path(repo_path) / rel)[: char_budget // 40])
    try:
        prose = provider.complete(
            f"In 1-2 sentences, summarize the ROLE of this file and any notable design point. "
            f"Do not restate code. File: {rel}\n\n{body[:char_budget]}",
            system="You are a careful repository-understanding agent.")
        if prose and prose.strip():
            fs.role = normalize_repo_relative(prose.strip(), repo_path)
            fs.skeleton_only = False
    except Exception:  # noqa: BLE001 — model failure must NOT drop the file (coverage guarantee)
        fs.role = "(summary unavailable — deterministic skeleton only)"
    return fs


def render_summary(fs: FileSummary, repo_path: str) -> str:
    lines = [f"# {fs.file}", "", f"**Role:** {fs.role or '(none stated)'}", "", "## Key symbols"]
    if fs.key_symbols:
        lines += [f"- **[fact]** `{n}` `{fs.file}:{ln}`." for n, ln in fs.key_symbols]
    else:
        lines.append("- (no functions/classes defined)")
    if fs.notes:
        lines += ["", f"**Notes:** {fs.notes}"]
    return normalize_repo_relative("\n".join(lines) + "\n", repo_path)


def summarize_repo(provider, repo_path: str, *, char_budget: int = 4000) -> SummarizeReport:
    """Write one summary per enumerated source file (100% coverage, FR-004). Reports peak/total."""
    files = enumerate_source_files(repo_path)
    out_dir = Path(repo_path) / ".reposkillopt" / "summaries"
    rep = SummarizeReport(files_total=len(files), summaries_dir=str(out_dir))
    for rel in files:
        fs = summarize_file(provider, repo_path, rel, char_budget=char_budget)
        md = render_summary(fs, repo_path)
        dest = out_dir / (rel + ".md")
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(md)
        rep.files_summarized += 1
        rep.skeleton_fallbacks += int(fs.skeleton_only)
        rep.peak_chars = max(rep.peak_chars, len(md))
        rep.total_chars += len(md)
    return rep


def assemble_from_summaries(repo_path: str, *, char_budget: int = 80_000) -> FromSummariesEvidence:
    """Reduce input = the complete summary set (bounded). Missing summaries are reported, not silent."""
    out_dir = Path(repo_path) / ".reposkillopt" / "summaries"
    ev = FromSummariesEvidence()
    parts, used = [], 0
    for rel in enumerate_source_files(repo_path):
        p = out_dir / (rel + ".md")
        if not p.is_file():
            ev.missing.append(rel)
            continue
        block = p.read_text()
        if used + len(block) > char_budget:
            ev.omitted.append(rel)
            continue
        parts.append(block)
        ev.included.append(rel)
        used += len(block)
    ev.text = "\n\n".join(parts)
    return ev


def generate_spec_from_summaries(provider, skill_text: str, repo_path: str, *,
                                 char_budget: int = 80_000):
    """Reduce: generate the spec from the summary set, then completeness + repo-relative. Returns (spec, stats)."""
    from .judge import generate_spec
    ev = assemble_from_summaries(repo_path, char_budget=char_budget)
    spec = generate_spec(provider, skill_text, Path(repo_path).name, ev.text)
    spec = normalize_repo_relative(spec, repo_path)
    spec = ensure_symbol_completeness(spec, repo_path)
    stats = {"peak": len(ev.text), "total": len(ev.text),
             "included": len(ev.included), "omitted": ev.omitted, "missing": ev.missing}
    return spec, stats
