"""Grounding benchmark harness (feature 007).

Measures how *grounded* the skill's Repository Specifications are — the fraction of
their `file:line` / `file:Symbol` citations that resolve against the real repository
files — across a pinned suite of repos, and writes a reproducible report under
`rubric/benchmarks/`.

The scorer is feature-005's `grounding.ground_spec` (model-free, deterministic), so the
benchmark and the optimizer agree by construction. Default mode scores a pre-written spec
(zero model calls); opt-in `generate` mode regenerates the spec via the engine first.
"""
from __future__ import annotations

import os
import statistics
import subprocess
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

from .grounding import ground_spec
from .quality import QualityMetrics, StructureMetrics


@dataclass
class BenchmarkEntry:
    name: str
    repo: str          # local path OR url@commit
    spec: str          # path to the Repository Specification to score (score mode)


@dataclass
class EntryResult:
    name: str
    pin: str = ""
    resolved: int = 0
    total: int = 0
    rate: float = 0.0
    checks: dict[str, bool] = field(default_factory=dict)
    checks_pass: bool = False
    failures: list[str] = field(default_factory=list)
    quality: QualityMetrics | None = None       # feature 008 — deterministic quality block
    structure: StructureMetrics | None = None   # feature 009 — symbol coverage + ER grounding
    rubric_score: float | None = None           # OPTIONAL model-scored aggregate (--rubric only)
    error: str | None = None


@dataclass
class Aggregate:
    n: int = 0
    skipped: int = 0
    mean_rate: float = 0.0
    median_rate: float = 0.0
    checks_pass_share: float = 0.0


@dataclass
class BenchmarkReport:
    mode: str
    date: str
    entries: list[EntryResult] = field(default_factory=list)
    aggregate: Aggregate = field(default_factory=Aggregate)


def parse_manifest(text: str) -> list[BenchmarkEntry]:
    """TAB-separated `name<TAB>repo<TAB>spec`; `#` and blank lines ignored."""
    out: list[BenchmarkEntry] = []
    for i, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = raw.split("\t")
        if len(parts) < 3:
            raise ValueError(f"manifest line {i}: expected name<TAB>repo<TAB>spec, got {raw!r}")
        out.append(BenchmarkEntry(name=parts[0].strip(), repo=parts[1].strip(),
                                  spec=parts[2].strip()))
    return out


def _git(args: list[str], cwd: str) -> None:
    subprocess.run(["git", *args], cwd=cwd, check=True,
                   capture_output=True, text=True, timeout=300)


def ensure_repo(repo: str, scratch_dir: str) -> tuple[str, str]:
    """Return (repo_path, pin). Local path -> as-is; `url@commit` -> pinned shallow clone."""
    if "@" in repo and (repo.startswith("http") or repo.endswith(".git") or "://" in repo):
        url, _, commit = repo.rpartition("@")
        safe = "".join(c if c.isalnum() else "_" for c in url)[-60:]
        dest = os.path.join(scratch_dir, safe)
        if not os.path.isdir(os.path.join(dest, ".git")):
            os.makedirs(dest, exist_ok=True)
            _git(["init", "-q"], dest)
            _git(["fetch", "--depth", "1", url, commit], dest)
            _git(["checkout", "-q", "FETCH_HEAD"], dest)
        return dest, commit
    p = Path(repo)
    if not p.is_dir():
        raise FileNotFoundError(f"repo path does not exist: {repo}")
    try:
        pin = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(p),
                             capture_output=True, text=True, timeout=30).stdout.strip() or "local"
    except Exception:  # noqa: BLE001
        pin = "local"
    return str(p), pin


def _resolve(path: str, base_dir: str | None) -> str:
    """Resolve a relative path against base_dir (repo root); absolute paths pass through."""
    if base_dir and not os.path.isabs(path) and "://" not in path:
        return os.path.join(base_dir, path)
    return path


