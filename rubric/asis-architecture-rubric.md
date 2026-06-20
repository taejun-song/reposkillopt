# Rubric — As-Is Architecture Analysis (`repo-architecture`)

Score each dimension 0–3 (0 absent · 1 weak · 2 adequate · 3 strong). A Skill Edit Proposal passes
the validation gate only if **no dimension regresses** on the held-out set AND the deterministic
checks pass.

| # | Dimension | What 3 looks like |
|---|-----------|-------------------|
| 1 | Architectural correctness | Containers/components/edges match the real code; no fabricated structure |
| 2 | Evidence grounding | Every component/edge cites a resolvable `file:line` |
| 3 | Blast-radius completeness | Impact covers modules, tests, contracts, call sites for the target |
| 4 | Confidence calibration | Each impact row's high/medium/low matches evidence strength |
| 5 | Unknown honesty | Unresolvable structure/impact marked `[unknown]` with reason, never dropped |
| 6 | Level coherence | C4 levels (context→container→component) are consistent and non-overlapping |

## Deterministic checks (model-free, must pass)
- `check_architecture_view(repo, view)` — every Components/Dependency bullet cited + all citations resolve.
- `check_impact_analysis(repo, impact)` — every impact row has a citation AND a confidence label.
