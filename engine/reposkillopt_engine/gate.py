"""Executable validation gate: regenerate held-out specs, score them, aggregate, decide.

Implements features 003 (single-scorer no-regression) and 004 (N-scorer majority + HELD)
as runnable code over any LLMProvider.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .judge import generate_spec, score_spec
from .providers.base import LLMProvider
from .rubric import RepoResult, ScoreCard, Verdict, aggregate, verdict_for


@dataclass
class HeldOutRepo:
    name: str
    commit: str
    content: str                          # repo material handed to the provider
    baseline: dict[str, int]              # per-dimension baseline scores (released version)


@dataclass
class GateConfig:
    mode: str = "single"                  # "single" | "majority"
    n: int = 1                            # scorers per repo (odd, >=3 for majority)
    effect_realized: bool = True          # whether the proposal's expected effect was met

    def scorers(self) -> int:
        if self.mode == "majority":
            if self.n < 3 or self.n % 2 == 0:
                raise ValueError("majority mode requires an odd N >= 3")
            return self.n
        return 1


@dataclass
class GateResult:
    verdict: Verdict
    results: list[RepoResult] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return self.verdict is Verdict.PASS


def run_gate(provider: LLMProvider, skill_text: str, repos: list[HeldOutRepo],
             config: GateConfig | None = None) -> GateResult:
    config = config or GateConfig()
    n = config.scorers()
    results: list[RepoResult] = []
    for repo in repos:
        spec = generate_spec(provider, skill_text, repo.name, repo.content)
        cards: list[ScoreCard] = [score_spec(provider, spec, repo.name) for _ in range(n)]
        dims, checks = aggregate(cards, repo.baseline)
        results.append(RepoResult(repo=repo.name, dims=dims, checks=checks))
    verdict = verdict_for(results, effect_realized=config.effect_realized)
    return GateResult(verdict=verdict, results=results)
