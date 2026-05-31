# Phase 0 Research — N-Scorers Majority Validation Gate

The four highest-impact decisions were resolved in `/speckit.clarify` (see `spec.md` → *Clarifications*). This document confirms those and records the remaining design decisions. Each: Decision / Rationale / Alternatives considered.

## R1 — No-majority aggregation = median + flag (confirmed)

- **Decision**: Per dimension, the aggregate is the **majority (modal)** score; when no strict majority exists, the **median**, and the dimension is flagged low-agreement. Method (`majority`/`median`) recorded per dimension.
- **Rationale**: Deterministic, reproducible, never loops. Median of an odd roster is well-defined.
- **Alternatives**: Conservative-min on the candidate side (stricter, can block noisy-but-fine edits); re-score-until-majority (can loop, costs more). Rejected in clarify.

## R2 — Roster = any independent mix (confirmed)

- **Decision**: Scorers may be all-agent, all-human, or mixed. The hard requirement is **independence**: each scores **blind**, with no access to other scorers' scores before submitting. The report attests independence and lists the roster (role, human/agent).
- **Rationale**: Keeps the loop agent-runnable and low-cost while preserving the property that makes majority meaningful (independent votes).
- **Independence for agent scorers**: distinct scoring sessions with **no shared transcript**; vary the scoring framing per scorer (e.g., different ordering/emphasis prompt) to reduce model-correlated errors. A human scorer is encouraged for high-stakes edits to add diversity but is not mandated.
- **Alternatives**: Require ≥1 human (more robust, costs human time every gate); require human majority (heaviest). Available as opt-in stricter rosters, not the default.

## R3 — Contested potential-regression → adjudicate before PASS; else HELD (confirmed)

- **Decision**: A dimension that is **low-agreement (range ≥2)** AND whose aggregate is **at or below baseline** is a possible masked regression: it MUST be **adjudicated** (re-scored to resolution, recorded) before the gate may PASS. An unresolved such dimension yields verdict **`HELD`**. Low agreement on a dimension comfortably above baseline is recorded but non-blocking.
- **Rationale**: Targets the blocking precisely where disagreement could hide a regression, without over-blocking well-above-baseline dimensions. Adds the third verdict `HELD` (alongside `PASS`/`FAIL` from feature 003).
- **Alternatives**: Majority value always final (can pass a contested dimension); any low-agreement blocks (over-blocking). Rejected in clarify.

## R4 — Roster size N = 3, scaling by stakes (confirmed)

- **Decision**: Default **N = 3** (odd). Scale to 5 or 7 for higher-stakes edits per the mode-selection rule. Requirement: odd and ≥3.
- **Rationale**: 3 is the smallest roster that lets a majority outvote a single outlier; scaling concentrates cost where stakes are highest.
- **Alternatives**: Fixed 3 (no scaling); caller-picks (no guidance). Rejected.

## R5 — Verdict computation (deterministic, incl. HELD)

- **Decision**: For each held-out repo and dimension: aggregate per R1; compare aggregate to the aggregated baseline; a deterministic-check aggregates by majority pass/fail.
  ```
  verdict = FAIL  if any dimension aggregate < baseline on any repo
                  OR any deterministic check aggregates to fail
  verdict = HELD  if (no FAIL) AND some dimension is low-agreement AND at-or-below baseline AND not adjudicated
  verdict = PASS  otherwise (no regression; contested-at-or-below dims all adjudicated; effect realized/waived)
  ```
  Reproducible from the recorded per-scorer matrix + these rules.
- **Rationale**: Encodes R1–R3 as one mechanical rule over the matrix.
- **Alternatives**: Fold HELD into FAIL (loses the "needs adjudication, not rejected" distinction). Rejected.

## R6 — No canonical-skill change

- **Decision**: Majority mode is documented entirely in `rubric/validation-gate.md` (a new "## Majority mode" section) + the report schema. The canonical Skill Convergence Loop step 6 already says a proposal must "pass a validation gate"; *how* it is scored (single vs majority) is methodology, not normative canonical content. So **no `SKILL.md` or adapter edit and no version bump** (canonical stays `0.2.0`).
- **Rationale**: Keeps the feature low-surface and avoids the 4-adapter equivalence cost of feature 003 for a change that does not alter what the gate *requires*, only how scoring is performed.
- **Alternatives**: Add a canonical sentence naming majority mode (unnecessary normativity; triggers adapter equivalence + bump). Rejected.

## R7 — Optional aggregation helper

- **Decision**: A new optional `rubric/scripts/majority-aggregate.sh` reads a report's per-scorer matrix and computes, per dimension, the majority/median, the agreement (range), and the contributory verdict signal (FAIL / HELD-candidate / OK), then prints the overall `PASS`/`FAIL`/`HELD`. POSIX-sh, with a test. Feature 003's `gate-verdict.sh` is left unchanged (it handles single-scorer reports).
- **Rationale**: Gives a runnable, testable anchor for SC-006 reproducibility without making the tool mandatory.
- **Alternatives**: Extend `gate-verdict.sh` to auto-detect mode (more coupling); no helper (loses the executable anchor). Rejected — a separate helper is cleaner.

## R8 — Worked-example data

- **Decision**: Reuse feature 003's held-out members (`benjaminp/six@1.16.0`, `sindresorhus/escape-string-regexp@v5.0.0`). Produce: an N-scorer baseline matrix, a `mode: majority` PASS report whose `six` *Test strategy quality* dimension is contested-but-above-baseline (flagged, non-blocking), and a HELD report where a dimension is contested at-or-below baseline and left unadjudicated. Scores are **illustrative worked examples** (consistent with feature 003 — regenerating/scoring real repos is out of environment scope); the schema, aggregation, and verdict rule are the real deliverable.
- **Rationale**: Demonstrates majority, low-agreement-non-blocking, and the new HELD path end-to-end on familiar data.
- **Alternatives**: New held-out repos (unnecessary; reuse is cleaner and keeps disjointness already-audited). Rejected.

## Open questions

None blocking.
