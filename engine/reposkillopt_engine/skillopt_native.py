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

import difflib
import json
import os
import shutil
import tempfile
from dataclasses import dataclass, field

from .evidence import EvidencePack
from .grounding import GroundingResult, ground_spec
from .judge import generate_spec, propose_edit, score_spec
from .providers import make_provider
from .providers.base import LLMProvider
from .rubric import ScoreCard, aggregate
from .version import bump

try:
    import skillopt.model as _M
    from skillopt.evaluation import evaluate_gate as _evaluate_gate
    from skillopt.gradient import run_minibatch_reflect as _reflect
    from skillopt.optimizer import apply_patch as _apply_patch
    HAS_SKILLOPT = True
except Exception:  # noqa: BLE001
    HAS_SKILLOPT = False


def require() -> None:
    if not HAS_SKILLOPT:
        raise RuntimeError("the 'skillopt' package is required; install with: pip install skillopt")


# SkillOpt ships no default analyst prompts (its built-in envs supply their own), so we
# provide them. They instruct SkillOpt's optimizer LLM to emit a patch in the exact shape
# its reflect parser expects: {"patch": {"edits": [{op,target,content}], "reasoning": ...}}.
_ANALYST_PROMPT = """You are the optimizer in a ReflACT loop improving a REPOSITORY-UNDERSTANDING \
skill: a Markdown document that instructs a coding agent how to analyze a code repository and \
produce an evidence-grounded Repository Specification.

You are shown the current skill and one or more trajectories. Each trajectory is a Repository \
Specification the skill produced for a repository, with its rubric score (0..1, higher is better; \
15 quality dimensions + 7 deterministic checks).

Propose at most L bounded edits to the SKILL itself (never to the specification) that would raise \
the score on this and similar repositories - e.g. stronger entrypoint/process modeling, more \
complete control/data-flow tracing, better deployment and risk detection, stricter \
evidence/citation discipline. Keep edits GENERIC (useful across repositories), not specific to one repo.

Output ONLY a JSON object of exactly this shape (no prose around it):
{"patch": {"edits": [{"op": "append|insert_after|replace|delete", "target": "<exact verbatim \
substring copied from the current skill; empty string for append>", "content": "<the new text>"}], \
"reasoning": "<one sentence>"}}

Rules: every `target` except for op=append MUST be an exact, verbatim substring of the current \
skill. Keep each edit small and reviewable. Do not rewrite the whole skill."""


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
    pack: EvidencePack | None = None   # richer cached evidence (feature 005); preferred over digest
    baseline: dict[str, int] = field(default_factory=dict)

    @property
    def repo_path(self) -> str | None:
        return self.pack.repo_path if self.pack else None

    @property
    def material(self) -> str:
        """What spec generation sees: the evidence pack when present, else the digest."""
        return self.pack.text if self.pack else self.digest


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


def _score_skill(provider: LLMProvider, skill_text: str,
                 task: RepoTask) -> tuple[float, str, ScoreCard, GroundingResult | None]:
    """Generate a spec with `skill_text` and score it.

    Returns (reward in [0,1], spec, card, grounding). When the task carries an evidence
    pack (feature 005), the reward combines the rubric quality with the deterministic
    pass-rate of the spec's citations resolved against the real repo:
        reward = 0.5 * rubric_norm + 0.5 * deterministic_pass_rate
    so a spec cannot win by fabricating citations. Without a pack (e.g. fake-provider
    unit path) it falls back to the rubric-only reward.
    """
    spec = generate_spec(provider, skill_text, task.name, task.material)
    card = score_spec(provider, spec, task.name)
    ground: GroundingResult | None = None
    if task.repo_path:
        ground = ground_spec(task.repo_path, spec)
        card.checks = dict(ground.checks)   # the gate sees the real, deterministic checks
    dims, _ = aggregate([card], task.baseline or {d: 0 for d in card.scores})
    rubric_norm = sum(d.aggregate for d in dims) / (len(dims) * 3.0)
    if ground is not None:
        reward = 0.5 * rubric_norm + 0.5 * _deterministic_score(spec, ground, task.repo_path)
    else:
        reward = rubric_norm
    return reward, spec, card, ground


