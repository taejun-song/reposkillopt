# Data Model — 010 Completeness Guarantee

## Completeness transform
`ensure_symbol_completeness(spec_text: str, repo_path: str) -> str`
- Pure, deterministic, idempotent. Input: a spec + repo. Output: the spec guaranteed to account
  for every defined function/class.

## Appended/updated section (the only structural change to a spec)
```
## Symbols not yet analyzed

N defined, M analyzed, N−M listed.

- path/to/file.ext: name1, name2, …      (or "path/to/file.ext: K symbols" when many)
- …
(… T more files omitted for size — note recorded …)   # only on huge repos
```
- Grouped by file; every not-yet-accounted symbol's file appears, so `compute_structure`
  credits 100% accounting via file-presence.
- Counts: N = total defined symbols; M = symbols named in the analyzed body; N−M = listed.

## Invariants
| property | guarantee |
|---|---|
| symbol_coverage after step | exactly 1.0 (FR-003/SC-001) |
| idempotent | 2nd application byte-identical (FR-004/SC-002) |
| analyzed_fraction | unchanged vs the model's original (FR-005/SC-003) |
| model-free / reproducible | no LLM; same inputs → same output (FR-010/SC-006) |

## Wiring (no metric/behavior change)
- `optimize_repo` → applied to emitted `best_spec`.
- `benchmark.run_entry` generate-mode → applied to the generated spec before scoring.
- `cli complete-spec` → agent-path helper producing the same result.
- Canonical skill final stage → instructs running the step; mirrored to 4 adapters; version 0.4.0.
