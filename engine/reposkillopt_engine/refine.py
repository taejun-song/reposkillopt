"""Continuous spec refinement loop (feature 018).

Goal #2, complementary to `optimize-repo` (goal #1 — which optimizes the SKILL by regenerating
the spec from scratch each round). Here we carry the **prior spec forward** and improve that same
document: each round we compute its concrete deterministic gaps (unresolved citations, missing
sections, uncovered symbols, malformed citations), have the model revise the document to fix
exactly those, re-score, and keep the candidate **only if its score strictly improves** (monotonic
— the document never regresses). Scoring and gap-extraction are model-free; the only model call is
the revise step. Chains with `optimize-repo`: feed its tuned skill + output spec in as the start.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .completeness import ensure_symbol_completeness
from .grounding import GroundingResult, ground_spec
from .quality import compute_quality, compute_structure
from .structure import extract_schema, extract_symbols


@dataclass(frozen=True)
class RefineStep:
    round: int
    score: float
    citation_rate: float
    accepted: bool
    n_gaps: int


@dataclass
class RefineResult:
    spec: str
    history: list = field(default_factory=list)
    rounds: int = 0


def spec_gaps(repo_path: str, spec: str) -> list[str]:
    """Concrete, deterministic, model-free gaps to fix in `spec` (drives the revise prompt)."""
    g = ground_spec(repo_path, spec)
    gaps = list(g.failures)
    # NB: symbol COVERAGE is not listed — the completeness step guarantees it deterministically
    # every round, so it is never the model's job. Model-fixable gaps only, below.
    s = compute_structure(spec, extract_symbols(repo_path), extract_schema(repo_path))
    if s.diagram_grounding is not None and s.diagram_grounding < 1.0:
        gaps.append(f"ER-diagram grounding is {s.diagram_grounding:.0%}; some entities are not real tables")
    q = compute_quality(spec, g, repo_path)
    if q.section_completeness < 1.0:
        gaps.append(f"section completeness is {q.section_completeness:.0%}; some required sections are missing or empty")
    if q.malformed_citation_rate > 0:
        gaps.append("some citations are malformed (comma-joined line lists); use one anchor per citation")
    return gaps


def score_spec(repo_path: str, spec: str) -> tuple[float, GroundingResult]:
    """Deterministic score = 0.5·grounding + 0.3·quality + 0.2·symbol-coverage. Reuses frozen metrics."""
    g = ground_spec(repo_path, spec)
    q = compute_quality(spec, g, repo_path)
    s = compute_structure(spec, extract_symbols(repo_path), extract_schema(repo_path))
    return 0.5 * g.rate + 0.3 * q.quality_score + 0.2 * s.symbol_coverage, g


def refine_once(provider, skill_text: str, repo_path: str, repo_name: str, prior_spec: str) -> str:
    """One refinement step: gaps → model revises the PRIOR spec → sanitize → guarantee completeness."""
    from .judge import revise_spec
    revised = revise_spec(provider, skill_text, repo_name, prior_spec, spec_gaps(repo_path, prior_spec))
    return ensure_symbol_completeness(revised, repo_path)


def refine_loop(provider, skill_text: str, repo_path: str, repo_name: str, *,
                initial_spec: str, rounds: int = 3) -> RefineResult:
    """Carry `initial_spec` forward and improve it for up to `rounds`; accept iff score strictly
    improves (monotonic); stop early when there are no gaps left."""
    spec = ensure_symbol_completeness(initial_spec, repo_path)
    best, _ = score_spec(repo_path, spec)
    history: list[RefineStep] = []
    for i in range(1, rounds + 1):
        if not spec_gaps(repo_path, spec):
            break                                            # already clean — nothing to fix
        cand = refine_once(provider, skill_text, repo_path, repo_name, spec)
        sc, g = score_spec(repo_path, cand)
        accepted = sc > best
        history.append(RefineStep(i, sc, g.rate, accepted, len(spec_gaps(repo_path, cand))))
        if accepted:
            spec, best = cand, sc                            # carry the improved document forward
    return RefineResult(spec=spec, history=history, rounds=len(history))
