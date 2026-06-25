# Contract: `gate-commit` engine entrypoint

The single entrypoint the hook calls. Gates staged `.reposkillopt/` artifacts and, on failure,
auto-remediates within a bounded, gate-set-monotonic loop, then re-stages converged artifacts.

## CLI

```
reposkillopt-engine gate-commit --repo <dir> --skill <skill.md> \
    --staged <path> [<path> …] \
    [--rollout-provider auto|claude-cli|opencode-cli|ollama] \
    [--rounds N] [--timeout SECONDS] [--no-restage]
```

- `--repo` — target repo root (defaults to the git work-tree root).
- `--skill` — the skill text used by the remediation revise step (defaults to the installed
  `repo-skillopt` skill).
- `--staged` — the staged artifact paths the hook detected (repo-relative). Only paths under
  `.reposkillopt/` are gated; any other path is ignored (defensive — the hook already filters).
- `--rollout-provider` — keyless id or `auto` (default `auto`; api-key ids are rejected, FR-009).
- `--rounds` — remediation round budget (default 3, D8).
- `--no-restage` — gate/remediate and report, but do **not** `git add` (used by tests; D5).

## Behavior

1. Classify each staged artifact (`classify_artifact`) and select its gates (`select_gates`).
2. Run the applicable gates on the **staged (index) content** (`git show :<path>`; D5).
3. If every applicable gate passes for every artifact → **exit 0** (commit proceeds), no model call,
   nothing changed (FR-003).
4. Otherwise resolve a provider (`detect_keyless_provider`):
   - **provider available** → for each failing artifact, run the bounded monotonic remediation loop
     (D2/D3). On convergence, write the converged text to the working tree and (unless `--no-restage`)
     `git add` it; record it in `restaged`.
   - **no provider** (`None`) → **block-and-report**: do not call a model; print the per-gate failures
     and bypass instructions; set `degraded=True` (FR-010).
5. Exit code:
   - **0** — every applicable gate passes across all staged artifacts (after any remediation); the
     committed content is the gated content.
   - **1** — at least one artifact did not converge, or block-and-report (no provider). Precise
     per-artifact, per-gate report on stderr + bypass instructions.
   - **2** — usage error (missing `--repo`/`--skill`, unreadable path, api-key provider requested).

## Guarantees

- **Determinism of gates** — for a fixed artifact + repo, every gate verdict is reproducible (FR-016).
- **Bounded** — the loop runs at most `--rounds` rounds and stops early on no-improvement (FR-005).
- **Monotonic** — no accepted round reduces the passing-gate set; a regressing candidate is discarded
  and never re-staged (FR-006/SC-005).
- **Re-stage fidelity** — only artifacts whose staged content changed are `git add`'d, and the
  re-staged content is exactly what passed the gates (FR-007/FR-014). `restaged` is the exact set.
- **No silent success** — on non-convergence nothing is re-staged and the report names the residual
  failing gates and rounds spent (FR-008/FR-017).
- **No hang** — the no-provider path performs no model call and returns in deterministic-gate time
  (SC-003).

## Reuse (no forks, no new deps)

`classify_artifact`/`select_gates`/`run_gates`/`remediate`/`gate_commit` live in `commit_gate.py` and
call: `grounding.ground_spec` (frozen), `quality/structure.compute_structure`, `completeness.
ensure_symbol_completeness`, `artifact_checks.*`, `refine.{spec_gaps,refine_once}` + `judge.revise_spec`,
`providers.make_provider`, and `scripts/coverage-gate.sh` (subprocess for the `coverage` gate).
