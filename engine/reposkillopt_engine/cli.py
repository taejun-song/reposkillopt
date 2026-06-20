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


# Low-context preset: shrink the evidence pack (keep the high-signal structure inventory,
# trim file excerpts) so the per-generation context fits a small window. ~60k -> ~24k chars.
_LOW_CTX = {"char_budget": 24_000, "max_files": 12, "max_file_lines": 200}


def _pack_opts(args) -> dict:
    """Resolve evidence-pack sizing from --low-context / --pack-budget (empty dict = defaults)."""
    opts = dict(_LOW_CTX) if getattr(args, "low_context", False) else {}
    if getattr(args, "pack_budget", None):
        opts["char_budget"] = args.pack_budget      # explicit budget overrides the preset
    return opts


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
    from .evidence import build_evidence_pack
    from .skillopt_native import HAS_SKILLOPT, RepoTask, build_repo_digest, optimize_repo
    if not HAS_SKILLOPT:
        print("error: the 'skillopt' package is required (pip install skillopt)", file=sys.stderr)
        return 1
    repo = Path(args.repo)
    if not repo.is_dir():
        print(f"error: not a directory: {repo}", file=sys.stderr)
        return 2
    skill = Path(args.skill).read_text()
    # Build the evidence pack ONCE per run (FR-002); reused across every candidate and round.
    pack_opts = _pack_opts(args)
    rounds = args.rounds if args.rounds is not None else (1 if args.low_context else 2)
    if pack_opts:
        print(f"building evidence pack for {repo.name} (low-context: "
              f"budget={pack_opts.get('char_budget')} chars) …", file=sys.stderr)
    else:
        print(f"building evidence pack for {repo.name} …", file=sys.stderr)
    pack = build_evidence_pack(str(repo), **pack_opts)
    print(f"  pack: {len(pack.text)} chars, {len(pack.included_files)} files embedded, "
          f"{len(pack.omitted)} omitted", file=sys.stderr)
    task = RepoTask(name=repo.name, digest=build_repo_digest(str(repo)), pack=pack)
    print(f"optimizing skill for {repo.name} — SkillOpt opt-backend={args.opt_backend}, "
          f"rollout={args.rollout_provider}, rounds={rounds}", file=sys.stderr)
    res = optimize_repo(skill, args.version, task,
                        opt_backend=args.opt_backend, provider=args.rollout_provider,
                        rounds=rounds, timeout=args.timeout)
    # Output 1: the specialized skill (canonical skill is never touched — FR-011).
    out = Path(args.out) if args.out else (repo / ".reposkillopt" / "best_skill.md")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(res.skill_text)
    # Output 2: the best Repository Specification it produced (FR-010).
    spec_out = repo / ".reposkillopt" / "specs" / "optimized-repository-specification.md"
    spec_out.parent.mkdir(parents=True, exist_ok=True)
    spec_out.write_text(res.best_spec)
    print(f"final version {res.version}; {res.accepted} accepted of {len(res.history)} rounds")
    print(f"  reward {res.best_reward:.3f}; citation resolution {res.citation_rate:.0%}")
    print(f"  wrote skill -> {out}")
    print(f"  wrote spec  -> {spec_out}")
    for rd in res.history:
        print(f"  round {rd.index}: [{rd.source}] {rd.action} "
              f"({'ACCEPT' if rd.accepted else 'reject'})", file=sys.stderr)
    return 0


def cmd_benchmark(args) -> int:
    from .benchmark import render_report, run_benchmark
    manifest = Path(args.manifest)
    if not manifest.is_file():
        print(f"error: manifest not found: {manifest}", file=sys.stderr)
        return 2
    provider = skill_text = None
    if args.mode == "generate" or args.rubric:
        from .providers import make_provider
        if args.mode == "generate" and not args.skill:
            print("error: --mode generate requires --skill", file=sys.stderr)
            return 2
        kw = {} if args.rollout_provider.startswith("fake") else {"timeout": args.timeout}
        provider = make_provider(args.rollout_provider, **kw)
        if args.skill:
            skill_text = Path(args.skill).read_text()
    repo_root = Path(__file__).resolve().parents[2]   # reposkillopt repo root
    print(f"benchmarking grounding ({args.mode} mode) over {manifest} …", file=sys.stderr)
    report = run_benchmark(manifest.read_text(), mode=args.mode, date=args.date,
                           provider=provider, skill_text=skill_text, base_dir=str(repo_root),
                           with_rubric=args.rubric, pack_opts=_pack_opts(args),
                           section_scoped=getattr(args, "section_scoped", False))
    out_dir = Path(args.out) if args.out else (repo_root / "rubric" / "benchmarks")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"{args.date}-grounding.md"
    out_file.write_text(render_report(report, manifest_path=str(manifest)))
    a = report.aggregate
    print(f"scored {a.n} (skipped {a.skipped}): mean {a.mean_rate:.0%}, median {a.median_rate:.0%}, "
          f"all-checks-pass {a.checks_pass_share:.0%}")
    print(f"  wrote {out_file}")
    return 0