def run_entry(entry: BenchmarkEntry, scratch_dir: str, *, mode: str = "score",
              provider=None, skill_text: str | None = None,
              base_dir: str | None = None, with_rubric: bool = False) -> EntryResult:
    """Score one entry. Never raises — failures become `EntryResult.error`."""
    from .quality import compute_quality
    res = EntryResult(name=entry.name)
    try:
        repo_path, res.pin = ensure_repo(_resolve(entry.repo, base_dir), scratch_dir)
        if mode == "generate":
            from .evidence import build_evidence_pack
            from .judge import generate_spec
            if provider is None or skill_text is None:
                raise ValueError("generate mode requires provider + skill_text")
            pack = build_evidence_pack(repo_path)
            spec_text = generate_spec(provider, skill_text, entry.name, pack.text)
            from .completeness import ensure_symbol_completeness   # guarantee 100% accounting
            spec_text = ensure_symbol_completeness(spec_text, repo_path)
        else:
            spec_text = Path(_resolve(entry.spec, base_dir)).read_text()
        g = ground_spec(repo_path, spec_text)
        res.resolved, res.total, res.rate = g.resolved, g.resolvable_total, g.rate
        res.checks = dict(g.checks)
        res.checks_pass = all(g.checks.values())
        res.failures = list(g.failures)
        res.quality = compute_quality(spec_text, g, repo_path)   # deterministic, no LLM
        from .quality import compute_structure
        from .structure import extract_schema, extract_symbols
        res.structure = compute_structure(spec_text, extract_symbols(repo_path),
                                          extract_schema(repo_path))   # deterministic, no LLM
        if with_rubric and provider is not None:                 # OPTIONAL model-scored signal
            from .judge import score_spec
            from .rubric import aggregate
            card = score_spec(provider, spec_text, entry.name)
            dims, _ = aggregate([card], {d: 0 for d in card.scores})
            res.rubric_score = sum(d.aggregate for d in dims) / (len(dims) * 3.0)
    except Exception as exc:  # noqa: BLE001 — a bad entry is skipped, never aborts the run
        res.error = str(exc)
    return res


def aggregate(results: list[EntryResult]) -> Aggregate:
    scored = [r for r in results if r.error is None]
    skipped = len(results) - len(scored)
    if not scored:
        return Aggregate(n=0, skipped=skipped)
    rates = [r.rate for r in scored]
    passes = sum(1 for r in scored if r.checks_pass)
    return Aggregate(
        n=len(scored), skipped=skipped,
        mean_rate=statistics.fmean(rates),
        median_rate=statistics.median(rates),
        checks_pass_share=passes / len(scored),
    )


def run_benchmark(manifest_text: str, *, mode: str = "score", date: str,
                  provider=None, skill_text: str | None = None, scratch_dir: str | None = None,
                  base_dir: str | None = None, with_rubric: bool = False) -> BenchmarkReport:
    entries = parse_manifest(manifest_text)
    report = BenchmarkReport(mode=mode, date=date)
    own_scratch = scratch_dir is None
    scratch = scratch_dir or tempfile.mkdtemp(prefix="rso-bench-")
    try:
        for e in entries:
            report.entries.append(run_entry(e, scratch, mode=mode, provider=provider,
                                            skill_text=skill_text, base_dir=base_dir,
                                            with_rubric=with_rubric))
    finally:
        if own_scratch:
            import shutil
            shutil.rmtree(scratch, ignore_errors=True)
    report.aggregate = aggregate(report.entries)
    return report


