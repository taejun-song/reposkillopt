---
kind: optimization-lift
date: 2026-06-07
repo: pallets/click@8.1.7
metric: citation-resolution-rate (feature-005 grounding, model-free)
baseline_canonical: 0.7419
optimized_per_repo: 0.9843
lift_points: 24.2
---

# Optimization lift — does SkillOpt optimization improve grounding?

A/B on `pallets/click@8.1.7`, same repo, same metric (the grounding benchmark's
**generate** mode: the skill regenerates the spec, then every `file:line`/`file:Symbol`
citation is resolved against the real files).

| Skill | Citation grounding |
|---|---|
| Canonical (baseline) | **74%** |
| Per-repo SkillOpt-optimized | **98%** |
| _lift_ | **+24 points** |

(For reference, the *static hand-authored* `examples/reference-output` click spec scores 61% —
the optimized, freshly-generated spec nearly doubles its grounded coverage.)

## What the optimizer learned (unprompted)

`optimize-repo` accepted 1 of 2 rounds (round 1 `accept_new_best`; reward 0.917; the accepted
candidate's internal citation resolution = 100%). The edit it generated from click's grounding
failures, verbatim:

> Cited paths MUST be full paths relative to the repository root (e.g., `src/click/core.py:57`,
> not `core.py:57`). Before writing any citation, confirm the path exists in the source tree
> observed in stage (a); never shorten or guess a path prefix.

That is exactly the defect the benchmark surfaced (bare `core.py:57` / `__init__.py:15` don't
resolve; the real files are `src/click/...`). The benchmark **caught** the gap and the optimizer
independently **learned to close it** — the loop, measured end to end.

## Reproduce

```sh
CLICK=$(mktemp -d); git clone --depth 1 --branch 8.1.7 https://github.com/pallets/click "$CLICK"
printf 'click\t%s\t-\n' "$CLICK" > /tmp/ab.tsv
cd engine
# baseline (canonical skill)
python3 -m reposkillopt_engine benchmark --manifest /tmp/ab.tsv --mode generate \
  --skill ../skills/repo-skillopt/SKILL.md --rollout-provider claude-cli --date baseline --out /tmp/ab-baseline
# optimize for click
python3 -m reposkillopt_engine optimize-repo "$CLICK" --skill ../skills/repo-skillopt/SKILL.md \
  --opt-backend claude-code --rollout-provider claude-cli --rounds 2
# optimized (specialized skill)
python3 -m reposkillopt_engine benchmark --manifest /tmp/ab.tsv --mode generate \
  --skill "$CLICK/.reposkillopt/best_skill.md" --rollout-provider claude-cli --date optimized --out /tmp/ab-optimized
```

> Note: generate-mode numbers depend on the model and are not bit-reproducible like score mode;
> the ~74%→~98% direction and magnitude are the result.
