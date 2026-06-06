"""Command-line entry point: `python -m reposkillopt_engine <gate|optimize> ...`.

Loads a run config from a JSON file (skill text path, held-out repos + baselines,
provider, mode). Uses the offline FakeProvider by default; pass --provider anthropic:<model>
or --provider openai:<model> (with the relevant env vars) for real LLM scoring.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .gate import GateConfig, HeldOutRepo, run_gate
from .optimizer import OptimizerConfig, optimize
from .providers import make_provider


def _load_repos(cfg: dict) -> list[HeldOutRepo]:
    repos = []
    for r in cfg["held_out"]:
        repos.append(HeldOutRepo(
            name=r["name"], commit=r.get("commit", ""),
            content=r.get("content", ""), baseline=r["baseline"],
        ))
    return repos


def _provider(args, cfg: dict):
    kwargs = {}
    if args.provider.startswith("fake"):
        kwargs = cfg.get("fake", {})
    return make_provider(args.provider, **kwargs)


def cmd_gate(args) -> int:
    cfg = json.loads(Path(args.config).read_text())
    skill = Path(cfg["skill_path"]).read_text() if "skill_path" in cfg else cfg.get("skill_text", "")
    repos = _load_repos(cfg)
    gate_cfg = GateConfig(**cfg.get("gate", {}))
    result = run_gate(_provider(args, cfg), skill, repos, gate_cfg)
    print(result.verdict.value)
    if args.verbose:
        for r in result.results:
            regressed = [d.dimension for d in r.dims if d.aggregate < d.baseline]
            held = [d.dimension for d in r.dims if d.low_agreement and d.vs_baseline in ("equal", "below")]
            print(f"  {r.repo}: regressed={regressed or '-'} contested={held or '-'}", file=sys.stderr)
    return 0 if result.passed else 1


def cmd_optimize(args) -> int:
    cfg = json.loads(Path(args.config).read_text())
    skill = Path(cfg["skill_path"]).read_text() if "skill_path" in cfg else cfg.get("skill_text", "")
    repos = _load_repos(cfg)
    opt_cfg = OptimizerConfig(
        max_rounds=cfg.get("max_rounds", 10),
        patience=cfg.get("patience", 2),
        guidance=cfg.get("guidance", OptimizerConfig.guidance),
        gate=GateConfig(**cfg.get("gate", {})),
        backend=getattr(args, "backend", None) or cfg.get("backend", "native"),
    )
    res = optimize(_provider(args, cfg), skill, cfg.get("version", "0.1.0"), repos, opt_cfg)
    print(f"final version {res.version}; {res.accepted_count} accepted of {len(res.history)} rounds")
    for r in res.history:
        mark = "ACCEPT" if r.accepted else "reject"
        print(f"  round {r.index}: {r.edit_kind:10} {r.verdict:5} {mark} -> {r.version} {r.note}", file=sys.stderr)
    if args.out:
        Path(args.out).write_text(res.skill_text)
    return 0


def cmd_optimize_repo(args) -> int:
    from .skillopt_native import HAS_SKILLOPT, RepoTask, build_repo_digest, optimize_repo
    if not HAS_SKILLOPT:
        print("error: the 'skillopt' package is required (pip install skillopt)", file=sys.stderr)
        return 1
    repo = Path(args.repo)
    if not repo.is_dir():
        print(f"error: not a directory: {repo}", file=sys.stderr)
        return 2
    skill = Path(args.skill).read_text()
    task = RepoTask(name=repo.name, digest=build_repo_digest(str(repo)))
    print(f"optimizing skill for {repo.name} — SkillOpt opt-backend={args.opt_backend}, "
          f"rollout={args.rollout_provider}, rounds={args.rounds}", file=sys.stderr)
    res = optimize_repo(skill, args.version, task,
                        opt_backend=args.opt_backend, provider=args.rollout_provider,
                        rounds=args.rounds)
    out = Path(args.out) if args.out else (repo / ".reposkillopt" / "best_skill.md")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(res.skill_text)
    print(f"final version {res.version}; {res.accepted} accepted of {len(res.history)} rounds; wrote {out}")
    for rd in res.history:
        print(f"  round {rd.index}: [{rd.source}] {rd.action} "
              f"({'ACCEPT' if rd.accepted else 'reject'})", file=sys.stderr)
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="reposkillopt-engine")
    p.add_argument("--provider", default="fake", help="fake | anthropic:<model> | openai:<model>")
    sub = p.add_subparsers(dest="cmd", required=True)

    g = sub.add_parser("gate", help="run the validation gate once")
    g.add_argument("config")
    g.add_argument("-v", "--verbose", action="store_true")
    g.set_defaults(func=cmd_gate)

    o = sub.add_parser("optimize", help="run the convergence loop")
    o.add_argument("config")
    o.add_argument("--out", help="write the final skill text here")
    o.add_argument("--backend", choices=["native", "skillopt"],
                   help="native rubric gate (default) | real microsoft/SkillOpt gate")
    o.set_defaults(func=cmd_optimize)

    r = sub.add_parser("optimize-repo",
                       help="optimize a skill FOR ONE REPO, fully driven by SkillOpt's ReflACT")
    r.add_argument("repo", help="path to the target repository")
    r.add_argument("--skill", required=True, help="path to the starting SKILL.md")
    r.add_argument("--opt-backend", default="claude-code",
                   help="SkillOpt edit-generator backend: claude-code (keyless) | openai | qwen | minimax")
    r.add_argument("--rollout-provider", default="claude-cli",
                   help="spec generate/score provider: claude-cli | anthropic:<model> | openai:<model>")
    r.add_argument("--rounds", type=int, default=2)
    r.add_argument("--version", default="0.2.0")
    r.add_argument("--out", help="default: <repo>/.reposkillopt/best_skill.md")
    r.set_defaults(func=cmd_optimize_repo)

    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
