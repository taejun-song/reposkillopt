---
kind: section-scoped-validation
date: 2026-06-11
repo: eco-standard-wiki
commit: 93014a973becda3152172cce7ec4cdc2985f3a7d
canonical_version: 0.6.0
mode: section-scoped (live, 19 per-section model calls)
---

# Section-scoped generation — live end-to-end validation (feature 011)

Live run of `benchmark --mode generate --section-scoped` on eco-standard-wiki: each of the 19
sections generated from only its deterministically-retrieved evidence slice, assembled, then the
completeness step applied once. Confirms the deterministic 86% peak-context reduction holds
through a real generation and the spec still satisfies every guarantee.

| Axis | Section-scoped (live) | Single-pack baseline (same skill) |
|---|---|---|
| Peak context per model call | **7.9 KB (~2.0k tok)** | 55.6 KB (~13.9k tok) |
| Citation grounding | 92.9% (260/280) | 87.4% (173/198) |
| Section completeness | 100% | 100% |
| Symbol coverage | 100% | 100% |
| ER-diagram grounding | 100% | 92.3% |
| Quality score | 97.7% | 98.1% |
| Malformed-citation rate | 0.36% | 5.1% |
| Analyzed fraction | 13.3% | 10.7% |

**Peak context −86%**; total evidence across sections (~85.7 KB) exceeds the single pack (the
documented tradeoff). The assembled spec is fully sectioned, fully symbol-covered, and fully
ER-grounded; grounding is actually *higher* than the single-pack baseline at the same skill —
focused per-section evidence appears to help citation discipline. No section-seam degradation
observed (single run; model nondeterminism applies, so the grounding delta is indicative, not
definitive).

```tsv
eco	93014a973becda3152172cce7ec4cdc2985f3a7d	260	280	0.9286	false	0.9773	2.5688	0.8899	0.0036	1.0000	1.0000	0.1330	79	1.0000
```

Reproduce:

```sh
python3 -m reposkillopt_engine benchmark --manifest <eco.tsv> --mode generate \
    --skill skills/repo-skillopt/SKILL.md --rollout-provider claude-cli --section-scoped --date ss
```