def cmd_complete_spec(args) -> int:
    from .completeness import ensure_symbol_completeness
    from .quality import compute_structure
    from .structure import extract_schema, extract_symbols
    repo, spec = Path(args.repo), Path(args.spec)
    if not repo.is_dir():
        print(f"error: not a directory: {repo}", file=sys.stderr); return 2
    if not spec.is_file():
        print(f"error: spec not found: {spec}", file=sys.stderr); return 2
    done = ensure_symbol_completeness(spec.read_text(), str(repo))
    m = compute_structure(done, extract_symbols(str(repo)), extract_schema(str(repo)))
    if args.out:
        Path(args.out).write_text(done)
        print(f"wrote {args.out} — symbol coverage {m.symbol_coverage:.0%} "
              f"({m.symbol_accounted}/{m.symbol_total}); analyzed {m.analyzed_fraction:.0%}")
    else:
        sys.stdout.write(done)
    return 0


def cmd_ontology(args) -> int:
    import json as _json

    from .ontology import (build_ontology, render_entity_map, render_er_diagram,
                           render_relationship_graph, to_structured)
    repo = Path(args.repo)
    if not repo.is_dir():
        print(f"error: not a directory: {repo}", file=sys.stderr)
        return 2
    onto = build_ontology(str(repo))
    if args.json:
        sys.stdout.write(_json.dumps(to_structured(onto), indent=2) + "\n")
        return 0
    print(render_entity_map(onto))
    print("\n### Relationship graph\n")
    print(render_relationship_graph(onto))
    print("\n### Data model (ER)\n")
    print(render_er_diagram(onto))
    c = to_structured(onto)["counts"]
    print(f"\n# {sum(c.values())} entities, {len(onto.relations)} relations, "
          f"{len(onto.unresolved)} unresolved", file=sys.stderr)
    return 0


def cmd_workflows(args) -> int:
    from .workflow import analyze_workflows, render_workflow_section
    repo = Path(args.repo)
    if not repo.is_dir():
        print(f"error: not a directory: {repo}", file=sys.stderr)
        return 2
    rep = analyze_workflows(str(repo))
    sys.stdout.write(render_workflow_section(rep))
    print(f"# {sum(rep.counts.values())} business entrypoints "
          f"({', '.join(f'{k}:{rep.counts[k]}' for k in sorted(rep.counts))})", file=sys.stderr)
    return 0


def cmd_refactors(args) -> int:
    from .refactor import analyze_refactors, render_refactor_section
    repo = Path(args.repo)
    if not repo.is_dir():
        print(f"error: not a directory: {repo}", file=sys.stderr)
        return 2
    rep = analyze_refactors(str(repo))
    sys.stdout.write(render_refactor_section(rep))
    print(f"# {rep.counts['clusters']} repeated structures across {rep.counts['instances']} functions",
          file=sys.stderr)
    return 0


def cmd_refine_spec(args) -> int:
    from .providers import make_provider
    from .refine import refine_loop, score_spec
    repo = Path(args.repo)
    if not repo.is_dir():
        print(f"error: not a directory: {repo}", file=sys.stderr)
        return 2
    skill = Path(args.skill).read_text()
    kw = {} if args.rollout_provider.startswith("fake") else {"timeout": args.timeout}
    provider = make_provider(args.rollout_provider, **kw)
    if args.spec:                       # carry an EXISTING spec forward (e.g. optimize-repo's output)
        initial = Path(args.spec).read_text()
    else:                               # or generate one to start from
        from .completeness import ensure_symbol_completeness
        from .evidence import build_evidence_pack
        from .judge import generate_spec
        pack = build_evidence_pack(str(repo))
        initial = ensure_symbol_completeness(generate_spec(provider, skill, repo.name, pack.text), str(repo))
    s0, _ = score_spec(str(repo), initial)
    print(f"refining {repo.name} — initial score {s0:.3f}, up to {args.rounds} rounds", file=sys.stderr)
    res = refine_loop(provider, skill, str(repo), repo.name, initial_spec=initial, rounds=args.rounds)
    out = Path(args.out) if args.out else (repo / ".reposkillopt" / "specs" / "refined-repository-specification.md")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(res.spec)
    sN, _ = score_spec(str(repo), res.spec)
    print(f"final score {sN:.3f} (was {s0:.3f}) after {res.rounds} rounds; wrote {out}")
    for st in res.history:
        print(f"  round {st.round}: score {st.score:.3f} cite {st.citation_rate:.0%} "
              f"{'ACCEPT' if st.accepted else 'reject'} ({st.n_gaps} gaps left)", file=sys.stderr)
    return 0


