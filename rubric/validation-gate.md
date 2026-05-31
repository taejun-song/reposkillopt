# Validation Gate — Skill Convergence

**Scope**: The procedure and acceptance criterion that gate a `scope: generic` Skill Edit Proposal before it may be accepted into the canonical skill (feature `003-validation-gating`).
**Companions**: `rubric/held-out-set.md` (the held-out reference set), `rubric/evaluation-rubric.md` (15 dimensions), `rubric/deterministic-checks.md` (7 checks), `rubric/gates/` (the reports).

The gate is **methodology over the existing rubric** — no service, database, training loop, or model fine-tuning. It is human-run; a named scorer-of-record records the scores and the verdict is a deterministic function of those scores.

## When the gate applies

- Only to `scope: generic` Skill Edit Proposals. `scope: repository-scoped` proposals are rejected upstream by the existing scope discipline and never reach the gate.
- A proposal may move to `status: accepted` **only** when it references a **passing** Validation Gate Report (this rule is normative in the canonical *Skill Convergence Loop*).

## Procedure

1. **Confirm eligibility** — the proposal is `scope: generic`.
2. **Confirm disjointness** — none of the proposal's `supporting_feedback` repositories appear in the held-out set (`rubric/held-out-set.md`). If one does, record `verdict: HELD` and stop (fixing the set or the proposal first).
3. **Ensure baselines** — a baseline scoring sheet exists for each held-out member at the **current released** skill version. If the released version changed since the last baseline, recompute baselines first (see *Re-baseline*).
4. **Build the candidate version** — apply the proposal's diff to a working copy of `skills/repo-skillopt/SKILL.md` (unreleased).
5. **Regenerate** — for each held-out member, run the candidate skill to produce a fresh Repository Specification under that repository's `.reposkillopt/specs/`. Score the regenerated output, not any pre-existing text.
6. **Score** — the scorer-of-record applies the 15 rubric dimensions and the 7 deterministic checks to each regenerated spec, recording candidate scores beside the baselines.
7. **Decide** — apply the verdict rule below; write a Validation Gate Report (`rubric/gates/VG-…md`).
8. **Route** — `PASS` → the proposal becomes eligible for `status: accepted`, after which the **normal version-bump flow** runs (apply the diff, bump the canonical version per semver, add a CHANGELOG entry, mirror to adapters). `FAIL`/`HELD` → the proposal is rejected/held and the report is **preserved**.

## Acceptance criterion

A proposal **PASSES** the gate if and only if **all** of:

- **No per-dimension regression** — on every held-out member, every dimension's candidate score is **≥** its baseline score.
- **No deterministic-check regression** — on every held-out member, no check flips `pass → fail`.
- **Effect realized (or waived)** — the proposal's stated `expected_effect` is realized on **≥1** dimension, **or** the proposal is a clarifying edit that explicitly waives improvement (recorded in the report).

Per-dimension comparison only. An **aggregate** (sum or mean) MUST NOT decide the verdict — a version can hold a constant aggregate while regressing on a dimension that matters (consistent with the rubric's per-dimension rule).

## Verdict rule (deterministic — reproducible from the recorded scores)

```
verdict = HELD   if a held-out member is in the proposal's supporting_feedback repos
verdict = FAIL   if any dimension candidate < baseline on any member
              OR any deterministic check flips pass -> fail on any member
              OR expected effect is neither realized nor waived
verdict = PASS   otherwise
```

The verdict depends only on the scores recorded by the scorer-of-record, so **anyone re-evaluating the recorded tables reaches the same verdict** (reproducibility). The optional helper `rubric/scripts/gate-verdict.sh` implements exactly this rule; it is a convenience, not a requirement — the rule above is normative.

## Scorer-of-record

Each gate run names one **scorer-of-record** (a human reviewer, who may be assisted by an agent) who produces and records the scores. Regeneration and rubric scoring are judgment steps and may vary run to run; the **recorded scores are the authoritative, reproducible input** to the verdict. A dispute is resolved by the scorer-of-record re-scoring and re-recording — never by averaging into an aggregate.

## Re-baseline

Baselines describe the **current released** skill version. Recompute (and relabel) them whenever the released canonical version changes — i.e., right after any accepted proposal bumps the version. The held-out set records the `released_version` its baselines describe.

> **Bootstrapping note (feature 003).** The canonical edit that *introduces* this gate (adding the rule to the Skill Convergence Loop and bumping `0.1.0 → 0.2.0`) is itself **not** gated — it establishes the mechanism. The gate binds **subsequent** `scope: generic` proposals. The worked example (`rubric/gates/VG-2026-06-01-001-*`) gates the pre-existing demo proposal `SP-2026-06-01-001`, not this bootstrapping edit, to avoid circularity. The held-out baselines used by that worked example are pinned at `0.1.0` (the version under which the demo proposal was authored); re-baselining the held-out set to `0.2.0` is **deferred** to the next real gate run and recorded as such in `rubric/held-out-set.md`.

## Comparing versions

To compare two candidate versions, score each against the **same** held-out set and diff the per-dimension rows of their reports. Because each report records per-dimension baseline-vs-candidate scores, a reader obtains per-dimension deltas across versions directly from the reports — no baseline re-derivation needed. A regression on any single dimension is visible even when an advisory aggregate is unchanged. This extends the project's version-comparison capability (feature 001 SC-012) from a single sheet to a versioned series of gate reports.