def render_report(report: BenchmarkReport, *, manifest_path: str) -> str:
    a = report.aggregate
    lines: list[str] = []
    lines.append("---")
    lines.append("kind: grounding-benchmark")
    lines.append(f"mode: {report.mode}")
    lines.append(f"date: {report.date}")
    lines.append(f"entries: {len(report.entries)}")
    lines.append(f"mean_rate: {a.mean_rate:.4f}")
    lines.append(f"median_rate: {a.median_rate:.4f}")
    lines.append(f"checks_pass_share: {a.checks_pass_share:.4f}")
    lines.append(f"skipped: {a.skipped}")
    lines.append("---\n")
    lines.append(f"# Grounding Benchmark — {report.date}\n")
    lines.append("Citation-resolution rate of Repository Specifications against the real "
                 "repository files (feature-005 grounding; model-free, reproducible).\n")
    lines.append("| Repo | Commit pin | Resolved/Total | Rate | All checks | Top issue |")
    lines.append("|------|-----------|----------------|------|-----------|-----------|")
    for r in report.entries:
        if r.error:
            lines.append(f"| {r.name} | — | — | — | — | ERROR: {r.error[:60]} |")
            continue
        top = (r.failures[0][:60] + "…") if r.failures else "—"
        lines.append(f"| {r.name} | `{r.pin[:12]}` | {r.resolved}/{r.total} | "
                     f"{r.rate:.0%} | {'✓' if r.checks_pass else '✗'} | {top} |")
    lines.append("")
    lines.append(f"**Aggregate** — scored {a.n} (skipped {a.skipped}): "
                 f"mean rate **{a.mean_rate:.0%}**, median **{a.median_rate:.0%}**, "
                 f"all-7-checks-pass share **{a.checks_pass_share:.0%}**.\n")

    # Deterministic quality metrics (feature 008) — visible even when the rate is maxed.
    scored = [r for r in report.entries if r.error is None and r.quality is not None]
    if scored:
        lines.append("## Deterministic quality metrics (model-free)\n")
        lines.append("| Repo | Quality | Cit/fact | Labeled | Malformed | Sections | Traces |")
        lines.append("|------|---------|----------|---------|-----------|----------|--------|")
        for r in scored:
            q = r.quality
            dens = "n/a" if q.citation_density is None else f"{q.citation_density:.2f}"
            lines.append(f"| {r.name} | **{q.quality_score:.0%}** | {dens} | "
                         f"{q.labeled_claim_rate:.0%} | {q.malformed_citation_rate:.0%} | "
                         f"{q.section_completeness:.0%} | {q.trace_presence:.0%} |")
        lines.append("")
        lines.append("_quality = mean of [labeled-claim rate, 1−malformed rate, section "
                     "completeness, min(citations/fact, 1), trace presence]; citations/fact "
                     "dropped when a spec has no `[fact]` claims._\n")
        # The 7 deterministic checks, individually.
        check_names = list(scored[0].checks.keys())
        lines.append("## Deterministic checks (per-repo)\n")
        lines.append("| Repo | " + " | ".join(check_names) + " |")
        lines.append("|------|" + "|".join("---" for _ in check_names) + "|")
        for r in scored:
            cells = " | ".join("✓" if r.checks.get(c) else "✗" for c in check_names)
            lines.append(f"| {r.name} | {cells} |")
        lines.append("")
        # Structural coverage (feature 009) — every symbol accounted for + ER grounded.
        if any(r.structure is not None for r in scored):
            lines.append("## Structural coverage (model-free)\n")
            lines.append("| Repo | Symbol coverage | Analyzed | Schema entities | ER grounding |")
            lines.append("|------|-----------------|----------|-----------------|--------------|")
            for r in scored:
                s = r.structure
                if s is None:
                    continue
                erg = "n/a" if s.diagram_grounding is None else f"{s.diagram_grounding:.0%}"
                lines.append(f"| {r.name} | {s.symbol_coverage:.0%} ({s.symbol_accounted}/{s.symbol_total}) "
                             f"| {s.analyzed_fraction:.0%} | {s.schema_entities} | {erg} |")
            lines.append("")
        if any(r.rubric_score is not None for r in scored):
            lines.append("## Model-scored (non-reproducible) — optional context\n")
            lines.append("> These come from the LLM rubric scorer; they are NOT reproducible and "
                         "are shown only for context. The deterministic metrics above are the result.\n")
            for r in scored:
                if r.rubric_score is not None:
                    lines.append(f"- {r.name}: rubric {r.rubric_score:.0%}")
            lines.append("")

    lines.append("Reproduce:\n")
    lines.append("```sh")
    lines.append(f"python3 -m reposkillopt_engine benchmark --manifest {manifest_path} "
                 f"--mode {report.mode} --date {report.date}")
    lines.append("```\n")
    lines.append("Machine-readable (`name\\tpin\\tresolved\\ttotal\\trate\\tchecks_pass"
                 "\\tquality_score\\tcitation_density\\tlabeled_rate\\tmalformed_rate"
                 "\\tsection_completeness\\tsymbol_coverage\\tanalyzed_fraction"
                 "\\tschema_entities\\tdiagram_grounding`):\n")
    lines.append("```tsv")
    for r in report.entries:
        if r.error:
            lines.append(f"{r.name}\terror\t0\t0\t0.0\tfalse\t0.0\tn/a\t0.0\t0.0\t0.0\t0.0\t0.0\t0\tn/a")
        else:
            q, s = r.quality, r.structure
            dens = "n/a" if (q is None or q.citation_density is None) else f"{q.citation_density:.4f}"
            erg = "n/a" if (s is None or s.diagram_grounding is None) else f"{s.diagram_grounding:.4f}"
            lines.append(
                f"{r.name}\t{r.pin}\t{r.resolved}\t{r.total}\t{r.rate:.4f}\t"
                f"{'true' if r.checks_pass else 'false'}\t"
                f"{q.quality_score:.4f}\t{dens}\t{q.labeled_claim_rate:.4f}\t"
                f"{q.malformed_citation_rate:.4f}\t{q.section_completeness:.4f}\t"
                f"{s.symbol_coverage:.4f}\t{s.analyzed_fraction:.4f}\t{s.schema_entities}\t{erg}")
    lines.append("```")
    return "\n".join(lines) + "\n"
