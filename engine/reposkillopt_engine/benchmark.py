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
              base_dir: str | None = None) -> EntryResult:
    """Score one entry. Never raises — failures become `EntryResult.error`."""
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
        else:
            spec_text = Path(_resolve(entry.spec, base_dir)).read_text()
        g = ground_spec(repo_path, spec_text)
        res.resolved, res.total, res.rate = g.resolved, g.resolvable_total, g.rate
        res.checks = dict(g.checks)
        res.checks_pass = all(g.checks.values())
        res.failures = list(g.failures)
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
                  provider=None, skill_text: str | None = None,
                  scratch_dir: str | None = None, base_dir: str | None = None) -> BenchmarkReport:
    entries = parse_manifest(manifest_text)
    report = BenchmarkReport(mode=mode, date=date)
    own_scratch = scratch_dir is None
    scratch = scratch_dir or tempfile.mkdtemp(prefix="rso-bench-")
    try:
        for e in entries:
            report.entries.append(run_entry(e, scratch, mode=mode, provider=provider,
                                            skill_text=skill_text, base_dir=base_dir))
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
    lines.append("Reproduce:\n")
    lines.append("```sh")
    lines.append(f"python3 -m reposkillopt_engine benchmark --manifest {manifest_path} "
                 f"--mode {report.mode} --date {report.date}")
    lines.append("```\n")
    lines.append("Machine-readable (`name\\tpin\\tresolved\\ttotal\\trate\\tchecks_pass`):\n")
    lines.append("```tsv")
    for r in report.entries:
        if r.error:
            lines.append(f"{r.name}\terror\t0\t0\t0.0\tfalse")
        else:
            lines.append(f"{r.name}\t{r.pin}\t{r.resolved}\t{r.total}\t{r.rate:.4f}\t"
                         f"{'true' if r.checks_pass else 'false'}")
    lines.append("```")
    return "\n".join(lines) + "\n"
