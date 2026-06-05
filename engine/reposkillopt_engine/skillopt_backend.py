"""Real integration with microsoft/SkillOpt (the `skillopt` PyPI package).

This is an OPTIONAL backend: when installed (`pip install skillopt`), the optimizer can
delegate the two core operations to SkillOpt's own code —

  * **edit application** via ``skillopt.optimizer.apply_edit`` (ops: append / insert_after
    / replace / delete), and
  * the **accept/reject gate decision** via ``skillopt.evaluation.evaluate_gate``
    (returns a ``GateAction`` of accept_new_best / accept / reject).

The native (rubric-based, no-regression / HELD) path in ``optimizer.py`` remains the
default and needs no SkillOpt. This module is what makes "RepoSkillOpt can actually use
SkillOpt" a true statement rather than just an inspiration.
"""
from __future__ import annotations

from .proposal import Proposal
from .rubric import RepoResult

try:  # the dependency is optional — guard the import
    from skillopt.evaluation import evaluate_gate as _evaluate_gate
    from skillopt.optimizer import apply_edit as _apply_edit
    from skillopt.types import Edit as _Edit
    import skillopt as _skillopt
    HAS_SKILLOPT = True
    SKILLOPT_VERSION = getattr(_skillopt, "__version__", "?")
except Exception:  # noqa: BLE001
    HAS_SKILLOPT = False
    SKILLOPT_VERSION = None


def require() -> None:
    if not HAS_SKILLOPT:
        raise RuntimeError(
            "the 'skillopt' backend was requested but the package is not installed; "
            "install it with: pip install 'reposkillopt-engine[skillopt]'  (or: pip install skillopt)"
        )


# Map our six edit kinds onto SkillOpt's four edit ops.
_OP_MAP = {
    "ADD": "insert_after",       # falls back to 'append' when there is no anchor
    "REPLACE": "replace",
    "SPECIALIZE": "replace",
    "GENERALIZE": "replace",
    "REORDER": "replace",
    "DELETE": "delete",
}


def to_skillopt_edit(proposal: Proposal):
    """Convert our Proposal into a real ``skillopt.types.Edit``."""
    require()
    if proposal.edit_kind == "ADD" and not proposal.anchor:
        op = "append"
    else:
        op = _OP_MAP.get(proposal.edit_kind)
    if op is None:
        raise ValueError(f"cannot map edit_kind {proposal.edit_kind!r} to a SkillOpt op")
    return _Edit(op=op, target=proposal.anchor, content=proposal.payload)


def apply_proposal(skill_text: str, proposal: Proposal) -> str:
    """Apply a proposal using SkillOpt's own ``apply_edit``."""
    require()
    return _apply_edit(skill_text, to_skillopt_edit(proposal))


def rubric_score(results: list[RepoResult]) -> float:
    """Project our per-dimension rubric aggregates onto a single [0,1] score for SkillOpt's gate.

    Mean of every per-dimension aggregate across all held-out repos, normalised by 3
    (the rubric max). Higher is better — an edit that raises any dimension raises the score.
    """
    vals = [d.aggregate for r in results for d in r.dims]
    return sum(vals) / (len(vals) * 3.0) if vals else 0.0


def gate_decision(candidate_skill: str, cand_score: float,
                  current_skill: str, current_score: float,
                  best_skill: str, best_score: float, best_step: int,
                  step: int, metric: str = "hard"):
    """Make the accept/reject decision with SkillOpt's real ``evaluate_gate``.

    Returns a ``skillopt.types.GateResult`` whose ``.action`` is one of
    accept_new_best / accept / reject.
    """
    require()
    return _evaluate_gate(
        candidate_skill=candidate_skill, cand_hard=cand_score,
        current_skill=current_skill, current_score=current_score,
        best_skill=best_skill, best_score=best_score, best_step=best_step,
        global_step=step, metric=metric,
    )
