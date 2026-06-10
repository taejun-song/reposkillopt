"""Deterministic section-scoped evidence retrieval (feature 011).

Lowers PEAK context: instead of one whole evidence pack feeding all 19 sections, retrieve only
the evidence each section needs — by deterministic structural rule, from the ontology the project
already computes (symbols, schema/FKs, manifests, entrypoints). **No embeddings, no vector DB.**

`retrieve_section_evidence(repo, section, char_budget=...)` is model-free and byte-identical for a
given input. `build_retrieval_report` surfaces the honest peak-vs-total tradeoff. The opt-in
`--section-scoped` generation mode (cli/benchmark) loops the sections over these slices; the
single-pack path stays the default.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from .evidence import (_ENTRYPOINT_HINTS, _MANIFESTS, _list_code_files, _numbered, _run,
                       build_evidence_pack)
from .structure import extract_schema, extract_symbols

# Canonical section -> ordered evidence categories (research D2). Fallback category is "inventory".
SECTION_EVIDENCE: dict[str, tuple[str, ...]] = {
    "Repository overview": ("readme", "manifests"),
    "Technology stack": ("manifests",),
    "Build and runtime commands": ("ci", "manifests"),
    "Major entrypoints": ("entrypoints", "imports"),
    "Architectural layers": ("top_modules",),
    "Core modules": ("top_modules", "symbols"),
    "Domain model": ("symbols",),
    "Data model": ("schema", "er_entities"),
    "External integrations": ("imports", "manifests"),
    "Control-flow traces": ("entrypoints", "top_modules"),
    "Data-flow traces": ("entrypoints", "schema"),
    "Dependency map": ("manifests", "imports"),
    "Configuration map": ("config",),
    "Testing strategy": ("tests",),
    "Deployment assumptions": ("deploy", "ci"),
    "Change-impact map": ("symbols",),
    "Known risks": ("inventory",),
    "Unknowns and unresolved questions": ("inventory",),
    "Evidence index": ("inventory",),
}

_DEFAULT_BUDGET = 8_000


@dataclass
class SectionEvidence:
    section: str
    text: str
    categories: list[str] = field(default_factory=list)
    files: list[str] = field(default_factory=list)
    fell_back: bool = False
    omitted: list[str] = field(default_factory=list)


@dataclass
class RetrievalReport:
    baseline_chars: int
    peak_section_chars: int
    total_chars: int
    fallbacks: list[str] = field(default_factory=list)
    per_section: list[tuple[str, int]] = field(default_factory=list)

    @property
    def peak_reduction(self) -> float:
        return 1.0 - (self.peak_section_chars / self.baseline_chars) if self.baseline_chars else 0.0


# ---- deterministic category resolvers (all return repo-relative paths, sorted) ----

def _tracked(repo: Path) -> list[str]:
    out = _run(repo, "git ls-files 2>/dev/null")
    files = out.splitlines() if out else sorted(
        str(p.relative_to(repo)) for p in repo.rglob("*") if p.is_file())
    return files


def _readme(repo: Path) -> list[str]:
    for r in ("README.md", "README.rst", "README"):
        if (repo / r).exists():
            return [r]
    return []


def _manifests(repo: Path) -> list[str]:
    return sorted(m for m in _MANIFESTS if (repo / m).exists())


def _ci(repo: Path) -> list[str]:
    out = [p for p in ("Makefile", "tox.ini", "noxfile.py", ".gitlab-ci.yml") if (repo / p).exists()]
    wf = repo / ".github" / "workflows"
    if wf.is_dir():
        out += [f".github/workflows/{f.name}" for f in wf.iterdir() if f.suffix in (".yml", ".yaml")]
    return sorted(out)


def _entrypoints(repo: Path) -> list[str]:
    return sorted(f for f in _list_code_files(repo) if Path(f).name in _ENTRYPOINT_HINTS)


def _top_modules(repo: Path, n: int = 6) -> list[str]:
    counts: dict[str, int] = {}
    for s in extract_symbols(str(repo)):
        counts[s.file] = counts.get(s.file, 0) + 1
    ranked = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))   # density desc, path tiebreak
    return [f for f, _ in ranked[:n]]


def _schema_files(repo: Path) -> list[str]:
    return sorted({e.source for e in extract_schema(str(repo)) if e.source})


def _config(repo: Path) -> list[str]:
    out = []
    for f in _tracked(repo):
        nm = Path(f).name.lower()
        if (f.endswith((".env", ".toml", ".ini", ".cfg")) or ".env" in nm
                or nm.startswith(("settings", "config"))
                or (f.endswith((".yaml", ".yml")) and "workflow" not in f.lower())):
            out.append(f)
    return sorted(set(out))[:12]


def _tests(repo: Path) -> list[str]:
    out = [f for f in _tracked(repo)
           if "/test" in f"/{f}".lower() or Path(f).name.startswith("test_")
           or Path(f).name.endswith(("_test.py", "_test.go", ".test.ts", ".spec.ts"))]
    out += [c for c in ("pytest.ini", "tox.ini", "jest.config.js") if (repo / c).exists()]
    return sorted(set(out))[:12]


def _deploy(repo: Path) -> list[str]:
    out = []
    for f in _tracked(repo):
        nm = Path(f).name
        if (nm in ("Dockerfile", "Procfile") or "docker-compose" in nm or nm.endswith(".service")
                or "/deploy" in f"/{f}".lower()
                or (f.endswith((".yaml", ".yml")) and ("k8s" in f.lower() or "deploy" in f.lower()))):
            out.append(f)
    return sorted(set(out))[:12]


_FILE_CATS = {
    "readme": _readme, "manifests": _manifests, "ci": _ci, "entrypoints": _entrypoints,
    "top_modules": _top_modules, "schema": _schema_files, "config": _config,
    "tests": _tests, "deploy": _deploy,
}


# ---- text categories (return a labelled text block) ----

def _symbols_text(repo: Path, budget: int) -> str:
    counts: dict[str, int] = {}
    for s in extract_symbols(str(repo)):
        counts[s.file] = counts.get(s.file, 0) + 1
    lines = [f"{f}: {n} symbols" for f, n in sorted(counts.items())]
    return ("SYMBOLS (deterministic inventory: "
            f"{sum(counts.values())} defs across {len(counts)} files)\n" + "\n".join(lines))[:budget]


def _er_text(repo: Path, budget: int) -> str:
    rows = []
    for e in extract_schema(str(repo)):
        fk = "; ".join(f"{c or '?'}->{t}" for c, t in e.fks)
        rows.append(f"{e.name} ({e.source}){'  FK: ' + fk if fk else ''}")
    return ("DB SCHEMA (deterministic) — draw the erDiagram from THESE tables:\n"
            + "\n".join(rows))[:budget] if rows else ""


def _imports_text(repo: Path, budget: int) -> str:
    grep = _run(repo, "grep -rnE '^(import |from |require\\(|use )' "
                "--include='*.py' --include='*.ts' --include='*.js' --include='*.go' . "
                "2>/dev/null | head -60")
    return ("IMPORTS (top 60):\n" + grep)[:budget] if grep else ""


def _inventory_text(repo: Path, budget: int) -> str:
    sym = _symbols_text(repo, budget)
    er = _er_text(repo, max(0, budget - len(sym) - 2))
    return (sym + ("\n\n" + er if er else ""))[:budget]


_TEXT_CATS = {
    "symbols": _symbols_text, "er_entities": _er_text,
    "imports": _imports_text, "inventory": _inventory_text,
}


def retrieve_section_evidence(repo_path: str, section: str, *,
                              char_budget: int = _DEFAULT_BUDGET) -> SectionEvidence:
    """Deterministic, model-free evidence slice for one section (FR-002/003/004/005)."""
    if section not in SECTION_EVIDENCE:
        raise ValueError(f"unknown section: {section!r}")
    repo = Path(repo_path)
    cats = SECTION_EVIDENCE[section]

    blocks: list[tuple[str, str]] = []   # (label, text) — label is a path for files
    used_cats: list[str] = []
    used_files: list[str] = []
    omitted: list[str] = []
    used = 0

    def _add(label: str, body: str, is_file: bool) -> None:
        nonlocal used
        if not body:
            return
        block = f"=== {'FILE ' if is_file else ''}{label}{' (line-numbered)' if is_file else ''} ===\n{body}"
        if used + len(block) + 2 > char_budget:
            omitted.append(label)
            return
        blocks.append((label, block))
        used += len(block) + 2
        if is_file:
            used_files.append(label)

    for cat in cats:
        if cat in _FILE_CATS:
            paths = _FILE_CATS[cat](repo)
            if paths:
                used_cats.append(cat)
            for p in paths:
                _add(p, _numbered(repo / p, 200), is_file=True)
        else:   # text category
            txt = _TEXT_CATS[cat](repo, char_budget)
            if txt:
                used_cats.append(cat)
                _add(cat, txt, is_file=False)

    if not blocks:   # mapped categories yielded nothing -> shared inventory (FR-005)
        used_cats = ["inventory"]
        _add("inventory", _inventory_text(repo, char_budget), is_file=False)

    # fell_back: the section got only the generic inventory (whether mapped there or it fell back)
    fell_back = used_cats == ["inventory"]
    text = "\n\n".join(b for _, b in blocks)[:char_budget]   # hard cap (FR-004)
    return SectionEvidence(section=section, text=text, categories=used_cats,
                           files=used_files, fell_back=fell_back, omitted=omitted)


def build_retrieval_report(repo_path: str, *,
                           char_budget: int = _DEFAULT_BUDGET) -> RetrievalReport:
    """Honest peak-vs-total instrumentation across all 19 sections (FR-008, model-free)."""
    baseline = len(build_evidence_pack(repo_path).text)
    per: list[tuple[str, int]] = []
    fallbacks: list[str] = []
    total = 0
    for section in SECTION_EVIDENCE:
        se = retrieve_section_evidence(repo_path, section, char_budget=char_budget)
        per.append((section, len(se.text)))
        total += len(se.text)
        if se.fell_back:
            fallbacks.append(section)
    peak = max((n for _, n in per), default=0)
    return RetrievalReport(baseline_chars=baseline, peak_section_chars=peak,
                           total_chars=total, fallbacks=fallbacks, per_section=per)