def cmd_render(args) -> int:
    from .render import render
    spec = Path(args.spec)
    if not spec.is_file():
        print(f"error: spec not found: {spec}", file=sys.stderr)
        return 2
    out = render(spec.read_text(), args.view)
    if args.out:
        Path(args.out).write_text(out)
        print(f"wrote {args.view} view -> {args.out}", file=sys.stderr)
    else:
        sys.stdout.write(out)
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
                   help="spec generate/score provider: claude-cli | opencode-cli | anthropic:<model> | openai:<model> | ollama:<model>")
    r.add_argument("--rounds", type=int, default=None,
                   help="optimize rounds (default 2; --low-context defaults this to 1)")
    r.add_argument("--pack-budget", type=int, default=None,
                   help="evidence-pack character budget (default 60000; lower = less context per generation)")
    r.add_argument("--low-context", action="store_true",
                   help="shrink the evidence pack (~24k chars) and default rounds to 1, for small context windows")
    r.add_argument("--timeout", type=float, default=600.0,
                   help="per model-call timeout in seconds (spec generation is slow on big repos)")
    r.add_argument("--version", default="0.2.0")
    r.add_argument("--out", help="default: <repo>/.reposkillopt/best_skill.md")
    r.set_defaults(func=cmd_optimize_repo)

    b = sub.add_parser("benchmark",
                       help="measure citation-grounding of specs across a pinned repo suite")
    b.add_argument("--manifest", required=True, help="TAB-separated name<TAB>repo<TAB>spec manifest")
    b.add_argument("--mode", choices=["score", "generate"], default="score")
    b.add_argument("--out", help="output dir (default: rubric/benchmarks/)")
    b.add_argument("--date", required=True, help="report date YYYY-MM-DD (kept explicit for reproducibility)")
    b.add_argument("--skill", help="generate mode: path to the SKILL.md to regenerate specs with")
    b.add_argument("--rollout-provider", default="claude-cli",
                   help="generate mode: spec provider (claude-cli | opencode-cli | anthropic:<model> | openai:<model> | ollama:<model>)")
    b.add_argument("--rubric", action="store_true",
                   help="ALSO report the LLM rubric score (non-reproducible, off by default; needs a provider)")
    b.add_argument("--timeout", type=float, default=900.0,
                   help="generate-mode: per model-call timeout in seconds (default 900; big repos are slow)")
    b.add_argument("--pack-budget", type=int, default=None,
                   help="generate-mode: evidence-pack character budget (default 60000)")
    b.add_argument("--low-context", action="store_true",
                   help="generate-mode: shrink the evidence pack (~24k chars) for small context windows")
    b.add_argument("--section-scoped", action="store_true",
                   help="generate-mode: produce the spec section-by-section from per-section retrieval "
                        "(lowers PEAK context per call; may raise TOTAL tokens). Opt-in; default off.")
    b.set_defaults(func=cmd_benchmark)

    c = sub.add_parser("complete-spec",
                       help="deterministically guarantee every function/class is accounted for in a spec")
    c.add_argument("--repo", required=True, help="path to the analyzed repository")
    c.add_argument("--spec", required=True, help="path to the Repository Specification to complete")
    c.add_argument("--out", help="write here (default: stdout)")
    c.set_defaults(func=cmd_complete_spec)

    on = sub.add_parser("ontology",
                        help="build the deterministic codebase ontology (entities + relations), model-free")
    on.add_argument("repo", help="path to the repository")
    on.add_argument("--json", action="store_true", help="emit structured JSON instead of Markdown views")
    on.set_defaults(func=cmd_ontology)

    wf = sub.add_parser("workflows",
                        help="enumerate + trace every business-process pipeline (route/job/cli), model-free")
    wf.add_argument("repo", help="path to the repository")
    wf.set_defaults(func=cmd_workflows)

    rf = sub.add_parser("refactors",
                        help="detect repeated structure that could be abstracted (advisory), model-free")
    rf.add_argument("repo", help="path to the repository")
    rf.set_defaults(func=cmd_refactors)

    rs = sub.add_parser("refine-spec",
                        help="continuously improve a spec: carry it forward + fix deterministic gaps each round (monotonic)")
    rs.add_argument("repo", help="path to the repository")
    rs.add_argument("--skill", required=True, help="skill to revise with (e.g. optimize-repo's best_skill.md)")
    rs.add_argument("--spec", help="starting spec to carry forward (e.g. optimize-repo's output); default: generate one")
    rs.add_argument("--rollout-provider", default="claude-cli",
                    help="revise/score provider: claude-cli | opencode-cli | anthropic:<model> | openai:<model> | ollama:<model>")
    rs.add_argument("--rounds", type=int, default=3)
    rs.add_argument("--timeout", type=float, default=600.0)
    rs.add_argument("--out", help="default: <repo>/.reposkillopt/specs/refined-repository-specification.md")
    rs.set_defaults(func=cmd_refine_spec)

    rv = sub.add_parser("render",
                        help="project a spec into an audience-specific view (deterministic, model-free)")
    rv.add_argument("--spec", required=True, help="path to the Repository Specification")
    rv.add_argument("--view", required=True, choices=["agent", "structured"],
                    help="agent: lean Markdown (no diagrams/comments) | structured: JSON of claims+citations")
    rv.add_argument("--out", help="write here (default: stdout)")
    rv.set_defaults(func=cmd_render)

    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
