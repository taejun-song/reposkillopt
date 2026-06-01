"""Rubric dimensions, checks, score aggregation, and the gate verdict.

Mirrors rubric/evaluation-rubric.md (15 dimensions, 0-3) and
rubric/deterministic-checks.md (7 checks), and implements the verdict rules from
features 003 (single-scorer no-regression) and 004 (N-scorer majority + HELD).
"""
from __future__ import annotations

import statistics
from collections import Counter
from dataclasses import dataclass, field
from enum import Enum

# 15 dimensions, in FR-028 order (short keys mirror rubric/evaluation-rubric.md).
DIMENSIONS: tuple[str, ...] = (
    "architectural_correctness", "evidence_quality", "citation_validity",
    "file_symbol_grounding", "hallucination_avoidance", "change_localization",
    "usefulness", "risk_awareness", "fact_hypothesis_distinction",
    "test_strategy_quality", "feedback_responsiveness", "spec_completeness",
    "spec_maintainability", "cross_agent_portability", "failure_mode_resistance",
)

# 7 deterministic checks, mirroring rubric/deterministic-checks.md.
CHECKS: tuple[str, ...] = (
    "cited_paths_exist", "cited_symbols_exist", "sections_present",
    "unsupported_claims_marked", "no_hallucinated_refs",
    "prior_feedback_addressed", "adapter_preserves_intent",
)


class Verdict(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    HELD = "HELD"


@dataclass
class ScoreCard:
    """One scorer's scores for one spec: per-dimension 0-3 and per-check pass/fail."""
    scores: dict[str, int]
    checks: dict[str, bool]

    def validate(self) -> None:
        for d in DIMENSIONS:
            v = self.scores.get(d)
            if not isinstance(v, int) or not 0 <= v <= 3:
                raise ValueError(f"dimension {d!r} must be an int 0-3, got {v!r}")
        for c in CHECKS:
            if not isinstance(self.checks.get(c), bool):
                raise ValueError(f"check {c!r} must be bool")


@dataclass
class DimAggregate:
    dimension: str
    baseline: int
    aggregate: int
    method: str            # "majority" | "median"
    range: int
    low_agreement: bool
    vs_baseline: str       # "above" | "equal" | "below"


def _aggregate_dimension(values: list[int]) -> tuple[int, str, int, bool]:
    """Return (aggregate, method, range, low_agreement) for one dimension across scorers."""
    counts = Counter(values)
    top, top_n = counts.most_common(1)[0]
    # strict majority = a value held by more than half the scorers
    if top_n * 2 > len(values):
        agg, method = top, "majority"
    else:
        agg, method = int(statistics.median(values)), "median"
    rng = max(values) - min(values)
    return agg, method, rng, rng >= 2


def aggregate(cards: list[ScoreCard], baseline: dict[str, int]) -> tuple[list[DimAggregate], dict[str, bool]]:
    """Aggregate N scorers' cards into per-dimension results + aggregated checks."""
    if not cards:
        raise ValueError("no score cards to aggregate")
    dims: list[DimAggregate] = []
    for d in DIMENSIONS:
        vals = [c.scores[d] for c in cards]
        agg, method, rng, low = _aggregate_dimension(vals)
        b = baseline.get(d, agg)
        vs = "above" if agg > b else ("below" if agg < b else "equal")
        dims.append(DimAggregate(d, b, agg, method, rng, low, vs))
    # checks aggregate by majority pass/fail
    checks: dict[str, bool] = {}
    for c in CHECKS:
        passes = sum(1 for card in cards if card.checks[c])
        checks[c] = passes * 2 > len(cards)
    return dims, checks


@dataclass
class RepoResult:
    repo: str
    dims: list[DimAggregate]
    checks: dict[str, bool]
    adjudicated: set[str] = field(default_factory=set)  # dimensions resolved by adjudication


def verdict_for(results: list[RepoResult], effect_realized: bool = True) -> Verdict:
    """Apply the features 003/004 verdict rule across all held-out repos.

    FAIL if any dimension aggregate < baseline, or any check fails.
    HELD if (not FAIL) and some dimension is low-agreement AND at/below baseline AND not adjudicated.
    PASS otherwise (and only if the expected effect is realized or waived).
    """
    held = False
    for r in results:
        if any(not ok for ok in r.checks.values()):
            return Verdict.FAIL
        for d in r.dims:
            if d.aggregate < d.baseline:
                return Verdict.FAIL
            if d.low_agreement and d.vs_baseline in ("equal", "below") and d.dimension not in r.adjudicated:
                held = True
    if held:
        return Verdict.HELD
    if not effect_realized:
        return Verdict.FAIL
    return Verdict.PASS