def _deterministic_score(spec: str, ground: GroundingResult, repo_path: str) -> float:
    """The model-free half of the reward — all deterministic, so it cannot be gamed by prose.

    Grounding-dominant, plus the feature-008 quality and feature-009 structural signals:
        0.4·citation-grounding(checks) + 0.3·quality + 0.2·analyzed-coverage + 0.1·ER-grounding
    (the ER term is dropped and the rest renormalized when the repo has no schema/diagram).
    """
    from .quality import compute_quality, compute_structure
    from .structure import extract_schema, extract_symbols
    det_rate = sum(1 for ok in ground.checks.values() if ok) / len(ground.checks)
    q = compute_quality(spec, ground, repo_path)
    s = compute_structure(spec, extract_symbols(repo_path), extract_schema(repo_path))
    parts = [(0.4, det_rate), (0.3, q.quality_score), (0.2, s.analyzed_fraction)]
    if s.diagram_grounding is not None:
        parts.append((0.1, s.diagram_grounding))
    wsum = sum(w for w, _ in parts)
    return sum(w * v for w, v in parts) / wsum


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


def _write_conversation(pred_dir: str, task: RepoTask, skill_text: str, spec: str) -> None:
    """Write the trajectory SkillOpt's analyst reads (<pred_dir>/<id>/conversation.json)."""
    d = os.path.join(pred_dir, str(task.name))
    os.makedirs(d, exist_ok=True)
    conversation = [
        {"role": "system", "content": "Apply the repository-understanding skill and produce "
                                      "an evidence-grounded Repository Specification."},
        {"role": "user", "content": f"Repository: {task.name}\n{task.digest}"},
        {"role": "assistant", "content": spec[:12000]},
    ]
    with open(os.path.join(d, "conversation.json"), "w") as f:
        json.dump(conversation, f)


def _snap_target(skill_text: str, target: str) -> str | None:
    """Snap an LLM-proposed (possibly paraphrased) target to an exact substring of the skill.

    SkillOpt's analyst sometimes returns a near-verbatim anchor; `apply_patch` needs an exact
    match. Return an exact substring, or None if no confident match.
    """
    if not target:
        return ""
    if target in skill_text:
        return target
    first = next((ln for ln in target.strip().splitlines() if ln.strip()), "")
    lines = skill_text.splitlines()
    key = first.strip()[:40]
    if key:
        hits = [ln for ln in lines if key in ln]
        if len(hits) == 1:
            return hits[0]
    close = difflib.get_close_matches(first, lines, n=1, cutoff=0.65)
    return close[0] if close else None


def _snap_patch(skill_text: str, patch: dict) -> dict:
    """Return the inner patch with each edit's target snapped to an exact skill substring.

    Drops edits whose target cannot be confidently resolved (so apply_patch never silently no-ops).
    """
    inner = patch.get("patch", patch) if isinstance(patch, dict) else patch
    edits = (inner or {}).get("edits", []) if isinstance(inner, dict) else []
    out = []
    for e in edits:
        if str(e.get("op")) == "append":
            out.append(e)
            continue
        snapped = _snap_target(skill_text, e.get("target", ""))
        if snapped:
            out.append({**e, "target": snapped})
    return {"edits": out, "reasoning": (inner or {}).get("reasoning", "")}


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
    best_spec: str = ""        # the spec generated by the final skill_text (feature 005 output)
    best_reward: float = 0.0   # combined reward of best_spec
    citation_rate: float = 1.0 # fraction of best_spec citations that resolve against the repo


