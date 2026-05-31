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

## Scoring modes

The gate may be scored in one of two modes; every gate report records which one it used.

| Mode | Scorers | Use |
|---|---|---|
| `single` | One scorer-of-record (the default above) | Low-risk edits. |
| `majority` | N independent scorers, odd and ≥3 (below) | Required for high-stakes edits. |

**Majority mode is REQUIRED when any of these holds:**

1. the proposal edits the canonical **Operating Principles** section, **or**
2. the proposal **previously failed** a validation gate (any earlier `FAIL`/`HELD`), **or**
3. the single scorer-of-record records **low confidence** on any decisive dimension.

Otherwise a low-risk clarifying edit MAY use `single` mode. The required-when list is a **minimum** — a maintainer may always choose `majority` for extra assurance.

Majority mode changes only **how scoring is performed** (one scorer → N + aggregation); it does **not** change what the gate *requires*. It is therefore methodology only: it needs **no edit to the canonical skill or adapters** and no version bump.

## Majority mode (N scorers)

In majority mode, **N independent scorers** (N odd, ≥3; default 3, scaling to 5/7 for the highest-stakes edits) each apply the rubric to every regenerated held-out specification, and the per-dimension scores are combined by majority.

### Roster and independence

- The roster is **odd and ≥3**. Scorers may be human, agent, or a mix.
- Each scorer scores **blind** — without access to any other scorer's scores before submitting. Agent scorers count as independent only when run in **separate sessions with no shared transcript** (varying the scoring framing reduces model-correlated error). A human scorer is encouraged for high-stakes edits but not mandated.
- The report records the roster (each scorer's role and `human`/`agent`) and an **independence attestation**.

### Independence breaches

If a scorer scored after seeing another's scores, their row is **excluded** (if the roster stays odd and ≥3) or **redone blind**. A verdict MUST NOT rest on a non-independent row.

### Aggregation

For each dimension, the **aggregate** is the **majority (modal)** score across scorers. If no strict majority exists, it is the **median**, and the dimension is flagged **low-agreement**. A dimension is low-agreement when the scorers span a **range ≥ 2**. Deterministic checks aggregate by **majority pass/fail** per check.

> Cross-scorer aggregation combines scores **within a single dimension**. It is *not* the cross-dimension aggregate (sum/mean across the 15 dimensions) that must never replace per-dimension comparison — that rule still holds.

### Adjudication and the HELD verdict

A low-agreement dimension whose aggregate is **above** baseline is recorded but does **not** block. A low-agreement dimension whose aggregate is **at or below** baseline is a possible masked regression and MUST be **adjudicated** — re-scored to resolution, with the resolved value and adjudicator recorded — before the gate may PASS. Adjudication updates that dimension's aggregated row to the resolved value. An unresolved such dimension yields verdict **`HELD`** (not PASS, not FAIL).

### Majority verdict rule (deterministic, reproducible from the matrix)

```
FAIL  if any dimension aggregate < baseline on any held-out repo,
      OR any deterministic check aggregates (majority) to fail.
HELD  if not FAIL, AND some dimension is low-agreement AND at or below baseline AND not adjudicated.
PASS  otherwise (no regression; every contested at-or-below dimension adjudicated; expected effect realized or waived).
```

The verdict depends only on the recorded per-scorer matrix and these rules, so anyone re-aggregating reaches the same `PASS`/`FAIL`/`HELD`. The optional helper `rubric/scripts/majority-aggregate.sh` implements exactly this rule over a report's aggregated tables; it is a convenience, not a requirement. Report schema: `specs/004-majority-scoring/contracts/majority-gate-report.contract.md`.
