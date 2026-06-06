"""Fully-SkillOpt-driven, backend-selectable per-repo skill optimization.

`skillopt_backend.py` uses SkillOpt for only two steps (apply_edit + evaluate_gate).
**This module hands the whole optimization to SkillOpt** — its own ReflACT edit
generator and patch machinery:

  edit generation : skillopt.gradient.run_minibatch_reflect   (SkillOpt's optimizer LLM)
  patch ranking   : skillopt.optimizer.rank_and_select
  patch apply     : skillopt.optimizer.apply_patch
  accept / reject : skillopt.evaluation.evaluate_gate

RepoSkillOpt supplies only the *reward*: produce a Repository Specification for the
repo (via a provider) and score it with the rubric. If SkillOpt's reflect yields no
usable patch, we fall back to RepoSkillOpt's own `judge.propose_edit` so a run always
makes progress.

**Backend is selectable — keyless OR API key:**
  - SkillOpt edit generator (`opt_backend`):
      "claude-code"  -> claude_code_exec (local `claude` CLI, no API key)
      "openai"/"azure"/"qwen"/"minimax" -> the matching API-key backend (keys from env)
  - Spec generate/score provider (`provider`): any RepoSkillOpt provider
      "claude-cli" (keyless) | "anthropic:<model>" (ANTHROPIC_API_KEY) | "openai:<model>"
"""
from __future__ import annotations

import os
import shutil
import tempfile
from dataclasses import dataclass, field

from .judge import generate_spec, propose_edit, score_spec
from .providers import make_provider
from .providers.base import LLMProvider
from .rubric import ScoreCard, aggregate
from .version import bump

try:
    import skillopt.model as _M
    from skillopt.evaluation import evaluate_gate as _evaluate_gate
    from skillopt.gradient import run_minibatch_reflect as _reflect
    from skillopt.optimizer import apply_patch as _apply_patch, rank_and_select as _rank_and_select
    HAS_SKILLOPT = True
except Exception:  # noqa: BLE001
    HAS_SKILLOPT = False


def require() -> None:
    if not HAS_SKILLOPT:
        raise RuntimeError("the 'skillopt' package is required; install with: pip install skillopt")


# ── backend selection (keyless local CLI or API key) ─────────────────────────
def configure_opt_backend(spec: str = "claude-code", *, claude_path: str | None = None) -> str:
    """Select + configure SkillOpt's optimizer/target backend. Returns the backend name."""
    require()
    name, _, _model = spec.partition(":")
    name = name.strip().lower()
    if name in ("claude-code", "claude_code", "claude-code-exec", "claude", "cli", "claude-cli"):
        # keyless: SkillOpt's claude_chat backend runs the local `claude` CLI (no API key)
        path = claude_path or shutil.which("claude")
        if path:
            os.environ.setdefault("CLAUDE_BIN", path)
        try:
            _M.configure_claude_code_exec(path=path)
        except Exception:  # noqa: BLE001 - exec-mode config is best-effort
            pass
        backend = "claude_chat"
    elif name in ("openai", "azure", "openai_chat"):
        # API key via env (OPENAI_API_KEY / AZURE_OPENAI_* per SkillOpt config)
        try:
            _M.configure_azure_openai()
        except Exception:  # noqa: BLE001
            pass
        backend = "openai_chat"
    elif name in ("qwen", "qwen_chat"):
        _M.configure_qwen_chat(api_key=os.environ.get("QWEN_CHAT_API_KEY"),
                               base_url=os.environ.get("QWEN_CHAT_BASE_URL"))
        backend = "qwen_chat"
    elif name in ("minimax", "minimax_chat"):
        _M.configure_minimax_chat(api_key=os.environ.get("MINIMAX_API_KEY"),
                                  base_url=os.environ.get("MINIMAX_BASE_URL"))
        backend = "minimax_chat"
    else:
        raise ValueError(f"unknown opt_backend: {spec!r} "
                         "(use claude-code | openai | qwen | minimax)")
    _M.set_optimizer_backend(backend)
    _M.set_target_backend(backend)
    return backend


# ── the reward: produce a spec for the repo and score it ─────────────────────
@dataclass
class RepoTask:
    name: str
    digest: str            # repo material handed to the model for spec generation
    baseline: dict[str, int] = field(default_factory=dict)


def build_repo_digest(repo_path: str, *, max_chars: int = 8000) -> str:
    """A generic, language-agnostic digest of a repo for spec generation."""
    import subprocess
    from pathlib import Path
    p = Path(repo_path)

    def run(cmd: str) -> str:
        return subprocess.run(["bash", "-c", f"cd {p!s} && {cmd}"],
                              capture_output=True, text=True).stdout.strip()

    parts = [f"REPOSITORY: {p.name}"]
    for r in ("README.md", "README.rst", "README"):
        if (p / r).exists():
            parts.append("=== README (head) ===\n" +
                         "\n".join((p / r).read_text(errors="ignore").splitlines()[:25]))
            break
    for m in ("pyproject.toml", "package.json", "go.mod", "Cargo.toml", "pom.xml",
              "requirements.txt", "composer.json", "Gemfile"):
        if (p / m).exists():
            parts.append(f"=== {m} ===\n" +
                         "\n".join((p / m).read_text(errors="ignore").splitlines()[:40]))
    parts.append("=== top-level entries ===\n" + run("ls -A | head -40"))
    parts.append("=== source tree (dirs, depth 2) ===\n" +
                 run("find . -maxdepth 2 -type d -not -path '*/.*' "
                     "-not -path '*/node_modules/*' | sort | head -50"))
    parts.append("=== file types ===\n" +
                 run("git ls-files 2>/dev/null | sed 's/.*\\.//' | sort | uniq -c | sort -rn | head -10"))
    return "\n".join(parts)[:max_chars]


