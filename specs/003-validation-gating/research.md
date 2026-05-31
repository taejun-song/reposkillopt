# Phase 0 Research — Validation-Gated Skill Convergence

The four highest-impact decisions were resolved in `/speckit.clarify` (see `spec.md` → *Clarifications*). This document confirms those and records the remaining design decisions. Each: Decision / Rationale / Alternatives considered.

## R1 — Gate criterion (confirmed)

- **Decision**: Accept iff (a) no per-dimension score regresses on any held-out repo, (b) all 7 deterministic checks still pass, and (c) the proposal's `expected_effect` is realized on ≥1 dimension, OR the proposal is a clarifying edit that explicitly waives improvement (recorded in the report).
- **Rationale**: Canonical edits are often additive/clarifying and target one dimension while holding others; demanding strict improvement on *all* dimensions would block valid edits. Requiring "no regression + realized effect (or waiver)" prevents both regressions and no-op churn.
- **Alternatives**: Strict improvement on the targeted dimension (too restrictive for additive edits); no-regression only (lets no-op edits through). Both rejected in clarify.

## R2 — Scoring input = regenerate, then score (confirmed)

- **Decision**: For each held-out repo, **re-run the candidate skill** to produce a fresh Repository Specification, then score that. Never score stale/pre-existing text.
- **Rationale**: A change to a workflow stage (e.g., "enumerate `tests/*` subdirs") only manifests in *regenerated* output; scoring static text would make such edits invisible to the gate.
- **Alternatives**: Re-score existing text (cheap but blind to behavioral edits); maintainer's choice per run (inconsistent gate). Rejected.

## R3 — Reproducibility via a scorer-of-record (confirmed)

- **Decision**: A named human **scorer-of-record** records the per-dimension and deterministic-check scores in the report. The PASS/FAIL **verdict is a pure function of those recorded scores**. "Reproducible" means: re-evaluating the recorded scores yields the same verdict — not that the LLM regeneration is bit-identical.
- **Rationale**: Rubric scoring is judgment; LLM regeneration is non-deterministic. Anchoring reproducibility to the *recorded scores* is honest and still gives a deterministic, auditable verdict (FR-011, FR-015, SC-005).
- **Alternatives**: N-scorers + majority (more robust, heavier — deferred as a future tightening); agent-scores-authoritative (non-reproducible). Rejected.

## R4 — Re-baseline trigger (confirmed)

- **Decision**: Recompute held-out **baseline** scoring sheets whenever the released canonical version changes (i.e., right after any accepted proposal bumps the version). Baselines are labeled with the released version they describe.
- **Rationale**: The gate compares candidate-vs-baseline; the baseline must reflect the *current released* version or the comparison floor drifts.
- **Alternatives**: Manual-only (risk of stale floor); fixed cadence (decoupled from what actually changes the skill). Rejected.

## R5 — Held-out set composition (must exclude the motivating repo)

- **Decision**: The held-out set is **commit-pinned** and contains **≥2** repositories, and crucially **excludes `pallets/click`** — click motivated the existing demo feedback/proposals (`FB-2026-05-31-002`, `FB-2026-06-01-004` → `SP-2026-06-01-001`), so per FR-008 it cannot also validate them. The MVP seeds the set with two small, pinned, pure-library repos in distinct ecosystems (candidates: a small Python lib such as `benjaminp/six` at a tagged release, and a small JS lib such as `sindresorhus/is-odd`/`chalk`-style micro-lib at a tag). Final selection is an implementation task; the requirement is "≥2 pinned, non-click, ideally cross-ecosystem".
- **Rationale**: Disjointness is the whole point of held-out validation (no overfitting to the repo that prompted the edit). Cross-ecosystem repos make "no regression" a stronger signal than a single-language set.
- **Alternatives**: Reuse click as held-out (violates FR-008); a single held-out repo (weak signal, and brittle if it can't be scored). Rejected.

## R6 — Verdict computation (deterministic from the report tables)

- **Decision**: The verdict is computed by a fixed rule over the report's two tables: FAIL if any per-dimension `candidate < baseline` on any repo, OR any deterministic check flips pass→fail; else PASS (subject to the R1 effect/waiver clause). An **optional** `rubric/scripts/gate-verdict.sh` implements exactly this rule for convenience; it is not required for acceptance (the rule is fully specified in `rubric/validation-gate.md`).
- **Rationale**: A purely mechanical verdict over recorded scores delivers FR-011/SC-005 without depending on a tool.
- **Alternatives**: Tool-only verdict (adds a hard dependency to a skill-first project); reviewer eyeballing without a written rule (non-reproducible). Rejected.

## R7 — Artifact locations

- **Decision**: `rubric/validation-gate.md` (methodology), `rubric/held-out-set.md` (set definition), `rubric/gates/VG-*.md` (reports), `rubric/scoring/<repo>-<ver>-{baseline,candidate}.md` (sheets). Regenerated candidate specs for a held-out repo go under that repo's own `.reposkillopt/specs/`.
- **Rationale**: Keeps gate artifacts beside the rubric they extend; keeps regenerated per-repo output under the standard target-repo layout (FR-036a).
- **Alternatives**: Put everything in the feature spec dir (divorces it from the rubric it depends on). Rejected.

## R8 — Making the gate binding (canonical edit + adapter equivalence)

- **Decision**: Add one additive step to the **Skill Convergence Loop** in `skills/repo-skillopt/SKILL.md`: "an accepted proposal MUST reference a passing Validation Gate Report (see `rubric/validation-gate.md`)." Bump canonical `version` `0.1.0 → 0.2.0` (minor, additive), add a CHANGELOG `0.2.0` entry, and mirror the new sentence + `canonical_version: 0.2.0` across all four adapters. Add an optional `validation_gate_report:` field to `templates/skill-edit-proposal.md`.
- **Rationale**: FR-006 (no acceptance without a passing gate) is only normative if the canonical skill says so; adapters must mirror to preserve equivalence (FR-024/025/027a).
- **Alternatives**: Keep the gate advisory in `rubric/` only (non-binding — defeats the feature); a major bump (unwarranted — the change is additive, not breaking). Rejected.
- **Note**: This canonical edit is itself the kind of change the gate governs. For this feature it is applied directly (bootstrapping the mechanism); the worked report `VG-2026-06-01-001` demonstrates the gate on the *existing demo* proposal `SP-2026-06-01-001`, not on this bootstrapping edit, to avoid a circular dependency.

## Open questions

None blocking. The exact second/third held-out repositories are an implementation choice within the "≥2 pinned, non-click" requirement (R5).
