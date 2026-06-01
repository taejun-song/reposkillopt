"""Validation-gated convergence optimizer.

The loop, à la SkillOpt's train.py but gated by the rubric instead of a benchmark
reward: propose a bounded edit -> apply -> run the validation gate -> accept (and bump
the version) only if it PASSes -> repeat until convergence, a round budget, or K
consecutive rejects. No weights are touched; the artifact is the skill's Markdown text.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .gate import GateConfig, HeldOutRepo, run_gate
from .judge import propose_edit
from .proposal import Proposal, ProposalError
from .providers.base import LLMProvider
from .rubric import Verdict
from .version import bump


@dataclass
class Round:
    index: int
    edit_kind: str
    verdict: str
    accepted: bool
    version: str
    note: str = ""


@dataclass
class OptimizerConfig:
    max_rounds: int = 10
    patience: int = 2                 # stop after this many consecutive non-accepts
    guidance: str = "Improve evidence grounding and secondary-structure coverage."
    gate: GateConfig = field(default_factory=GateConfig)


@dataclass
class OptimizerResult:
    skill_text: str
    version: str
    history: list[Round] = field(default_factory=list)

    @property
    def accepted_count(self) -> int:
        return sum(1 for r in self.history if r.accepted)


def optimize(provider: LLMProvider, skill_text: str, version: str,
             repos: list[HeldOutRepo], config: OptimizerConfig | None = None) -> OptimizerResult:
    config = config or OptimizerConfig()
    result = OptimizerResult(skill_text=skill_text, version=version)
    misses = 0

    for i in range(1, config.max_rounds + 1):
        proposal = propose_edit(provider, result.skill_text, config.guidance)
        if proposal.is_terminal:
            result.history.append(Round(i, "NONE", "-", False, result.version, "converged: no further edit"))
            break
        if not proposal.eligible():
            misses += 1
            result.history.append(Round(i, proposal.edit_kind, "-", False, result.version,
                                        "skipped: not generic / not eligible"))
            if misses >= config.patience:
                break
            continue

        try:
            candidate = proposal.apply(result.skill_text)
        except ProposalError as exc:
            misses += 1
            result.history.append(Round(i, proposal.edit_kind, "-", False, result.version, f"apply failed: {exc}"))
            if misses >= config.patience:
                break
            continue

        gate = run_gate(provider, candidate, repos, config.gate)
        accepted = gate.verdict is Verdict.PASS
        if accepted:
            result.skill_text = candidate
            result.version = bump(result.version, proposal.bump_level)
            misses = 0
        else:
            misses += 1
        result.history.append(Round(i, proposal.edit_kind, gate.verdict.value, accepted, result.version))
        if not accepted and misses >= config.patience:
            break

    return result
