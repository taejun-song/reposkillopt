"""Commit-time gate + bounded auto-remediation (feature 021).

The engine half of the pre-commit enforcement: classify each staged `.reposkillopt/` artifact, run
exactly the gates that apply to it (coverage / grounding / completeness / check-artifact), and on any
failure run a **bounded, gate-set-monotonic** remediation loop that fixes the artifact and re-stages
it so the commit lands passing. If no keyless provider is reachable, degrade to block-and-report
(run the gates, exit non-zero) — never call a model, never hang.

Determinism: the gate *verdicts* are reproducible (same artifact + repo ⇒ same verdict). The
remediation *edits* are model-driven and therefore nondeterministic; the loop is bounded and never
regresses an already-passing gate. Reuses grounding (frozen)/quality/structure/completeness/
artifact_checks/refine/judge/providers — no new deps. Coverage mirrors `scripts/coverage-gate.sh
--files` (every source file mentioned), computed here in Python so the engine needs no shell script
present in the target repo.
"""
from __future__ import annotations

import os
import re
import shutil
import socket
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

from . import artifact_checks as ac
from .completeness import ensure_symbol_completeness
from .evidence import _list_code_files
from .grounding import ground_spec
from .quality import compute_structure
from .refine import spec_gaps
from .structure import extract_schema, extract_symbols

# ---- gate ids ----
COVERAGE = "coverage"
GROUNDING = "grounding"
COMPLETENESS = "completeness"
CHECK_ARTIFACT = "check_artifact"

# ---- artifact kinds ----
REPO_SPEC = "repo_spec"
ARCHITECTURE = "architecture"
IMPACT = "impact"
ADR = "adr"
LEDGER = "ledger"
OTHER = "other"

_GATES_BY_KIND = {
    REPO_SPEC: [COVERAGE, GROUNDING, COMPLETENESS],
    ARCHITECTURE: [CHECK_ARTIFACT, GROUNDING],
    IMPACT: [CHECK_ARTIFACT, GROUNDING],
    ADR: [CHECK_ARTIFACT],
    LEDGER: [CHECK_ARTIFACT],
    OTHER: [GROUNDING],
}

KEYLESS = {"claude-cli", "claude_cli", "cli", "opencode-cli", "opencode_cli", "ollama"}


# ============================ classification ============================

def classify_artifact(path: str, text: str) -> str:
    """Deterministic kind from path + content (research D1). Pure function — reproducible."""
    name = os.path.basename(path).lower()
    fm = ac._front_matter(text)
    has_dec = re.search(r"^##\s*Decision\b", text, re.M | re.I)
    has_cons = re.search(r"^##\s*Consequences\b", text, re.M | re.I)
    if "adr" in name or (has_dec and has_cons):
        return ADR
    if "ledger" in name or "topological_order" in fm:
        return LEDGER
    if "impact" in name or "blast" in name:
        return IMPACT
    if "architecture" in name or "arch-view" in name or re.search(r"^##\s*Architecture\b", text, re.M | re.I):
        return ARCHITECTURE
    norm = path.replace(os.sep, "/")
    if "/specs/" in norm or "specification" in name or _looks_like_repo_spec(text):
        return REPO_SPEC
    return OTHER


def _looks_like_repo_spec(text: str) -> bool:
    from .grounding import REQUIRED_SECTIONS
    present = sum(1 for s in REQUIRED_SECTIONS if re.search(rf"^#+\s*{re.escape(s)}", text, re.M | re.I))
    return present >= 5


def select_gates(kind: str) -> list:
    return list(_GATES_BY_KIND.get(kind, [GROUNDING]))


# ============================ gate evaluation ============================

@dataclass
class GateVerdict:
    gate: str
    passed: bool
    reasons: list = field(default_factory=list)


@dataclass
class GateReport:
    artifact: str
    kind: str
    verdicts: list = field(default_factory=list)

    @property
    def passing(self) -> frozenset:
        return frozenset(v.gate for v in self.verdicts if v.passed)

    @property
    def all_pass(self) -> bool:
        return all(v.passed for v in self.verdicts)


