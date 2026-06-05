"""Validation-gated convergence optimizer.

The loop, à la SkillOpt's train.py but gated by the rubric instead of a benchmark
reward: propose a bounded edit -> apply -> run the validation gate -> accept (and bump
the version) only if it PASSes -> repeat until convergence, a round budget, or K
consecutive rejects. No weights are touched; the artifact is the skill's Markdown text.

Two backends:
  * ``backend="native"`` (default) — edits applied by ``Proposal.apply`` and accepted on
    the rubric's no-regression PASS verdict (features 003/004; no extra dependency).
  * ``backend="skillopt"`` — edits applied by **SkillOpt's** ``apply_edit`` and accepted by
    **SkillOpt's** ``evaluate_gate`` over a rubric-derived score. Requires the optional
    ``skillopt`` package (see ``skillopt_backend``).
"""
from __future__ import annotations

from dataclasses import dataclass, field

from . import skillopt_backend as so
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
    backend: str = "native"           # "native" (rubric no-regression) | "skillopt" (SkillOpt's gate)


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
    use_skillopt = config.backend == "skillopt"
    if use_skillopt:
        so.require()
    result = OptimizerResult(skill_text=skill_text, version=version)
    misses = 0

    # SkillOpt's gate compares scalar scores; seed current/best from the starting skill.
    cur_score = best_score = best_step = 0
    best_skill = skill_text
    if use_skillopt:
        cur_score = best_score = so.rubric_score(run_gate(provider, skill_text, repos, config.gate).results)

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
            candidate = (so.apply_proposal(result.skill_text, proposal) if use_skillopt
                         else proposal.apply(result.skill_text))
        except (ProposalError, Exception) as exc:  # noqa: BLE001 - record any apply error and continue
            if isinstance(exc, ProposalError) or use_skillopt:
                misses += 1
                result.history.append(Round(i, proposal.edit_kind, "-", False, result.version, f"apply failed: {exc}"))
                if misses >= config.patience:
                    break
                continue
            raise

        gate = run_gate(provider, candidate, repos, config.gate)

        if use_skillopt:
            cand_score = so.rubric_score(gate.results)
            decision = so.gate_decision(candidate, cand_score, result.skill_text, cur_score,
                                        best_skill, best_score, best_step, i)
            label = str(decision.action)
            accepted = decision.action in ("accept", "accept_new_best")
            if accepted:
                result.skill_text = candidate
                result.version = bump(result.version, proposal.bump_level)
                cur_score = cand_score
                if decision.action == "accept_new_best":
                    best_skill, best_score, best_step = candidate, cand_score, i
                misses = 0
            else:
                misses += 1
        else:
            label = gate.verdict.value
            accepted = gate.verdict is Verdict.PASS
            if accepted:
                result.skill_text = candidate
                result.version = bump(result.version, proposal.bump_level)
                misses = 0
            else:
                misses += 1

        result.history.append(Round(i, proposal.edit_kind, label, accepted, result.version))
        if not accepted and misses >= config.patience:
            break

    return result
