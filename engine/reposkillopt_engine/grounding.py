"""Deterministic grounding of a Repository Specification against the real repo (feature 005).

No LLM, no network (SC-006): parse the spec's citations, resolve each against the
repository filesystem, and compute the citation-bearing rubric checks plus concrete
failure strings that steer SkillOpt's reflect (FR-009). The reward folds the
deterministic pass-rate in alongside the rubric (see `skillopt_native._score_skill`).
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from .rubric import CHECKS

# The 19 required Repository Specification sections (mirror SKILL.md / the template).
REQUIRED_SECTIONS: tuple[str, ...] = (
    "Repository overview", "Technology stack", "Build and runtime commands",
    "Major entrypoints", "Architectural layers", "Core modules", "Domain model",
    "Data model", "External integrations", "Control-flow traces", "Data-flow traces",
    "Dependency map", "Configuration map", "Testing strategy", "Deployment assumptions",
    "Change-impact map", "Known risks", "Unknowns and unresolved questions", "Evidence index",
)

# A path with a letter-initial extension (so IPs "127.0.0.1:80" and versions "0.2.0" don't match),
# then ":" and a locator. Trailing comma-line-lists (e.g. db.py:24,38,51) are expanded by the caller.
_CIT_RE = re.compile(
    r"(?P<path>[A-Za-z0-9_][A-Za-z0-9_./\-]*\.[A-Za-z][A-Za-z0-9_]*)"
    r":(?P<loc>\d+(?:-\d+)?(?:,\d+)*|[A-Za-z_][A-Za-z0-9_]*)"
    r"(?::(?P<line2>\d+))?"
)
_FACT_RE = re.compile(r"\*\*\[fact\]\*\*")


@dataclass
class Citation:
    raw: str
    path: str
    kind: str                      # line | range | symbol | symbol_line | malformed
    line: int | None = None
    start: int | None = None
    end: int | None = None
    symbol: str | None = None


@dataclass
class GroundingResult:
    citations: list[Citation] = field(default_factory=list)
    resolved: int = 0
    resolvable_total: int = 0
    rate: float = 1.0
    checks: dict[str, bool] = field(default_factory=dict)
    failures: list[str] = field(default_factory=list)


def parse_citations(spec_text: str) -> list[Citation]:
    """Extract file citations of the forms path:line | path:start-end | path:Symbol[:line]."""
    out: list[Citation] = []
    for m in _CIT_RE.finditer(spec_text):
        path, loc, line2 = m.group("path"), m.group("loc"), m.group("line2")
        raw = m.group(0)
        if re.fullmatch(r"\d+", loc):
            out.append(Citation(raw, path, "line", line=int(loc)))
        elif re.fullmatch(r"\d+-\d+", loc):
            a, b = loc.split("-")
            out.append(Citation(raw, path, "range", start=int(a), end=int(b)))
        elif re.fullmatch(r"\d+(?:,\d+)+", loc):
            for n in loc.split(","):           # expand "24,38,51" into one citation per line
                out.append(Citation(f"{path}:{n}", path, "line", line=int(n)))
        else:                                  # identifier -> symbol (optionally with a line)
            if line2:
                out.append(Citation(raw, path, "symbol_line", symbol=loc, line=int(line2)))
            else:
                out.append(Citation(raw, path, "symbol", symbol=loc))
    return out


def _line_count(path: Path, _cache: dict[str, int]) -> int:
    key = str(path)
    if key not in _cache:
        try:
            with path.open(errors="ignore") as fh:
                _cache[key] = sum(1 for _ in fh)
        except Exception:  # noqa: BLE001
            _cache[key] = -1
    return _cache[key]


def _resolve(repo: Path, c: Citation, lc_cache: dict[str, int],
             txt_cache: dict[str, str]) -> tuple[bool, str]:
    """Return (resolved?, reason-if-not)."""
    fp = repo / c.path
    if not fp.is_file():
        return False, f'file "{c.path}" does not exist'
    n = _line_count(fp, lc_cache)
    if c.kind == "line":
        return (1 <= c.line <= n, "" if 1 <= c.line <= n else f'line {c.line} out of range (file has {n})')
    if c.kind == "range":
        ok = 1 <= c.start <= c.end <= n
        return ok, "" if ok else f'range {c.start}-{c.end} out of range (file has {n})'
    if c.kind in ("symbol", "symbol_line"):
        if str(fp) not in txt_cache:
            try:
                txt_cache[str(fp)] = fp.read_text(errors="ignore")
            except Exception:  # noqa: BLE001
                txt_cache[str(fp)] = ""
        found = bool(re.search(rf"\b{re.escape(c.symbol)}\b", txt_cache[str(fp)]))
        if not found:
            return False, f'symbol "{c.symbol}" not found in {c.path}'
        if c.kind == "symbol_line" and not (1 <= c.line <= n):
            return False, f'line {c.line} out of range (file has {n})'
        return True, ""
    return False, "malformed citation"


def _unmarked_fact(spec_text: str) -> str | None:
    """A `**[fact]**` whose following ~90 chars contain no citation/backtick -> unsupported."""
    for m in _FACT_RE.finditer(spec_text):
        tail = spec_text[m.end():m.end() + 90]
        if "`" in tail or _CIT_RE.search(tail) or "cmd:" in tail:
            continue
        return spec_text[m.end():m.end() + 40].strip().replace("\n", " ")
    return None


def ground_spec(repo_path: str, spec_text: str, *,
                hallucination_threshold: float = 0.9) -> GroundingResult:
    """Resolve a spec's citations against `repo_path` and compute checks + failures."""
    repo = Path(repo_path)
    g = GroundingResult(citations=parse_citations(spec_text))
    lc_cache: dict[str, int] = {}
    txt_cache: dict[str, str] = {}

    considered = [c for c in g.citations if c.kind != "malformed"]  # cmd: never parsed as Citation
    paths_ok = True
    symbols_ok = True
    for c in considered:
        ok, reason = _resolve(repo, c, lc_cache, txt_cache)
        if ok:
            g.resolved += 1
        else:
            g.failures.append(f'cited "{c.raw}" — {reason}')
            if "does not exist" in reason:
                paths_ok = False
            if c.kind in ("symbol", "symbol_line"):
                symbols_ok = False
    g.resolvable_total = len(considered)
    g.rate = (g.resolved / g.resolvable_total) if g.resolvable_total else 1.0

    missing = [s for s in REQUIRED_SECTIONS if s.lower() not in spec_text.lower()]
    for s in missing:
        g.failures.append(f'required section "{s}" missing')

    unmarked = _unmarked_fact(spec_text)
    if unmarked is not None:
        g.failures.append(f'"[fact]" claim without a citation near "{unmarked}…"')

    # The 7 rubric checks: citation-bearing ones are now deterministic; the two that need
    # cross-session/adapter context are not derivable here and default True (recorded in research R4).
    g.checks = {
        "cited_paths_exist": paths_ok,
        "cited_symbols_exist": symbols_ok,
        "sections_present": not missing,
        "unsupported_claims_marked": unmarked is None,
        "no_hallucinated_refs": g.rate >= hallucination_threshold,
        "prior_feedback_addressed": True,
        "adapter_preserves_intent": True,
    }
    assert set(g.checks) == set(CHECKS)  # keep in lockstep with the rubric's 7 checks
    return g