def _coverage_verdict(repo: str, text: str) -> GateVerdict:
    """Every source file mentioned (mirrors coverage-gate.sh --files). No silent omission."""
    files = sorted(_list_code_files(Path(repo)))
    missing = [f for f in files if f not in text]
    return GateVerdict(COVERAGE, not missing, [f"file not covered: {f}" for f in missing[:20]])


def _grounding_verdict(repo: str, text: str) -> GateVerdict:
    g = ground_spec(repo, text)
    return GateVerdict(GROUNDING, g.rate >= 1.0, list(g.failures))


def _completeness_verdict(repo: str, text: str) -> GateVerdict:
    s = compute_structure(text, extract_symbols(repo), extract_schema(repo))
    ok = s.symbol_coverage >= 1.0
    return GateVerdict(COMPLETENESS, ok,
                       [] if ok else [f"symbol coverage {s.symbol_coverage:.0%} < 100%"])


def _check_artifact_verdict(repo: str, kind: str, text: str) -> GateVerdict:
    if kind == ARCHITECTURE:
        res = ac.check_architecture_view(repo, text)
    elif kind == IMPACT:
        res = ac.check_impact_analysis(repo, text)
    elif kind == ADR:
        res = ac.check_adr(text)
    elif kind == LEDGER:
        res = ac.check_task_ledger(text)
    else:
        res = ac.CheckResult(True, [])
    return GateVerdict(CHECK_ARTIFACT, res.passed, list(res.failures))


def run_gates(repo: str, path: str, text: str, kind: str | None = None) -> GateReport:
    if kind is None:
        kind = classify_artifact(path, text)
    verdicts = []
    for gate in select_gates(kind):
        if gate == COVERAGE:
            verdicts.append(_coverage_verdict(repo, text))
        elif gate == GROUNDING:
            verdicts.append(_grounding_verdict(repo, text))
        elif gate == COMPLETENESS:
            verdicts.append(_completeness_verdict(repo, text))
        elif gate == CHECK_ARTIFACT:
            verdicts.append(_check_artifact_verdict(repo, kind, text))
    return GateReport(artifact=path, kind=kind, verdicts=verdicts)


# ============================ remediation ============================

@dataclass
class RemediationRound:
    round: int
    before: frozenset
    after: frozenset
    gap_count: int
    accepted: bool
    regressed: bool


@dataclass
class RemediationResult:
    artifact: str
    final_text: str
    converged: bool
    rounds: list = field(default_factory=list)
    changed: bool = False


def _revise(provider, skill_text: str, repo: str, repo_name: str, prior: str, gates: list) -> str:
    """One model revise targeting the deterministic gaps; deterministically guarantee completeness."""
    from .judge import revise_spec
    cand = revise_spec(provider, skill_text, repo_name, prior, spec_gaps(repo, prior))
    if COMPLETENESS in gates:
        cand = ensure_symbol_completeness(cand, repo)
    return cand


def remediate(provider, skill_text: str, repo: str, repo_name: str, path: str, text: str,
              *, rounds: int = 3) -> RemediationResult:
    """Bounded, gate-set-monotonic loop. Accept a round iff its passing set ⊇ the carried set and it
    strictly improves (more gates passing, or same gates with fewer residual gaps). Stop at the budget,
    on convergence, or on the first non-improving round (FR-005/FR-006)."""
    kind = classify_artifact(path, text)
    gates = select_gates(kind)
    best_text = text
    best_report = run_gates(repo, path, best_text, kind)
    best_passing = best_report.passing
    best_gaps = len(spec_gaps(repo, best_text))
    history: list[RemediationRound] = []
    for i in range(1, rounds + 1):
        if best_report.all_pass:
            break
        cand = _revise(provider, skill_text, repo, repo_name, best_text, gates)
        cand_report = run_gates(repo, path, cand, kind)
        after = cand_report.passing
        cand_gaps = len(spec_gaps(repo, cand))
        regressed = not (after >= best_passing)
        improved = (after > best_passing) or (after == best_passing and cand_gaps < best_gaps)
        accepted = (not regressed) and improved
        history.append(RemediationRound(i, best_passing, after, cand_gaps, accepted, regressed))
        if accepted:
            best_text, best_report, best_passing, best_gaps = cand, cand_report, after, cand_gaps
        else:
            break   # no improvement (or a regression) — stop early
    return RemediationResult(artifact=path, final_text=best_text, converged=best_report.all_pass,
                             rounds=history, changed=(best_text != text))


