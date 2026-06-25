# Phase 0 Research: Commit-Time Gate Hook

All decisions reuse existing machinery; no new dependency is introduced. Each is framed as
Decision / Rationale / Alternatives.

## D1 — Gate selection by artifact kind

**Decision**: `classify_artifact(path, text)` maps a staged `.reposkillopt/` file to a kind, and
`select_gates(kind)` returns exactly the gates that are meaningful for it:

| Kind (how detected) | Gates run |
|---|---|
| Repository Specification (`specs/…`, or front-matter/sections of a repo spec) | coverage (files) + grounding + completeness |
| architecture view (`*architecture*`, or an `## Architecture`/Components+Dependency shape) | check-artifact(architecture) + grounding |
| impact analysis (`*impact*` / impact table) | check-artifact(impact) + grounding |
| ADR (`*adr*` / `## Decision` + `## Consequences`) | check-artifact(adr) |
| task ledger (`*ledger*`/`*tasks*` with `topological_order` front-matter) | check-artifact(ledger) |
| feedback / proposal / other markdown | grounding only |

**Rationale**: Running an irrelevant gate (e.g. completeness on a feedback note) would produce false
failures and either block valid commits or trigger pointless model calls. Classification is a pure
function of path + text → deterministic and unit-testable (a core TDD target). The `check-artifact`
kinds reuse `artifact_checks.py` verbatim; architecture/impact additionally resolve citations
(grounding) because those checks already call `_unresolved`.

**Alternatives considered**: (a) run all four gates on everything — rejected: false failures + wasted
model calls. (b) require the user to declare the kind — rejected: the hook must work unattended; a
deterministic classifier is more honest and testable.

## D2 — Monotonic on the *passing-gate set*, not just the score

**Decision**: Remediation wraps the existing refine step but accepts a candidate round **iff its set
of passing gates is a superset of the carried-forward artifact's passing set** (no gate regresses)
**and** it strictly improves (more gates passing, or the same gates with strictly fewer residual gap
items). The artifact carried forward is the best-so-far ordered by `(|passing gates|, −gap_count)`.

**Rationale**: FR-006/SC-005 demand exact non-regression of passing gates. `refine_loop` is monotonic
on its *score* (`0.5·grounding + 0.3·quality + 0.2·coverage`), which is a proxy: a round could raise
the score while flipping a previously-passing gate to failing. The wrapper makes the gate set itself
the acceptance criterion, so the guarantee is exact rather than proxied. `refine_once` is still the
engine of each round (model revise targeting `spec_gaps`), so we reuse, not fork.

**Alternatives considered**: use `refine_loop` as-is — rejected: score-monotonic ≠ gate-set-monotonic.
Re-implement a new revise prompt — rejected: `judge.revise_spec` + `spec_gaps` already target exactly
the failing-gate evidence.

## D3 — Completeness is fixed deterministically every round (never the model's job)

**Decision**: Each round applies `ensure_symbol_completeness(text, repo)` to the candidate before
scoring gates, exactly as `refine_once` already does. The completeness gate is therefore satisfiable
without a model call.

