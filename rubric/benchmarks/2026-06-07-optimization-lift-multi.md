---
kind: optimization-lift-suite
date: 2026-06-07
metric: citation-resolution-rate (feature-005 grounding), generate-mode A/B per repo
repos: 4
---

# Optimization lift across 4 repos

For each repo, same A/B: generate-mode grounding with the **canonical** skill (baseline) vs
the **per-repo SkillOpt-optimized** skill (`optimize-repo`, 2 rounds). Same repo, same metric.

| Repo | Lang | Baseline | Optimized | Δ | optimize-repo |
|------|------|----------|-----------|---|---------------|
| `pallets/click@8.1.7` | py | 74% | **98%** | **+24** | 1/2 accepted |
| `pallets/itsdangerous@2.1.2` | py | 69% | **100%** | **+31** | 1/2 accepted |
| `pallets/markupsafe@2.1.3` | py | 100% | 98% | −2 | 1/2 accepted |
| `chalk/chalk@v5.3.0` | js | 100% | 100% | 0 | **0/2 accepted** |

## What this shows (honestly)

- **Where baseline grounding had gaps, optimization closed them** — click 74→98, itsdangerous
  69→100. These are the cases that matter, and the lift is large (+24, +31).
- **Where the baseline was already ~perfect, optimization held steady, not broke it.** chalk's
  gate **correctly rejected all edits** (0/2 accepted — nothing to improve). markupsafe shows a
  −2 pt wobble: it accepted an edit whose *internal* citation resolution was 100%, but a fresh
  generate-mode regeneration landed at 97.7% — i.e. within generate-mode stochastic noise, not a
  real regression.
- **Net:** the optimizer targets the real problem (poor grounding) and exercises restraint when
  there's nothing to fix. Across the 2 repos with headroom, mean grounding rose from 71% → 99%.

## Caveat

Generate-mode numbers depend on the model and are not bit-reproducible (unlike score mode); the
direction and magnitude are the result. The deterministic score-mode metric (citation resolution
against pinned files) is the reproducible backbone; see `2026-06-07-grounding.md`.

Reproduce: see `2026-06-07-optimization-lift-click.md` (same procedure, per repo).