def _score_skill(provider: LLMProvider, skill_text: str, task: RepoTask) -> tuple[float, str, ScoreCard]:
    """Generate a spec with `skill_text` and score it. Returns (reward in [0,1], spec, card)."""
    spec = generate_spec(provider, skill_text, task.name, task.digest)
    card = score_spec(provider, spec, task.name)
    dims, checks = aggregate([card], task.baseline or {d: 0 for d in card.scores})
    reward = sum(d.aggregate for d in dims) / (len(dims) * 3.0)
    return reward, spec, card


def _rollout_results(reward: float, spec: str, task: RepoTask) -> list[dict]:
    """Shape a rollout result for SkillOpt's reflect (RolloutResult-compatible)."""
    return [{
        "id": task.name,
        "hard": reward,
        "soft": reward,
        "task_type": "repo_spec",
        "task_description": f"Produce a Repository Specification for {task.name}.",
        "predicted_answer": spec,
        "question": f"Apply the skill to {task.name} and produce its Repository Specification.",
        "reference_text": task.digest[:4000],
        "extras": {},
    }]


# ── the loop: SkillOpt generates/ranks/applies/gates the edits ───────────────
@dataclass
class NativeRound:
    index: int
    source: str            # "skillopt-reflect" | "fallback-propose"
    action: str            # GateAction or "no-patch"
    accepted: bool


@dataclass
class NativeResult:
    skill_text: str
    version: str
    history: list[NativeRound] = field(default_factory=list)
    accepted: int = 0


def optimize_repo(skill_text: str, version: str, task: RepoTask, *,
                  opt_backend: str = "claude-code", provider: str = "claude-cli",
                  rounds: int = 2, edit_budget: int = 3) -> NativeResult:
    """Optimize the skill for one repo, with SkillOpt owning edit generation + the gate."""
    require()
    configure_opt_backend(opt_backend)
    prov = make_provider(provider)
    res = NativeResult(skill_text=skill_text, version=version)

    cur_reward, _, _ = _score_skill(prov, res.skill_text, task)
    best_skill, best_score, best_step = res.skill_text, cur_reward, 0

    for i in range(1, rounds + 1):
        _, spec, _ = _score_skill(prov, res.skill_text, task)
        results = _rollout_results(cur_reward, spec, task)

        # 1) SkillOpt generates a patch (ReflACT reflect); fall back to our proposer.
        patch, source = None, "skillopt-reflect"
        try:
            with tempfile.TemporaryDirectory() as td:
                patches = _reflect(results=results, skill_content=res.skill_text,
                                   prediction_dir=os.path.join(td, "pred"),
                                   patches_dir=os.path.join(td, "patches"),
                                   workers=1, failure_only=False,
                                   minibatch_size=1, edit_budget=edit_budget)
            patch = next((p for p in (patches or []) if p), None)
            if patch:
                ranked = _rank_and_select(res.skill_text, patch, max_edits=edit_budget)
                patch = ranked or patch
        except Exception:  # noqa: BLE001 - reflect is the riskiest call; degrade gracefully
            patch = None
        if not patch:
            source = "fallback-propose"
            prop = propose_edit(prov, res.skill_text, "Improve evidence grounding and trace coverage.")
            if prop.is_terminal or not prop.eligible():
                res.history.append(NativeRound(i, source, "no-patch", False))
                continue
            patch = {"edits": [{"op": "replace" if prop.edit_kind != "ADD" else "insert_after",
                                "target": prop.anchor, "content": prop.payload}]}

        # 2) SkillOpt applies the patch.
        candidate = _apply_patch(res.skill_text, patch)
        cand_reward, _, _ = _score_skill(prov, candidate, task)

        # 3) SkillOpt's gate decides accept/reject.
        decision = _evaluate_gate(candidate_skill=candidate, cand_hard=cand_reward,
                                  current_skill=res.skill_text, current_score=cur_reward,
                                  best_skill=best_skill, best_score=best_score,
                                  best_step=best_step, global_step=i, metric="hard")
        accepted = decision.action in ("accept", "accept_new_best")
        if accepted:
            res.skill_text = candidate
            res.version = bump(res.version, "minor")
            cur_reward = cand_reward
            res.accepted += 1
            if decision.action == "accept_new_best":
                best_skill, best_score, best_step = candidate, cand_reward, i
        res.history.append(NativeRound(i, source, str(decision.action), accepted))

    return res