**Rationale**: Symbol coverage is a deterministic transform (append the "Symbols not yet analyzed"
accounting); making the model responsible for it would be nondeterministic and unreliable. This
mirrors `refine.py` (its comment: "symbol COVERAGE is not listed [in gaps] — the completeness step
guarantees it deterministically every round"). Consequence: a Repository Specification's completeness
gate can pass even when no provider is available — but grounding/coverage(files) still need the model
to fix unresolved/omitted facts, so a genuinely under-grounded artifact still requires a provider.

**Alternatives considered**: leave completeness to the model — rejected: nondeterministic, violates
Principle IV's spirit and duplicates an existing deterministic guarantee.

## D4 — Availability probe + block-and-report degradation (no hang)

**Decision**: `detect_keyless_provider(spec="auto", timeout)` resolves a usable keyless provider:
- explicit `--rollout-provider <id>` → use it (claude-cli/opencode-cli/ollama only; reject api-key ids);
- `auto` → probe candidates in order: `claude-cli` and `opencode-cli` via `shutil.which`; `ollama`
  via a short TCP connect to `127.0.0.1:11434` with a tight timeout. First available wins.
- none available → return `None`.

When the provider is `None`, `gate_commit` runs the deterministic gates and exits **block-and-report**
(non-zero with a per-gate report + bypass instructions) — it never calls a model and never waits.
The hook applies the same principle one level up: if `python3` or the engine package is unreachable,
the hook prints a block-and-report message (it may still run the dependency-free `coverage-gate.sh`)
and exits non-zero with bypass instructions — it never hangs.

**Rationale**: FR-010/FR-011/SC-003. An enforcement hook that can hang on an unreachable model or trap
a developer with no path forward is unacceptable. Tight probe timeouts guarantee bounded latency.

**Alternatives considered**: block the commit hard when no provider — rejected: offline developers
would be trapped (the env toggle + `--no-verify` exist precisely so they aren't, but the *default*
no-provider behavior must still be report-and-exit, not hang). Auto-install a provider — out of scope.

## D5 — Gate the staged (index) content; re-stage exactly the changed artifacts

**Decision**: For each staged artifact, read the **index** blob (`git show :<path>`), gate/remediate
that text, write the converged result to the working tree, and `git add <path>` only the artifacts
whose content actually changed. `gate_commit` returns the set of re-staged paths (the re-stage
accounting that is unit-tested). A `--no-restage` flag lets tests assert the decision without touching
a real index.

**Rationale**: FR-014 — what is gated must be what is committed. Reading the index (not the working
tree) makes partial staging correct: only the staged version is judged and only its remediated form is
committed. Re-staging exactly the changed set avoids spurious diffs.

**Alternatives considered**: gate the working-tree file — rejected: diverges from the index on partial
staging, so the committed content could differ from what passed the gate.

## D6 — Install location respects `core.hooksPath`; chain a pre-existing hook

**Decision**: Install to `"$(git rev-parse --git-path hooks)"/pre-commit` (honors `core.hooksPath`
and worktrees). If a `pre-commit` already exists there, move it to a recorded backup
(`pre-commit.reposkillopt-chained`) and the installed hook invokes the backup **first**, preserving
its exit status (`sh backup "$@"; rc=$?; [ "$rc" -ne 0 ] && exit "$rc"`), then runs the gate logic.

**Rationale**: FR-012 — real repos have pre-commit hooks; silently disabling them is data loss.
Using `git rev-parse --git-path hooks` is the portable way to find the hooks dir under custom
`core.hooksPath` and linked worktrees.

**Alternatives considered**: write directly to `.git/hooks` — rejected: wrong under `core.hooksPath`.
Append our logic into the existing hook file — rejected: brittle to re-runs and hard to cleanly
uninstall; a separate backup + chain call is reversible and recorded.

## D7 — Installer lifecycle via a `git-hook` manifest adapter row

**Decision**: Reuse the existing manifest: install records a row with adapter id `git-hook`, version =
tool version, and `paths_csv` = the installed hook path **and** the chained-backup path (if any).
`--list` shows it via `manifest_list`; `--uninstall git-hook` removes the installed hook, restores the
chained backup from the recorded path, and drops the row via `manifest_remove_row`. Reuse
`copy_atomic` for atomic writes.

**Rationale**: FR-013 — one lifecycle mechanism, already proven (002/006). The line-based manifest
format is unchanged; only a new adapter id is introduced.

**Alternatives considered**: a separate hook-state file — rejected: duplicates the manifest and risks
drift between two sources of truth.

## D8 — Bypass surface and round budget

**Decision**: Two documented bypasses, both honored: `REPOSKILLOPT_HOOK=off` (hook is a no-op) and
git's native `git commit --no-verify` (git skips the hook entirely). Default remediation round budget
= **3** (matches `refine_loop`'s default), overridable via `--rounds`.

**Rationale**: FR-005/FR-011. A bounded budget guarantees termination; the env toggle and `--no-verify`
guarantee a developer is never trapped. 3 rounds matches the validated `refine` default and the live
018/020 runs that converged within it.

## D9 — Honesty about determinism

**Decision**: Document plainly (engine README + hook contract) that gate *verdicts* are reproducible
(same artifact + same repo ⇒ same verdict) while the remediation *edits* are model-driven and
nondeterministic. The failure report states which gates still fail, on which artifact, and how many
rounds were spent — never implying success it didn't achieve (FR-016/FR-017/SC-005).

**Rationale**: Principle IV honesty and the project-wide "report real numbers, flag caveats" norm.
