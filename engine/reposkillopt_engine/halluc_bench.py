"""Mutation benchmark for the hallucination catcher (feature 022).

The meta-loop: take a known-clean grounded spec, inject one hallucination of each class at a known
site, and measure the catcher's per-class RECALL (fraction of injections flagged) and overall
PRECISION (is the clean spec flagged?). Deterministic — fixed clean spec ⇒ fixed mutants ⇒ fixed
numbers; the only nondeterminism is an optional model whose output is the *subject* of a run, never
the ground truth. Reuses the 007/008 report conventions (Markdown + YAML under rubric/benchmarks/).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from .hallucination import (CLAIM_CODE_MISMATCH, FABRICATED_SYMBOL, UNLABELED_CLAIM,
                            UNSUPPORTED_QUANTITY, detect_hallucinations)
from .structure import _read, extract_symbols


@dataclass
class Mutation:
    cls: str            # mutator name
    expect: str         # CheckKind the catcher should produce
    site: int           # 1-based line of the injection in `after`
    after: str          # mutated spec


@dataclass
class CalibrationReport:
    model: str = "fixtures"
    window: int = 3
    spec_path: str = ""
    per_class: dict = field(default_factory=dict)   # kind -> (injected, flagged)
    precision: float = 1.0

    def render(self) -> str:
        fm = (f"---\nkind: hallucination-calibration\nmodel: {self.model}\n"
              f"window: {self.window}\ngenerated_from: {self.spec_path}\n---\n")
        rows = ["| class | injected | flagged | recall |", "|---|---|---|---|"]
        for cls in (CLAIM_CODE_MISMATCH, FABRICATED_SYMBOL, UNLABELED_CLAIM, UNSUPPORTED_QUANTITY):
            inj, fl = self.per_class.get(cls, (0, 0))
            r = (fl / inj) if inj else 1.0
            rows.append(f"| {cls} | {inj} | {fl} | {r:.2f} |")
        return (fm + "# Hallucination catcher — calibration\n\n" + "\n".join(rows)
                + f"\n\noverall precision (clean spec not flagged): {self.precision:.1f}\n")


def _pick_wrong_line(lines: list[str], token: str, sym_line: int, window: int) -> int | None:
    """A valid 1-based line whose ±window does NOT contain `token` and is far from sym_line."""
    n = len(lines)
    for cand in range(n, 0, -1):
        if abs(cand - sym_line) <= window:
            continue
        lo, hi = max(0, cand - 1 - window), min(n, cand + window)
        if token not in "\n".join(lines[lo:hi]):
            return cand
    return None


def build_mutations(repo_path: str, clean_spec: str) -> list[Mutation]:
    """One injected hallucination per class, appended to the clean spec (site = last line)."""
    syms = [s for s in extract_symbols(repo_path)]
    muts: list[Mutation] = []
    for s in syms:
        lines = _read(Path(repo_path) / s.file)
        if not lines:
            continue
        base = clean_spec.rstrip("\n")

        def _mk(extra: str):
            after = base + "\n" + extra + "\n"
            return after, len(after.splitlines())

        # 1) mis-cited real symbol -> claim_code_mismatch
        wrong = _pick_wrong_line(lines, s.name, s.line, 3)
        if wrong is not None:
            after, site = _mk(f"**[fact]** the `{s.name}` symbol `{s.file}:{wrong}`")
            muts.append(Mutation("flip_citation_line", CLAIM_CODE_MISMATCH, site, after))
        # 2) renamed cited symbol (nonexistent) -> fabricated_symbol
        after, site = _mk(f"**[fact]** uses `{s.name}Xz` `{s.file}:{s.line}`")
        muts.append(Mutation("rename_cited_symbol", FABRICATED_SYMBOL, site, after))
        # 3) invented API -> fabricated_symbol
        after, site = _mk(f"**[fact]** calls `{s.name}_invented_api` `{s.file}:{s.line}`")
        muts.append(Mutation("invent_api", FABRICATED_SYMBOL, site, after))
        # 4) stripped label -> unlabeled_claim
        after, site = _mk(f"The `{s.name}` symbol builds the app and returns a value here.")
        muts.append(Mutation("strip_label", UNLABELED_CLAIM, site, after))
        # 5) fabricated quantity -> unsupported_quantity
        after, site = _mk(f"**[fact]** exposes 999999 handlers `{s.file}:{s.line}`")
        muts.append(Mutation("alter_quantity", UNSUPPORTED_QUANTITY, site, after))
        break   # one symbol is enough for a deterministic per-class measurement
    return muts


def run_mutation_benchmark(repo_path: str, clean_spec: str, *, window: int = 3,
                           model: str = "fixtures", spec_path: str = "") -> CalibrationReport:
    per: dict[str, list[int]] = {k: [0, 0] for k in
                                 (CLAIM_CODE_MISMATCH, FABRICATED_SYMBOL, UNLABELED_CLAIM, UNSUPPORTED_QUANTITY)}
    for m in build_mutations(repo_path, clean_spec):
        per[m.expect][0] += 1
        fs = detect_hallucinations(repo_path, "specs/repository-specification.md", m.after, window=window)
        if any(f.kind == m.expect and abs(f.line - m.site) <= 1 for f in fs):
            per[m.expect][1] += 1
    clean_findings = detect_hallucinations(repo_path, "specs/repository-specification.md",
                                           clean_spec, window=window)
    precision = 1.0 if not clean_findings else 0.0
    return CalibrationReport(model=model, window=window, spec_path=spec_path,
                             per_class={k: (v[0], v[1]) for k, v in per.items()}, precision=precision)