# ============================ provider availability ============================

@dataclass
class ProviderAvailability:
    provider: object | None
    id: str | None
    probed: list = field(default_factory=list)


def _ollama_up(timeout: float) -> bool:
    try:
        with socket.create_connection(("127.0.0.1", 11434), timeout=timeout):
            return True
    except OSError:
        return False


def detect_keyless_provider(spec: str = "auto", *, timeout: float = 5.0,
                            _ollama_up=_ollama_up) -> ProviderAvailability:
    """Resolve a usable keyless provider, or None (→ block-and-report). Rejects api-key ids (FR-009)."""
    from .providers import make_provider
    if spec and spec != "auto":
        if spec.startswith("fake"):
            return ProviderAvailability(make_provider(spec), spec, [spec])
        base = spec.split(":", 1)[0]
        if base not in KEYLESS:
            raise ValueError(f"provider {spec!r} is not keyless; the commit hook accepts only "
                             f"{sorted(set(s for s in KEYLESS if '_' not in s))}")
        return ProviderAvailability(make_provider(spec, timeout=timeout), spec, [spec])
    probed = []
    probed.append("claude-cli")
    if shutil.which("claude"):
        return ProviderAvailability(make_provider("claude-cli", timeout=timeout), "claude-cli", probed)
    probed.append("opencode-cli")
    if shutil.which("opencode"):
        return ProviderAvailability(make_provider("opencode-cli", timeout=timeout), "opencode-cli", probed)
    probed.append("ollama")
    model = os.environ.get("REPOSKILLOPT_OLLAMA_MODEL")
    if model and _ollama_up(timeout):
        return ProviderAvailability(make_provider(f"ollama:{model}", timeout=timeout), f"ollama:{model}", probed)
    return ProviderAvailability(None, None, probed)


# ============================ orchestration ============================

@dataclass
class CommitGateOutcome:
    reports: list = field(default_factory=list)
    remediations: list = field(default_factory=list)
    restaged: list = field(default_factory=list)
    exit_code: int = 0
    degraded: bool = False
    probed: list = field(default_factory=list)


def _under_reposkillopt(repo: str, rel: str) -> bool:
    norm = rel.replace(os.sep, "/")
    return ".reposkillopt/" in ("/" + norm)


def _read_staged(repo: str, rel: str) -> str | None:
    """Staged (index) content, falling back to the working-tree file (D5)."""
    proc = subprocess.run(["git", "show", f":{rel}"], cwd=repo, capture_output=True, text=True)
    if proc.returncode == 0:
        return proc.stdout
    p = Path(repo) / rel
    return p.read_text() if p.is_file() else None


def _git_add(repo: str, rel: str) -> None:
    subprocess.run(["git", "add", "--", rel], cwd=repo, check=False)


def gate_commit(repo: str, skill_text: str, staged: list, *, provider=None, rounds: int = 3,
                restage: bool = True, repo_name: str | None = None) -> CommitGateOutcome:
    """Gate each staged `.reposkillopt/` artifact; remediate failures if a provider is available,
    else block-and-report. Re-stage exactly the converged, changed artifacts."""
    repo = os.path.abspath(repo)
    repo_name = repo_name or Path(repo).name
    out = CommitGateOutcome()
    items = []   # (rel, text, report)
    for rel in staged:
        if not _under_reposkillopt(repo, rel):
            continue
        text = _read_staged(repo, rel)
        if text is None:
            continue
        rep = run_gates(repo, rel, text)
        out.reports.append(rep)
        items.append((rel, text, rep))

    failing = [it for it in items if not it[2].all_pass]
    if not failing:
        out.exit_code = 0
        return out

    if provider is None:                         # block-and-report (FR-010): no model, no hang
        out.degraded = True
        out.exit_code = 1
        return out

    all_converged = True
    for rel, text, _rep in failing:
        res = remediate(provider, skill_text, repo, repo_name, rel, text, rounds=rounds)
        out.remediations.append(res)
        if res.converged:
            if res.changed:
                (Path(repo) / rel).write_text(res.final_text)
                if restage:
                    _git_add(repo, rel)
                out.restaged.append(rel)
        else:
            all_converged = False
    out.exit_code = 0 if all_converged else 1
    return out
