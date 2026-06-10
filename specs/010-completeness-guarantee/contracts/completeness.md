# Contract — Completeness Step (010)

## `engine/reposkillopt_engine/completeness.py` (NEW)

```python
def ensure_symbol_completeness(spec_text: str, repo_path: str, *, max_chars: int = 20_000) -> str:
    # 1. syms = structure.extract_symbols(repo_path)
    # 2. find existing "Symbols not yet analyzed" section; analyzed_body = spec minus it
    # 3. accounted = name in spec OR file in existing section; missing = not accounted
    # 4. if not missing: return spec_text unchanged   (idempotent)
    # 5. build the section (grouped by file; names until max_chars then per-file counts; counts line)
    # 6. replace existing section or append; return new spec
```

- **Pure, deterministic, idempotent, model-free.** Reuses feature-009 `extract_symbols` and the
  feature-008/009 "accounted = name present OR file listed" rule.
- **Post-condition**: `compute_structure(result, extract_symbols(repo), …).symbol_coverage == 1.0`.
- **Invariant**: `analyzed_fraction(result) == analyzed_fraction(spec_text)` (listing ≠ analysis).

## Wiring

- `skillopt_native.optimize_repo`: `res.best_spec = ensure_symbol_completeness(res.best_spec, task.repo_path)` before return (when a repo path is available).
- `benchmark.run_entry` (mode == "generate"): `spec_text = ensure_symbol_completeness(spec_text, repo_path)` before `ground_spec` / `compute_*`.
- Default/score mode: **not** applied (measures the given spec as authored).

## CLI (`cli.py`)

```
reposkillopt-engine complete-spec --repo <path> --spec <path> [--out <path>]
```
- Writes the completed spec to `--out` (or stdout); model-free; prints the resulting `N defined, M analyzed, N−M listed`.

## Skill / adapters (Markdown, mirrored)

- `skills/repo-skillopt/SKILL.md` final workflow stage: *after producing the spec, run the
  completeness step (or append the deterministically-computed listing) so every function/class is
  accounted for; never hand-transcribe the list.* Bump `version` → 0.4.0; CHANGELOG row.
- Mirror into `adapters/{claude-code,codex,opencode,generic}/*`; `canonical_version` → 0.4.0.

## Invariants
- Grounding behavior, the rubric, the optimizer reward, and the metric definitions are **unchanged**
  (FR-010). No new heavyweight dependency. Reproducible.
