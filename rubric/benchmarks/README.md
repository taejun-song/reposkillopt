# Grounding benchmark

A reproducible, **model-free** measurement of how grounded RepoSkillOpt's Repository
Specifications are: the fraction of a spec's `file:line` / `file:Symbol` citations that
**resolve against the real repository files** (feature-005 grounding), plus the 7
deterministic rubric checks.

## Run

```sh
cd engine
python3 -m reposkillopt_engine benchmark --manifest ../rubric/benchmarks/seed-manifest.tsv --date YYYY-MM-DD
```

This pins and shallow-clones each repo at its tagged commit, scores the shipped reference
specs, and writes `rubric/benchmarks/<date>-grounding.md` (per-repo table + aggregate +
reproduce command + a machine-readable TSV block). Score mode makes **zero** model calls and
is reproducible: same manifest + same specs + same pins → identical numbers.

## Manifest

`seed-manifest.tsv` — `name<TAB>repo<TAB>spec`, one entry per line, `#` comments. `repo` is a
local path or `url@commit`; `spec` is repo-root-relative.

## Generate mode (optional, needs a provider)

`--mode generate --skill ../skills/repo-skillopt/SKILL.md --rollout-provider claude-cli`
regenerates each spec with the **current** canonical skill before grounding — measuring the
live skill rather than the shipped reference outputs.

## First result (2026-06-07)

Seed = the full `pallets/click@8.1.7` reference spec. **61% of citations resolve** (109/179).
The unresolved ones are genuine imprecision in the reference spec — bare shorthand like
`__init__.py:15` / `decorators.py:292` that doesn't resolve against the repo root (the real
files are `src/click/__init__.py`, `src/click/decorators.py`). That is exactly the defect the
benchmark exists to surface: the skill's own discipline requires real filesystem paths, and
the deterministic grounding refuses shorthand. The number is honest, reproducible, and a target
to improve (`--mode generate` measures the current canonical skill rather than the shipped spec).

The seed deliberately holds only full 19-section specs; it should grow with more diverse repos.