def optimize_repo(skill_text: str, version: str, task: RepoTask, *,
                  opt_backend: str = "claude-code", provider: str = "claude-cli",
                  rounds: int = 2, edit_budget: int = 3, timeout: float = 600.0) -> NativeResult:
    """Optimize the skill for one repo, with SkillOpt owning edit generation + the gate."""
    require()
    configure_opt_backend(opt_backend)
    # spec generation can be slow on large repos; allow a generous per-call timeout.
    prov = make_provider(provider, **({} if provider.startswith("fake") else {"timeout": timeout}))
    res = NativeResult(skill_text=skill_text, version=version)

    cur_reward, cur_spec, _, cur_ground = _score_skill(prov, res.skill_text, task)
    best_skill, best_score, best_step = res.skill_text, cur_reward, 0

    for i in range(1, rounds + 1):
        spec = cur_spec   # reuse the current skill's spec (avoid a redundant regeneration per round)
        # Frame the trajectory as improvable (binary hard=0) so SkillOpt's error analyst engages.
        result = _rollout_results(cur_reward, spec, task)[0]
        result["hard"] = 0
        result["fail_reason"] = _fail_reason(cur_reward, cur_ground)

        # 1) SkillOpt generates a patch via its ReflACT optimizer LLM; snap anchors so it applies.
        patch, source = None, "skillopt-reflect"
        try:
            with tempfile.TemporaryDirectory() as td:
                pred = os.path.join(td, "pred")
                _write_conversation(pred, task, res.skill_text, spec)   # analyst reads conversation.json
                patches = _reflect(results=[result], skill_content=res.skill_text,
                                   prediction_dir=pred, patches_dir=os.path.join(td, "patches"),
                                   workers=1, failure_only=True,
                                   minibatch_size=1, edit_budget=edit_budget,
                                   error_system=_ANALYST_PROMPT, success_system=_ANALYST_PROMPT)
            raw = next((p for p in (patches or []) if p), None)
            if raw:
                snapped = _snap_patch(res.skill_text, raw)
                patch = snapped if snapped.get("edits") else None
        except Exception:  # noqa: BLE001 - reflect is the riskiest call; degrade gracefully
            patch = None
        if not patch:
            source = "fallback-propose"
            prop = propose_edit(prov, res.skill_text, "Improve evidence grounding and trace coverage.")
            if prop.is_terminal or not prop.eligible():
                res.history.append(NativeRound(i, source, "no-patch", False))
                continue
            anchor = _snap_target(res.skill_text, prop.anchor) or prop.anchor
            patch = {"edits": [{"op": "replace" if prop.edit_kind != "ADD" else "insert_after",
                                "target": anchor, "content": prop.payload}]}

        # 2) SkillOpt applies the patch.
        candidate = _apply_patch(res.skill_text, patch)
        cand_reward, cand_spec, _, cand_ground = _score_skill(prov, candidate, task)

        # 3) SkillOpt's gate decides accept/reject.
        decision = _evaluate_gate(candidate_skill=candidate, cand_hard=cand_reward,
                                  current_skill=res.skill_text, current_score=cur_reward,
                                  best_skill=best_skill, best_score=best_score,
                                  best_step=best_step, global_step=i, metric="hard")
        accepted = decision.action in ("accept", "accept_new_best")
        if accepted:
            res.skill_text = candidate
            res.version = bump(res.version, "minor")
            cur_reward, cur_spec, cur_ground = cand_reward, cand_spec, cand_ground  # carry forward
            res.accepted += 1
            if decision.action == "accept_new_best":
                best_skill, best_score, best_step = candidate, cand_reward, i
        res.history.append(NativeRound(i, source, str(decision.action), accepted))

    # Feature 005 outputs: the spec for the final (best) skill_text + its grounding.
    res.skill_text = _set_version(res.skill_text, res.version)  # front matter matches the bumped version
    res.best_spec = cur_spec
    if task.repo_path:   # feature 010: guarantee 100% symbol accounting in the emitted spec
        from .completeness import ensure_symbol_completeness
        res.best_spec = ensure_symbol_completeness(res.best_spec, task.repo_path)
    res.best_reward = cur_reward
    res.citation_rate = cur_ground.rate if cur_ground else 1.0
    return res


def _set_version(skill_text: str, version: str) -> str:
    """Rewrite the front-matter `version:` line to `version` (no-op if absent)."""
    import re as _re
    return _re.sub(r"(?m)^version:[ \t]*.*$", f"version: {version}", skill_text, count=1)


def _fail_reason(reward: float, ground: GroundingResult | None, *, cap: int = 6) -> str:
    """Build SkillOpt's reflect `fail_reason` from concrete grounding failures (FR-009)."""
    head = f"spec scored {reward:.2f}/1.0."
    if not ground or not ground.failures:
        return (head + " Improve process/scheduler modeling, control/data-flow tracing depth, "
                "and risk detection.")
    seen: list[str] = []
    for f in ground.failures:
        if f not in seen:
            seen.append(f)
        if len(seen) >= cap:
            break
    return (head + f" Citation resolution {ground.rate:.0%}. Fix these grounding gaps: "
            + "; ".join(seen))
