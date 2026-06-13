"""Refactoring opportunities (feature 015) — a derived view over the ontology (012).

Deterministic, model-free detection of repeated STRUCTURE that could be abstracted: function
bodies are normalized to their shape (identifiers→`ID`, numbers→`NUM`, strings→`STR`, keeping
keywords and the type after `except`/`raise`), hashed, and clustered. Low-noise bias — a cluster
is reported only with **≥3 members** and a **≥8-token** body. The rendered section is **advisory and
`[inference]`-only** (never `[fact]`), so it cannot affect any gated metric. Best-effort regex
(feature 009 posture); `rg`-first for the agent path.
"""
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from pathlib import Path

from .structure import _read, extract_symbols

MIN_CLUSTER = 3
MIN_TOKENS = 8

_KW = frozenset(
    "def class return if elif else for while try except finally raise with as import from in is "
    "not and or pass yield await async lambda None True False break continue global nonlocal del "
    "assert match case".split())
_STR = re.compile(r'"[^"\\]*(?:\\.[^"\\]*)*"|\'[^\'\\]*(?:\\.[^\'\\]*)*\'')
_NUM = re.compile(r"\b\d+\.?\d*\b")
_TOK = re.compile(r"\w+|[^\s\w]")


@dataclass(frozen=True)
class Block:
    file: str
    line: int
    normalized: str
    signature: str
    ntokens: int


@dataclass
class Cluster:
    signature: str
    members: list = field(default_factory=list)   # [{"file","line"}]
    ntokens: int = 0
    severity: str = "low"
    suggestion: str = ""


@dataclass
class RefactorReport:
    clusters: list = field(default_factory=list)
    counts: dict = field(default_factory=dict)


def _normalize(body: str) -> str:
    lines = [re.sub(r"#.*$", "", ln) for ln in body.splitlines()]
    text = "\n".join(ln for ln in lines if ln.strip())
    text = _STR.sub(" STR ", text)
    text = _NUM.sub(" NUM ", text)
    toks = _TOK.findall(text)
    out: list[str] = []
    for i, t in enumerate(toks):
        prev = toks[i - 1] if i else ""
        if t in _KW or t in ("STR", "NUM"):
            out.append(t)
        elif re.fullmatch(r"[A-Za-z_]\w*", t):
            out.append(t if prev in ("except", "raise") else "ID")   # keep exception/raise type
        else:
            out.append(t)
    return " ".join(out)


def _func_body(lines: list[str], start: int, *, cap: int = 80) -> str:
    base = len(lines[start]) - len(lines[start].lstrip())
    out = [lines[start]]
    for k in range(start + 1, min(len(lines), start + 1 + cap)):
        ln = lines[k]
        if ln.strip() and (len(ln) - len(ln.lstrip())) <= base:
            break
        out.append(ln)
    return "\n".join(out)


def _blocks(repo: Path) -> list[Block]:
    out: list[Block] = []
    for s in extract_symbols(str(repo)):
        if s.kind != "func":
            continue
        lines = _read(repo / s.file)
        if s.line - 1 >= len(lines):
            continue
        norm = _normalize(_func_body(lines, s.line - 1))
        nt = len(norm.split())
        if nt < MIN_TOKENS:
            continue
        sig = hashlib.sha1(norm.encode("utf-8")).hexdigest()[:16]
        out.append(Block(s.file, s.line, norm, sig, nt))
    return out


def _suggest(norm: str) -> str:
    if "try" in norm and "except" in norm:
        return "extract a shared try/except wrapper (a helper or decorator)"
    if norm.count("if") >= 2:
        return "extract the repeated branching into a shared helper / lookup table"
    return "extract a shared helper for the repeated structure"


def analyze_refactors(repo_path: str) -> RefactorReport:
    """Deterministic clusters of structurally-near-duplicate functions. Model-free."""
    repo = Path(repo_path)
    by_sig: dict[str, list[Block]] = {}
    for b in _blocks(repo):
        by_sig.setdefault(b.signature, []).append(b)
    clusters: list[Cluster] = []
    for sig, members in by_sig.items():
        if len(members) < MIN_CLUSTER:
            continue
        nt = members[0].ntokens
        n = len(members)
        sev = "high" if n >= 10 else "medium" if n >= 5 else "low"
        ms = [{"file": m.file, "line": m.line} for m in sorted(members, key=lambda x: (x.file, x.line))]
        clusters.append(Cluster(sig, ms, nt, sev, _suggest(members[0].normalized)))
    clusters.sort(key=lambda c: ({"high": 0, "medium": 1, "low": 2}[c.severity], -len(c.members), c.signature))
    counts = {"clusters": len(clusters), "instances": sum(len(c.members) for c in clusters)}
    return RefactorReport(clusters=clusters, counts=counts)


def render_refactor_section(rep: RefactorReport, *, per_cluster: int = 8) -> str:
    """## 16a. Refactoring opportunities — advisory, [inference]-only."""
    out = ["## 16a. Refactoring opportunities", ""]
    if not rep.clusters:
        out.append("None known — no structure repeats above the reporting threshold "
                   f"(≥{MIN_CLUSTER} instances, ≥{MIN_TOKENS} tokens).")
        return "\n".join(out) + "\n"
    out.append(f"_{rep.counts['clusters']} repeated structures across "
               f"{rep.counts['instances']} functions (advisory — **[inference]** only)._")
    out.append("")
    for c in rep.clusters:
        cites = ", ".join(f"`{m['file']}:{m['line']}`" for m in c.members[:per_cluster])
        extra = f" (+{len(c.members) - per_cluster} more)" if len(c.members) > per_cluster else ""
        out.append(f"- **[inference]** **{c.severity}** — {len(c.members)} functions share one "
                   f"shape (~{c.ntokens} tokens); {c.suggestion}. Instances: {cites}{extra}.")
    return "\n".join(out) + "\n"
